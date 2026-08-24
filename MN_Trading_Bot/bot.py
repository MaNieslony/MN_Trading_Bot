# bot.py
"""
MN Options Trading Bot
═══════════════════════

Config-driven options trading bot using Interactive Brokers (ib_insync).

Features:
- Multiple strategies via schedules.json
- Multiple trade types via trade_templates.json (e.g. Bull Put, Butterfly)
- Configurable entry conditions (RSI, Intraday Move, SMA, etc.)
- Configurable execution times and position sizing
- Paper and Live trading support
- Headless CLI execution with graceful shutdown

USAGE:
  python mn_trading_bot.py --schedule SPX-FFBPS
  python mn_trading_bot.py --schedule SPX-10BPS --debug

CONFIGURATION FILES:
  config/schedules.json              # When & under which conditions to trade
  config/trade_templates.json        # What to trade (legs, deltas, structure)
  config/broker_settings.json        # IB Gateway/TWS connection settings
  config/bot_mode_settings.json      # DEBUG, market hours flags
  config/telegram_settings.json      # Telegram notification credentials

OUTPUT:
  logs/mn_trading_bot_YYYYMMDD.log
  reports/mn_trading_trade_report.csv
"""
from bot_logging import print_startup_banner, _setup_logging as bot_setup_logging
from config.loader import load_broker_settings, load_telegram_settings,load_bot_mode_settings,load_merged_schedules
from broker.ib_broker import IBBroker
from broker.ib_errors import build_error_callback
from market.market_flow import wait_for_ticker_data
from market.market_data import ensure_live_data_if_market_open
from market.contracts import get_index_contract
from market.adapters import init_market_caches,preload_option_chain_adapter,preload_deltas_adapter,build_strikes_for_delta_adapter,get_current_price_adapter,get_open_price_adapter,get_option_conid_adapter,get_option_deltas_adapter,get_option_chain_adapter,get_rsi_adapter,get_sma_adapter,get_vix_adapter,get_iv_rank_adapter
from conditions.entry_conditions import check_entry_conditions
from runtime.sleep import interruptible_sleep
from runtime.validation import validate_startup
from runtime.shutdown import shutdown
from runtime.context.schedule_context import ScheduleContext
from runtime.context.market_context import is_market_open_now,wait_for_execution_time_now
from runtime.context.trading_day_context import should_trade_today_now
from runtime.context.market_wait_context import wait_for_market_open_now
from tradetype.bull_put import BullPutTradeType
from tradetype.pbw import PutBrokenWingTradeType
from tradetype.rut_iron_condor import RutIronCondorTradeType
from trade.trading_cycle import run_trading_cycle
from trade.execution import execute_credit_sweep
from trade.combo_factory import create_combo_contract
from trade.trade_logger import log_trade
from trade.position_sizing import calculate_quantity_from_buying_power
from trade.telegram import send_telegram_notification

from ib_insync import IB, util
from datetime import datetime, time as dt_time, timedelta
from typing import Optional, Tuple, List, Dict
import pytz
import sys
import signal
import argparse

class Bot:
    """Bot Class"""
    def __init__(self, selected_schedule: str = None):
        self.running = True
        self.trade_in_progress = False
        self.selected_schedule = selected_schedule
        self._shutting_down = False

        # ------------------------------------------------------------
        # Setup logging
        # ------------------------------------------------------------
        self._setup_logging()
        # ------------------------------------------------------------
        # Load bot mode settings
        # ------------------------------------------------------------
        settings = load_bot_mode_settings()

        self.DEBUG_MODE = settings["DEBUG_MODE"]
        self.CHECK_CONDITIONS = settings["CHECK_CONDITIONS"]
        self.CHECK_EXECUTION_TIME = settings["CHECK_EXECUTION_TIME"]
        self.CHECK_MARKET_OPEN = settings["CHECK_MARKET_OPEN"]
        self.TRADE_REPORT_CSV = settings.get("TRADE_REPORT_CSV","reports/mn_trading_trade_report.csv")

        # ------------------------------------------------------------
        # Load schedules + select by name + apply config to flat attributes + create TradeType instance
        # ------------------------------------------------------------
        schedules = load_merged_schedules()
        if not schedules:
            raise RuntimeError("❌ No schedules loaded from schedules.json")

        if not self.selected_schedule:
            available = ", ".join(sorted(s.get("NAME", "<no-name>") for s in schedules))
            raise ValueError(f"❌ --schedule missing. Available: {available}")

        trade_cfg = next(
            (s for s in schedules if s.get("NAME") == self.selected_schedule),
            None
        )

        if not trade_cfg:
            available = ", ".join(sorted(s.get("NAME", "<no-name>") for s in schedules))
            raise ValueError(
                f"❌ Schedule '{self.selected_schedule}' not found. Available: {available}"
            )

        self.schedules = schedules

        ScheduleContext(trade_cfg).apply(self)

        # ------------------------------------------------------------
        # TradeType (instrument logic)
        # ------------------------------------------------------------
        self.trade_type = self._create_trade_type(self.TRADE_TYPE)
        self.logger.info(f"✅ TradeType: {self.TRADE_TYPE}")

        # ------------------------------------------------------------
        # Load broker settings
        # ------------------------------------------------------------
        broker_cfg = load_broker_settings()

        self.IB_HOST = broker_cfg["IB_HOST"]
        self.IB_CLIENT_ID = broker_cfg["CLIENT_ID"]

        if broker_cfg["USE_PAPER_TRADING"]:
            self.IB_PORT = broker_cfg["IB_PORT_PAPER"]
        else:
            self.IB_PORT = broker_cfg["IB_PORT_LIVE"]

        self._is_paper_trading = (self.IB_PORT == 7497)

        # ------------------------------------------------------------
        # Load Telegram settings
        # ------------------------------------------------------------
        telegram = load_telegram_settings()
        self.TELEGRAM_ENABLED = telegram["TELEGRAM_ENABLED"]
        self.TELEGRAM_CHAT_ID = telegram["TELEGRAM_CHAT_ID"]
        self.TELEGRAM_BOT_TOKEN = telegram["TELEGRAM_BOT_TOKEN"]

        # ------------------------------------------------------------
        # Static / runtime-only values
        # ------------------------------------------------------------
        self.MARKET_OPEN_TIME = dt_time(9, 30)
        self.MARKET_CLOSE_TIME = dt_time(16, 0)

        self.underlying_price = 0.0
        self.open_price = 0.0
        self.last_trade_date = None

        # ------------------------------------------------------------
        # IB Connection
        # ------------------------------------------------------------
        self.ib = IB()

        # Initialize market-related caches (option chains, deltas, etc.)
        init_market_caches(self)

        # Broker abstraction layer (handles connection, reconnection, health checks, etc.)
        self.broker = IBBroker(
            ib=self.ib,
            logger=self.logger,
            host=self.IB_HOST,
            port=self.IB_PORT,
            client_id=self.IB_CLIENT_ID,
            is_market_open_callable=self.is_market_open,
            setup_error_callback_callable=self._setup_error_callback,
        )

        self.broker.bot = self

        # Silence ib_insync connection noise
        _orig_error = self.ib.wrapper.error

        def _patched_error(reqId, errorCode, errorString, contract=""):
            if errorCode not in (1100, 1102, 1300, 2104, 2106, 2158):
                _orig_error(reqId, errorCode, errorString, contract)

        self.ib.wrapper.error = _patched_error

# ============================================================================
# BROKER
# ============================================================================
    def connect(self) -> bool:
        return self.broker.connect()

    def disconnect(self):
        return self.broker.disconnect()

    def reconnect(self, max_retries: int = 3) -> bool:
        return self.broker.reconnect(max_retries=max_retries)

    def check_connection_health(self) -> bool:
        return self.broker.check_connection_health()

# ============================================================================
# IB ERRORS
# ============================================================================
    def _setup_error_callback(self):
        self.ib.errorEvent += build_error_callback(self.logger)
# ============================================================================
# RUNTIME
# ============================================================================
    def validate_startup(self) -> bool:
        return validate_startup(ib_host=self.IB_HOST,ib_port=self.IB_PORT,allocation=self.ALLOCATION,execution_time=self.EXECUTION_TIME,market_open_time=self.MARKET_OPEN_TIME,market_close_time=self.MARKET_CLOSE_TIME,logger=self.logger)

    def interruptible_sleep(self, seconds: float) -> bool:
        return interruptible_sleep(seconds=seconds,is_running_callable=lambda: self.running,ib=self.ib,broker=self.broker,logger=self.logger)

    def shutdown(self):
        shutdown(bot=self,broker=self.broker,logger=self.logger)
            
    def ensure_live_data_if_market_open(self):
        ensure_live_data_if_market_open(ib=self.ib,is_market_open_callable=self.is_market_open,is_paper_trading=self._is_paper_trading)
    
    def wait_for_ticker_data(self, tickers, timeout=0.5, wait_for_greeks=False):
        return wait_for_ticker_data(tickers=tickers,timeout=timeout,wait_for_greeks=wait_for_greeks)

# ============================================================================
# MARKET (delegated to market.adapters)
# ============================================================================
    def preload_option_chain(self, expiry: str):
        return preload_option_chain_adapter(self, expiry)

    def preload_deltas(self, expiry: str, trading_class: str, strikes_for_delta: List[float]):
        return preload_deltas_adapter(self, expiry, trading_class, strikes_for_delta)

    def _build_strikes_for_delta(self, strikes: List[float]) -> List[float]:
        return build_strikes_for_delta_adapter(self, strikes)

    def get_current_price(self) -> Optional[float]:
        return get_current_price_adapter(self)

    def get_open_price(self) -> Optional[float]:
        return get_open_price_adapter(self)

    def _get_option_conid(self, expiry: str, strike: float, right: str, trading_class: str = None):
        return get_option_conid_adapter(self, expiry, strike, right, trading_class)

    def get_option_deltas(self, expiry: str, strikes: List[float], put_call: str, trading_class: str) -> Dict[float, float]:
        return get_option_deltas_adapter(self, expiry=expiry, strikes=strikes, put_call=put_call, trading_class=trading_class)

    def get_option_chain(self, expiry: str) -> Tuple[Optional[str], List[float]]:
        return get_option_chain_adapter(self, expiry)

    def get_rsi(self, period: int = 14, bar_size: str = "1 day") -> Optional[float]:
        return get_rsi_adapter(self, period=period, bar_size=bar_size)

    def get_sma(self, period: int, bar_size: str = "1 day") -> Optional[float]:
        return get_sma_adapter(self, period=period, bar_size=bar_size)

    def get_vix(self) -> Optional[float]:
        return get_vix_adapter(self)

    def get_iv_rank(self) -> Optional[float]:
        return get_iv_rank_adapter(self)

    def is_market_open(self) -> bool:
        return is_market_open_now(market_open_time=self.MARKET_OPEN_TIME,market_close_time=self.MARKET_CLOSE_TIME,check_market_open=self.CHECK_MARKET_OPEN,logger=self.logger)

    def wait_for_EXECUTION_TIME(self) -> bool:
        return wait_for_execution_time_now(execution_time=self.EXECUTION_TIME,check_execution_time=self.CHECK_EXECUTION_TIME,interruptible_sleep=self.interruptible_sleep,logger=self.logger)

    def should_trade_today(self) -> bool:
        return should_trade_today_now(last_trade_date=self.last_trade_date,schedule_name=self.STRATEGY_NAME,logger=self.logger,trade_report_csv=self.TRADE_REPORT_CSV)

# ============================================================================
# TRADE TYPE FACTORY
# ============================================================================
    def _create_trade_type(self, trade_type: str):
        """
        Factory for trade types (config-driven).
        Extend here when adding new trade types (e.g. BUTTERFLY).
        """
        tt = (trade_type or "").strip().upper()

        if tt in ("BULL_PUT", "PUT_SPREAD", "BPS"):
            return BullPutTradeType(
                leg1_target=self.LEG1_TARGET,
                leg1_target_type=self.LEG1_TARGET_TYPE,
                leg2_target=self.LEG2_TARGET,
                leg2_target_type=self.LEG2_TARGET_TYPE,
                logger=self.logger,
            )

        if tt in ("PUT_BROKEN_WING", "PBW"):
            return PutBrokenWingTradeType(
                leg1_target=self.LEG1_TARGET,
                leg1_target_type=self.LEG1_TARGET_TYPE,
                leg2_target=self.LEG2_TARGET,
                leg2_target_type=self.LEG2_TARGET_TYPE,
                leg3_target=self.LEG3_TARGET,
                leg3_target_type=self.LEG3_TARGET_TYPE,
                logger=self.logger,
            )

        if tt in ("IRON_CONDOR", "RUT_IRON_CONDOR"):
            return RutIronCondorTradeType(logger=self.logger)

        raise ValueError(f"❌ Unknown TRADE_TYPE '{trade_type}' in template/schedule '{self.STRATEGY_NAME}'")

# ============================================================================
# POSITION SIZING
# ============================================================================
    def calculate_quantity_from_buying_power(
        self,
        mid_credit: float,
        natural_credit: float
    ) -> int:

        if self.QUANTITY_MODE == "FixedQty":
            return self.FIXED_QTY

        # PremAllocation (bestehende Logik)
        return calculate_quantity_from_buying_power(allocation=self.ALLOCATION,min_qty=self.MIN_QTY,max_qty=self.MAX_QTY,mid_credit=mid_credit,natural_credit=natural_credit,is_paper_trading=self._is_paper_trading,logger=self.logger)
# ====================================================================
# QUANTITY HELPERS
# ====================================================================
    def get_effective_quantity(self) -> int:
        """
        Quantity used for logging / pre-execution display.
        (Actual execution quantity is still determined in the sweep.)
        """
        if self.QUANTITY_MODE == "FixedQty":
            return self.FIXED_QTY
        return self.MIN_QTY
# ============================================================================
# TRADE
# ============================================================================
    def execute_credit_sweep(self, combo, found_credit: Optional[float] = None, natural_credit: Optional[float] = None):

        return execute_credit_sweep(
            ib=self.ib,
            logger=self.logger,
            combo=combo,
            found_credit=found_credit,
            natural_credit=natural_credit,
            calculate_quantity_callable=self.calculate_quantity_from_buying_power,
            log_trade_callable=self._log_trade,
            interruptible_sleep_callable=self.interruptible_sleep,
            min_qty=self.MIN_QTY,
            max_qty=self.MAX_QTY,
            max_sweep_price=self.MAX_SWEEP_PRICE,
            sweep_step=self.SWEEP_STEP,
            sweep_wait_seconds=self.SWEEP_WAIT_SECONDS,
            max_sweep_attempts=self.MAX_SWEEP_ATTEMPTS,
            expiration_minutes=self.EXPIRATION_MINUTES,
            order_ref=self.STRATEGY_NAME,
            profit_target_enabled=self.PROFIT_TARGET_ENABLED,
            profit_target_pct=self.PROFIT_TARGET_PCT,
            profit_target_eth=self.PROFIT_TARGET_ETH,
            start_sweep_quantile=self.START_SWEEP_QUANTILE,
        )

    def create_combo_contract(self,expiry: str,leg1: float,leg2: float,trading_class: str,):
        return create_combo_contract(
            symbol=self.SYMBOL,
            expiry=expiry,
            leg1=leg1,
            leg2=leg2,
            trading_class=trading_class,
            leg1_put_call=self.LEG1_PUT_CALL,
            leg2_put_call=self.LEG2_PUT_CALL,
            leg1_action=self.LEG1_ACTION,
            leg2_action=self.LEG2_ACTION,
            leg1_qty=self.LEG1_QTY,
            leg2_qty=self.LEG2_QTY,
            min_sweep_price=self.MIN_SWEEP_PRICE,
            max_sweep_price=self.MAX_SWEEP_PRICE,
            get_option_conid_callable=self._get_option_conid,
            logger=self.logger,
        )

# ============================================================================
# REPORTING
# ============================================================================
    def _log_trade(self, trade, premium_paid: float, quantity: int = None, profit_target=None):

        trade_type_label = getattr(self.trade_type, "display_name", self.TRADE_TYPE)

        log_trade(
            trade=trade,
            premium_paid=premium_paid,
            quantity=quantity,
            symbol=self.SYMBOL,
            strategy_name=self.STRATEGY_NAME,
            trade_type=self.TRADE_TYPE,
            trade_type_label=trade_type_label,
            leg1_qty=self.LEG1_QTY,
            leg2_qty=self.LEG2_QTY,
            leg3_qty=self.LEG3_QTY,
            leg4_qty=self.LEG4_QTY,
            commission_per_contract=self.COMMISSION_PER_CONTRACT,
            is_paper_trading=self._is_paper_trading,
            telegram_enabled=self.TELEGRAM_ENABLED,
            telegram_chat_id=self.TELEGRAM_CHAT_ID,
            send_telegram_callable=self.send_telegram_notification,
            ib=self.ib,
            logger=self.logger,
            csv_file=self.TRADE_REPORT_CSV,
            profit_target=profit_target,
        )

    def check_entry_conditions(self) -> bool:
        return check_entry_conditions(
            check_conditions=self.CHECK_CONDITIONS,
            symbol=self.SYMBOL,
            entry_conditions=self.trade_cfg.get("ENTRY_CONDITIONS", {}),
            get_rsi_callable=self.get_rsi,
            get_sma_callable=self.get_sma,
            get_vix_callable=self.get_vix,
            get_iv_rank_callable=self.get_iv_rank,
            underlying_price=self.underlying_price,
            open_price=self.open_price,
            logger=self.logger,
        )

# ============================================================================
# NOTIFICATIONS
# ============================================================================
    def send_telegram_notification(self, message: str):
        send_telegram_notification(enabled=self.TELEGRAM_ENABLED,chat_id=self.TELEGRAM_CHAT_ID,bot_token=self.TELEGRAM_BOT_TOKEN,message=message,logger=self.logger)
# ============================================================================
# OTHER
# ============================================================================
    def _setup_logging(self):
        bot_setup_logging(self)

    def is_paper_trading(self) -> bool:
        """Check if currently connected to paper trading account."""
        return self._is_paper_trading if self._is_paper_trading is not None else False    

    def get_SPX_index_contract(self):
        """
        Backward-compatible wrapper.
        Internally uses symbol-agnostic index metadata.
        """
        return get_index_contract(self.SYMBOL)

    def wait_for_market_open(self):
        return wait_for_market_open_now(check_market_open=self.CHECK_MARKET_OPEN,market_open_time=self.MARKET_OPEN_TIME,market_close_time=self.MARKET_CLOSE_TIME,interruptible_sleep=self.interruptible_sleep,broker=self.broker,logger=self.logger)
# ============================================================================
# DEF RUN 
# ============================================================================
    def run(self):
        """
        Main run loop

        Shutdown model:
        - Ctrl+C / SIGTERM sets self.running = False
        - run() exits cooperatively and then calls shutdown() exactly once
        """

        self.logger.debug("=" * 80)
        self.logger.debug("🎯 Bot started")
        self.logger.debug("=" * 80)

        if not self.validate_startup():
            self.logger.error("❌ Startup validation failed - bot cannot start")
            return

        connection_failures = 0
        max_connection_failures = 3
        retry_interval_seconds = 60

        try:
            # --------------------------------------------------------
            # CONNECT LOOP
            # --------------------------------------------------------
            while self.running and not getattr(self, "_shutting_down", False):

                if not self.broker.connect():
                    connection_failures += 1
                    self.logger.error(
                        f"IB connection failed ({connection_failures}/{max_connection_failures})"
                    )

                    if connection_failures >= max_connection_failures:
                        self.logger.error(
                            f"❌ Max connection failures reached ({max_connection_failures})"
                        )
                        if not self.interruptible_sleep(300):
                            break
                        connection_failures = 0
                    else:
                        if not self.interruptible_sleep(60):
                            break

                    continue

                connection_failures = 0

                if self.CHECK_MARKET_OPEN and self.running:
                    self.wait_for_market_open()

                # ----------------------------------------------------
                # DAILY / RETRY LOOP
                # ----------------------------------------------------
                while self.running and not getattr(self, "_shutting_down", False):
                    try:
                        self.trade_in_progress = True
                        try:
                            run_trading_cycle(self)
                        finally:
                            self.trade_in_progress = False

                        if not self.running:
                            break

                        # ------------------------------------------------
                        # Sleep / scheduling
                        # ------------------------------------------------
                        if self.CHECK_MARKET_OPEN:
                            et_tz = pytz.timezone("US/Eastern")
                            now_et = datetime.now(et_tz)

                            next_open = now_et.replace(
                                hour=self.MARKET_OPEN_TIME.hour,
                                minute=self.MARKET_OPEN_TIME.minute,
                                second=0,
                                microsecond=0
                            ) + timedelta(days=1)

                            while next_open.weekday() >= 5:
                                next_open += timedelta(days=1)

                            sleep_seconds = (next_open - now_et).total_seconds()

                            self.logger.info(
                                f"🛌 Sleeping until next market open "
                                f"({next_open.strftime('%Y-%m-%d %H:%M')} ET)"
                            )

                            elapsed = 0
                            check_interval = 300  # 5 minutes

                            while (
                                elapsed < sleep_seconds
                                and self.running
                                and not getattr(self, "_shutting_down", False)
                            ):
                                sleep_time = min(check_interval, sleep_seconds - elapsed)

                                if not self.interruptible_sleep(sleep_time):
                                    break

                                elapsed += sleep_time

                                if (
                                    self.running
                                    and not getattr(self, "_shutting_down", False)
                                    and not self.broker.check_connection_health()
                                ):
                                    self.logger.error(
                                        "Connection health check failed - attempting reconnect"
                                    )
                                    if (
                                        self.running
                                        and not getattr(self, "_shutting_down", False)
                                        and not self.broker.reconnect()
                                    ):
                                        self.logger.error(
                                            "Reconnection failed - breaking daily loop"
                                        )
                                        break

                            if not self.running:
                                break

                        else:
                            self.logger.info("Market-open scheduling disabled – continuing loop")

                            if not self.interruptible_sleep(retry_interval_seconds):
                                break

                            if (
                                self.running
                                and not getattr(self, "_shutting_down", False)
                                and not self.broker.check_connection_health()
                            ):
                                self.logger.error("Connection health check failed - attempting reconnect")

                                if (
                                    self.running
                                    and not getattr(self, "_shutting_down", False)
                                    and not self.broker.reconnect()
                                ):
                                    self.logger.error("Reconnection failed - breaking daily loop")
                                    break

                    except Exception as e:
                        if not self.running or getattr(self, "_shutting_down", False):
                            break

                        self.logger.error(
                            f"Error in trading cycle: {e}", exc_info=True
                        )
                        self.logger.info("Waiting 5 minutes before retry...")

                        if not self.interruptible_sleep(300):
                            break

                # end DAILY / RETRY LOOP
                if self.broker.check_connection_health():
                    self.broker.disconnect()

        except Exception as e:
            self.logger.critical(
                f"Critical error in main run loop: {e}",
                exc_info=True
            )

        finally:
            self.shutdown()
# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
if __name__ == '__main__':

    bot = None

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--schedule",
        required=True,
        help="Name des Schedules aus schedules.json (z.B. SPX-MORNING)"
    )
    args = parser.parse_args()

    def signal_handler(_sig, _frame):
        print("\nShutdown signal received...")
        if bot is not None:
            bot.running = False

    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, signal_handler)

    print_startup_banner()

    try:
        util.patchAsyncio()
        bot = Bot(selected_schedule=args.schedule)
        bot.run()
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Fatal bot error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)