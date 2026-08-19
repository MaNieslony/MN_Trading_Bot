# trade/trade_logger.py

import os
import csv
import pytz
from datetime import datetime

from trade.metrics import TradeMetrics

def log_trade(
    *,
    trade,
    premium_paid: float,
    quantity: int,
    symbol: str,
    strategy_name: str,
    trade_type: str,
    trade_type_label: str,
    leg1_qty: int,
    leg2_qty: int,
    leg3_qty: int,
    leg4_qty: int,
    commission_per_contract: float,
    is_paper_trading: bool,
    telegram_enabled: bool,
    telegram_chat_id: str,
    send_telegram_callable,
    ib,
    logger,
    csv_file: str,
    profit_target: dict | None = None,
):
    """

    """

    trade_type_label = trade_type_label or trade_type

    try:
        combo = trade.contract

        is_pbw = trade_type.upper() in ("PUT_BROKEN_WING", "PBW")
        is_ic = trade_type.upper() in ("IRON_CONDOR", "RUT_IRON_CONDOR")

        # ------------------------------------------------------------
        # Optional selection metrics (robust formatting for CSV)
        # ------------------------------------------------------------
        metrics = getattr(combo, "metrics", None) or TradeMetrics()

        short_mid_val = metrics.short_leg_mid
        short_mid_str = f"{short_mid_val:.2f}" if isinstance(short_mid_val, (int, float)) else ""

        delta_val = metrics.short_delta
        delta_str = f"{delta_val:.4f}" if isinstance(delta_val, (int, float)) else ""

        ic_call_mid_val = getattr(metrics, "ic_short_call_mid", None)
        ic_call_mid_str = f"{ic_call_mid_val:.2f}" if isinstance(ic_call_mid_val, (int, float)) else ""

        leg1_strike = getattr(combo, '_leg1_strike', 0)
        leg2_strike = getattr(combo, '_leg2_strike', 0)
        leg3_strike = getattr(combo, '_leg3_strike', None) if (is_pbw or is_ic) else None
        leg4_strike = getattr(combo, '_leg4_strike', None) if is_ic else None
        expiry = getattr(combo, '_expiry', '')

        et_tz = pytz.timezone('US/Eastern')

        if trade.fills:
            fill_time_utc = trade.fills[0].time
            if fill_time_utc.tzinfo is None:
                fill_time_utc = pytz.utc.localize(fill_time_utc)
            fill_dt_et = fill_time_utc.astimezone(et_tz)
        else:
            fill_dt_et = datetime.now(et_tz)

        timestamp = fill_dt_et.strftime('%Y-%m-%d %H:%M')

        if expiry and len(expiry) == 8:
            expiry_formatted = f"{expiry[0:4]}-{expiry[4:6]}-{expiry[6:8]}"
        else:
            expiry_formatted = ''

        if quantity is None:
            quantity = 1

        # ------------------------------------------------------------
        # FILL + COMMISSION AGGREGATION
        # ------------------------------------------------------------
        ib.sleep(2)

        fill_data = {}

        for fill in trade.fills:
            con_id = fill.contract.conId
            fill_price = fill.execution.price
            fill_qty = fill.execution.shares
            commission = 0.0

            if hasattr(fill, 'commissionReport') and fill.commissionReport:
                commission = abs(fill.commissionReport.commission)

            if fill.contract.strike == 0.0:
                logger.debug(
                    f"Fill (BAG summary, skipped): conId={con_id} "
                    f"price={fill_price} commission={commission}"
                )
                continue

            if con_id not in fill_data:
                fill_data[con_id] = {
                    'total_qty': 0.0,
                    'total_value': 0.0,
                    'commission': 0.0
                }

            fill_data[con_id]['total_qty'] += fill_qty
            fill_data[con_id]['total_value'] += fill_price * fill_qty
            fill_data[con_id]['commission'] += commission

            logger.debug(
                f"Fill (leg): conId={con_id} strike={int(fill.contract.strike)} "
                f"qty={int(fill_qty)} price={fill_price} commission={commission} "
                f"→ accumulated=${fill_data[con_id]['commission']:.4f}"
            )

        for con_id, d in fill_data.items():
            d['price'] = d['total_value'] / d['total_qty'] if d['total_qty'] > 0 else 0.0

        leg_conids = {}
        if hasattr(combo, 'comboLegs'):
            for i, combo_leg in enumerate(combo.comboLegs):
                leg_conids[i] = combo_leg.conId

        def get_leg_data(strike, leg_index):
            con_id = leg_conids.get(leg_index)
            if con_id and con_id in fill_data:
                return fill_data[con_id]['price'], fill_data[con_id]['commission']
            logger.warning(f"No fill data for leg {leg_index} (strike={strike}) - using estimate")
            return 0.0, commission_per_contract

        leg1_price, leg1_commission = get_leg_data(leg1_strike, 0)
        leg2_price, leg2_commission = get_leg_data(leg2_strike, 1)

        if is_ic:
            leg3_price, leg3_commission = get_leg_data(leg3_strike, 2)
            leg4_price, leg4_commission = get_leg_data(leg4_strike, 3)
            total_commission = leg1_commission + leg2_commission + leg3_commission + leg4_commission
        elif is_pbw:
            leg3_price, leg3_commission = get_leg_data(leg3_strike, 2)
            leg4_price = leg4_commission = None
            total_commission = leg1_commission + leg2_commission + leg3_commission
        else:
            leg3_price = leg3_commission = None
            leg4_price = leg4_commission = None
            total_commission = leg1_commission + leg2_commission

        if total_commission == 0:
            if is_ic:
                total_contracts = (leg1_qty + leg2_qty + leg3_qty + leg4_qty) * quantity
                leg3_commission = commission_per_contract * leg3_qty * quantity
                leg4_commission = commission_per_contract * leg4_qty * quantity
            elif is_pbw:
                total_contracts = (leg1_qty + leg2_qty + leg3_qty) * quantity
                leg3_commission = commission_per_contract * leg3_qty * quantity
            else:
                total_contracts = (leg1_qty + leg2_qty) * quantity

            total_commission = commission_per_contract * total_contracts
            leg1_commission = commission_per_contract * leg1_qty * quantity
            leg2_commission = commission_per_contract * leg2_qty * quantity
        else:
            logger.debug(f"Actual commission from fills: ${total_commission:.2f}")

        # ------------------------------------------------------------
        # CSV WRITE
        # ------------------------------------------------------------
        rows = []

        # ------------------------------------------------------------
        # IRON CONDOR: 4-leg logging
        # ------------------------------------------------------------
        if is_ic:
            delta_fmt = lambda d: f"{d:.4f}" if isinstance(d, (int, float)) else ""
            short_put_delta = getattr(metrics, "ic_short_put_delta", None)
            short_call_delta = getattr(metrics, "ic_short_call_delta", None)

            # LEG2 – LONG PUT
            rows.append({
                'Symbol': symbol, 'Type': '', 'Trade date and time': timestamp,
                'Option Expiration Date': expiry_formatted,
                'Option Strike': int(leg2_strike), 'Option Call/Put': 'Put',
                'Shares/Contracts': leg2_qty * quantity,
                'Price/Prem': f"{leg2_price:.2f}", 'Fees & Commissions': f"{leg2_commission:.2f}",
                'Notes': 'Long Put',
                'Option Action': '', 'Action Fees & Commissions': '', 'Action Date and time': '',
                'Expired Contracts': '', 'Assigned/Called Away/Exercised Shares': '', 'Action Notes': '',
                'SCHEDULE_NAME': strategy_name, 'Short Leg Mid': '', 'Delta': '',
            })

            # LEG1 – SHORT PUT
            rows.append({
                'Symbol': symbol, 'Type': '', 'Trade date and time': timestamp,
                'Option Expiration Date': expiry_formatted,
                'Option Strike': int(leg1_strike), 'Option Call/Put': 'Put',
                'Shares/Contracts': -(leg1_qty * quantity),
                'Price/Prem': f"{leg1_price:.2f}", 'Fees & Commissions': f"{leg1_commission:.2f}",
                'Notes': 'Short Put',
                'Option Action': '', 'Action Fees & Commissions': '', 'Action Date and time': '',
                'Expired Contracts': '', 'Assigned/Called Away/Exercised Shares': '', 'Action Notes': '',
                'SCHEDULE_NAME': strategy_name, 'Short Leg Mid': short_mid_str, 'Delta': delta_fmt(short_put_delta),
            })

            # LEG3 – SHORT CALL
            rows.append({
                'Symbol': symbol, 'Type': '', 'Trade date and time': timestamp,
                'Option Expiration Date': expiry_formatted,
                'Option Strike': int(leg3_strike), 'Option Call/Put': 'Call',
                'Shares/Contracts': -(leg3_qty * quantity),
                'Price/Prem': f"{leg3_price:.2f}", 'Fees & Commissions': f"{leg3_commission:.2f}",
                'Notes': 'Short Call',
                'Option Action': '', 'Action Fees & Commissions': '', 'Action Date and time': '',
                'Expired Contracts': '', 'Assigned/Called Away/Exercised Shares': '', 'Action Notes': '',
                'SCHEDULE_NAME': strategy_name, 'Short Leg Mid': ic_call_mid_str, 'Delta': delta_fmt(short_call_delta),
            })

            # LEG4 – LONG CALL
            rows.append({
                'Symbol': symbol, 'Type': '', 'Trade date and time': timestamp,
                'Option Expiration Date': expiry_formatted,
                'Option Strike': int(leg4_strike), 'Option Call/Put': 'Call',
                'Shares/Contracts': leg4_qty * quantity,
                'Price/Prem': f"{leg4_price:.2f}", 'Fees & Commissions': f"{leg4_commission:.2f}",
                'Notes': 'Long Call',
                'Option Action': '', 'Action Fees & Commissions': '', 'Action Date and time': '',
                'Expired Contracts': '', 'Assigned/Called Away/Exercised Shares': '', 'Action Notes': '',
                'SCHEDULE_NAME': strategy_name, 'Short Leg Mid': '', 'Delta': '',
            })

        # ------------------------------------------------------------
        # PBW: 3-leg logging (unverändert)
        # ------------------------------------------------------------
        elif is_pbw:

            short_delta = metrics.short_delta
            delta_fmt = lambda d: f"{d:.4f}" if isinstance(d, (int, float)) else ""

            leg1_delta = getattr(metrics, "leg1_delta", short_delta)

            rows.append({
                'Symbol': symbol, 'Type': '', 'Trade date and time': timestamp,
                'Option Expiration Date': expiry_formatted,
                'Option Strike': int(leg2_strike), 'Option Call/Put': 'Put',
                'Shares/Contracts': leg2_qty * quantity,
                'Price/Prem': f"{leg2_price:.2f}", 'Fees & Commissions': f"{leg2_commission:.2f}",
                'Notes': 'Lower Wing',
                'Option Action': '', 'Action Fees & Commissions': '', 'Action Date and time': '',
                'Expired Contracts': '', 'Assigned/Called Away/Exercised Shares': '', 'Action Notes': '',
                'SCHEDULE_NAME': strategy_name, 'Short Leg Mid': '', 'Delta': '',
            })

            rows.append({
                'Symbol': symbol, 'Type': '', 'Trade date and time': timestamp,
                'Option Expiration Date': expiry_formatted,
                'Option Strike': int(leg1_strike), 'Option Call/Put': 'Put',
                'Shares/Contracts': -(leg1_qty * quantity),
                'Price/Prem': f"{leg1_price:.2f}", 'Fees & Commissions': f"{leg1_commission:.2f}",
                'Notes': 'Body',
                'Option Action': '', 'Action Fees & Commissions': '', 'Action Date and time': '',
                'Expired Contracts': '', 'Assigned/Called Away/Exercised Shares': '', 'Action Notes': '',
                'SCHEDULE_NAME': strategy_name, 'Short Leg Mid': '', 'Delta': delta_fmt(leg1_delta),
            })

            rows.append({
                'Symbol': symbol, 'Type': '', 'Trade date and time': timestamp,
                'Option Expiration Date': expiry_formatted,
                'Option Strike': int(leg3_strike), 'Option Call/Put': 'Put',
                'Shares/Contracts': leg3_qty * quantity,
                'Price/Prem': f"{leg3_price:.2f}", 'Fees & Commissions': f"{leg3_commission:.2f}",
                'Notes': 'Upper Wing',
                'Option Action': '', 'Action Fees & Commissions': '', 'Action Date and time': '',
                'Expired Contracts': '', 'Assigned/Called Away/Exercised Shares': '', 'Action Notes': '',
                'SCHEDULE_NAME': strategy_name, 'Short Leg Mid': '', 'Delta': '',
            })

        # ------------------------------------------------------------
        # DEFAULT: 2-leg spreads (unverändert)
        # ------------------------------------------------------------
        else:
            rows.extend([
                {
                    'Symbol': symbol, 'Type': '', 'Trade date and time': timestamp,
                    'Option Expiration Date': expiry_formatted,
                    'Option Strike': int(leg1_strike), 'Option Call/Put': 'Put',
                    'Shares/Contracts': -(leg1_qty * quantity),
                    'Price/Prem': f"{leg1_price:.2f}", 'Fees & Commissions': f"{leg1_commission:.2f}",
                    'Notes': f'{trade_type_label} - Short',
                    'Option Action': '', 'Action Fees & Commissions': '', 'Action Date and time': '',
                    'Expired Contracts': '', 'Assigned/Called Away/Exercised Shares': '', 'Action Notes': '',
                    'SCHEDULE_NAME': strategy_name, 'Short Leg Mid': short_mid_str, 'Delta': delta_str
                },
                {
                    'Symbol': symbol, 'Type': '', 'Trade date and time': timestamp,
                    'Option Expiration Date': expiry_formatted,
                    'Option Strike': int(leg2_strike), 'Option Call/Put': 'Put',
                    'Shares/Contracts': leg2_qty * quantity,
                    'Price/Prem': f"{leg2_price:.2f}", 'Fees & Commissions': f"{leg2_commission:.2f}",
                    'Notes': f'{trade_type_label} - Long',
                    'Option Action': '', 'Action Fees & Commissions': '', 'Action Date and time': '',
                    'Expired Contracts': '', 'Assigned/Called Away/Exercised Shares': '', 'Action Notes': '',
                    'SCHEDULE_NAME': strategy_name, 'Short Leg Mid': '', 'Delta': ''
                }
            ])

        os.makedirs(os.path.dirname(csv_file), exist_ok=True)
        file_exists = os.path.exists(csv_file)

        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            if not file_exists:
                writer.writeheader()
            for row in rows:
                writer.writerow(row)

        expiry_fmt = datetime.strptime(expiry, "%Y%m%d").strftime("%b%d'%y")
        if is_ic:
            logger.info(
                f"✅ Trade logged: IRON CONDOR {quantity} {symbol} {expiry_fmt} "
                f"{int(leg2_strike)}/{int(leg1_strike)}P  {int(leg3_strike)}/{int(leg4_strike)}C"
            )
        elif is_pbw:
            logger.info(
                f"✅ Trade logged: BUY {quantity} {symbol} {expiry_fmt} "
                f"{int(leg2_strike)}/{int(leg1_strike)}/{int(leg3_strike)} "
                f"{trade_type_label}"
            )
        else:
            logger.info(
                f"✅ Trade logged: BUY {quantity} {symbol} {expiry_fmt} "
                f"{int(leg1_strike)}/{int(leg2_strike)} {trade_type_label}"
            )

        # ------------------------------------------------------------
        # TELEGRAM
        # ------------------------------------------------------------
        if telegram_enabled and telegram_chat_id:
            account_type = "📝 Paper Trading" if is_paper_trading else "💰 Live Trading"
            now_et = fill_dt_et
            expiry_date = datetime.strptime(expiry, '%Y%m%d')
            dte = (expiry_date.date() - now_et.date()).days

            credit_per_contract = abs(premium_paid)
            total_credit = credit_per_contract * quantity * 100
            net_credit = total_credit - total_commission

            short_delta = metrics.short_delta
            short_delta_str = f"{short_delta:.3f}" if isinstance(short_delta, (int, float)) else "n/a"

            spread_width = None
            if trade_type.upper() in ("BULL_PUT", "BULL_CALL"):
                spread_width = abs(int(leg1_strike) - int(leg2_strike))

            extra_ic_line = ""
            short_delta_label = "Delta (short)"

            if is_ic:
                short_delta_label = "Delta (short put)"
                put_width = int(leg1_strike - leg2_strike)
                call_width = int(leg4_strike - leg3_strike)

                strikes_str = f"{int(leg2_strike)}/{int(leg1_strike)}P  {int(leg3_strike)}/{int(leg4_strike)}C"
                spread_info = (
                    f"├ Put-Spread Breite: <b>{put_width} Punkte</b>\n"
                    f"├ Call-Spread Breite: <b>{call_width} Punkte</b>\n"
                )

                call_delta_val = getattr(metrics, "ic_short_call_delta", None)
                call_delta_str = f"{call_delta_val:.3f}" if isinstance(call_delta_val, (int, float)) else "n/a"
                extra_ic_line = f"├ Delta (short call): <b>{call_delta_str}</b>\n"

            elif is_pbw:
                lower_wing = int(leg1_strike - leg2_strike)
                upper_wing = int(leg3_strike - leg1_strike)

                strikes_str = f"{int(leg2_strike)} / {int(leg1_strike)} / {int(leg3_strike)}"
                spread_info = (
                    f"├ Lower Wing: <b>{lower_wing} points</b>\n"
                    f"├ Upper Wing: <b>{upper_wing} points</b>\n"
                )
            else:
                strikes_str = f"{int(leg1_strike)} / {int(leg2_strike)}"
                spread_info = f"├ Spread Width: <b>{int(spread_width)} points</b>\n"

            msg = f"""🔥 <b>{strategy_name} {trade_type_label} FILLED</b> 🔥

{account_type}

📅 <b>Entry Time:</b> {now_et.strftime('%Y-%m-%d %H:%M')} ET
📆 <b>Expiration:</b> {expiry_formatted} ({dte} DTE)

💰 <b>Details:</b>
├ Strikes: <b>{strikes_str}</b>
{spread_info.rstrip()}
├ Quantity: <b>{quantity}</b>

💵 <b>Entry:</b>
├ Credit/contract: <b>${credit_per_contract:.2f} (${credit_per_contract*100:.0f})</b>
├ Total Credit: <b>${total_credit:.2f}</b>
├ Total Commission: <b>${total_commission:.2f}</b>
├ Net Credit: <b>${net_credit:.2f}</b>
├ {short_delta_label}: <b>{short_delta_str}</b>
{extra_ic_line}"""

            if profit_target:
                msg += f"""
🎯 <b>Profit Target:</b> (GTC order placed)
├ Exit Price: <b>${profit_target['exit_price']:.2f}</b> ({profit_target['target_pct']:.0f}% profit)
├ Target Profit: <b>+${profit_target['expected_profit']:.2f}</b>
"""

            send_telegram_callable(msg)

    except Exception as e:
        logger.error(f"Failed to log trade: {e}", exc_info=True)