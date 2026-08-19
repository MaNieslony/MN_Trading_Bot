# broker/ib_broker.py

import time
from ib_insync import IB


class IBBroker:
    """
    Kapselt IB-Verbindung + Reconnect + Health-Checks.
    Der Bot enthält keine IB-connect/disconnect Logik mehr.
    """

    def __init__(self, ib: IB, logger, host: str, port: int, client_id: int,
                 is_market_open_callable, setup_error_callback_callable):
        self.ib = ib
        self.logger = logger

        self.host = host
        self.port = port
        self.client_id = client_id

        # Callbacks aus Bot (weil die Logik dort schon existiert)
        self.is_market_open = is_market_open_callable
        self._setup_error_callback = setup_error_callback_callable

        self.is_paper_trading = (self.port == 7497)

    def connect(self) -> bool:
        """Connect to Interactive Brokers."""
        CONNECT_TIMEOUT = 30  # Standard ib_insync default is only 4s
        max_internal_attempts = 2

        for internal_attempt in range(1, max_internal_attempts + 1):
            try:
                if self.ib.isConnected():
                    try:
                        self.ib.disconnect()
                    except Exception:
                        pass

                self.ib.connect(
                    self.host,
                    self.port,
                    clientId=self.client_id,
                    timeout=CONNECT_TIMEOUT,
                )

                # Setup error logging
                self._setup_error_callback()

                # Paper/Live info
                self.is_paper_trading = (self.port == 7497)
                if self.is_paper_trading:
                    self.logger.info("📝 PAPER TRADING MODE detected")
                else:
                    self.logger.info("💰 LIVE TRADING MODE detected")

                # Market data type selection
                if self.is_market_open():
                    data_type = 1  # Live
                    self.logger.debug("Using LIVE market data (market open)")
                else:
                    data_type = 3  # Delayed
                    self.logger.debug("Using DELAYED market data (market closed)")

                self.ib.reqMarketDataType(data_type)
                return True

            except TimeoutError as e:
                self.logger.warning(
                    f"⏱️ Connect timed out ({CONNECT_TIMEOUT}s) - "
                    f"internal attempt {internal_attempt}/{max_internal_attempts}: {e}"
                )
                if internal_attempt < max_internal_attempts:
                    time.sleep(3)
                    continue
                self.logger.error("❌ Failed to connect to IB after internal retries (timeout)")
                return False

            except Exception as e:
                self.logger.error(f"❌ Failed to connect to IB: {e}", exc_info=True)
                return False

        return False

    def disconnect(self):
        """Disconnect from Interactive Brokers."""
        if self.ib.isConnected():
            self.ib.disconnect()
            self.logger.info("Disconnected from IB")

    def reconnect(self, max_retries: int = 3) -> bool:
        """Simple reconnect logic with fixed backoff."""

        # ✅ SHUTDOWN-GUARD (entscheidend!)
        if getattr(self, "bot", None) and getattr(self.bot, "_shutting_down", False):
            self.logger.info("Reconnect suppressed – bot is shutting down")
            return False

        if self.ib.isConnected():
            try:
                self.ib.disconnect()
            except Exception:
                pass

        for attempt in range(1, max_retries + 1):
            # ✅ Nochmals absichern
            if getattr(self.bot, "_shutting_down", False):
                self.logger.info("Reconnect aborted – bot is shutting down")
                return False

            self.logger.warning(f"🔄 Reconnect attempt {attempt}/{max_retries}")

            try:
                if self.connect():
                    self.logger.info("✅ Reconnected successfully")
                    return True
            except Exception as e:
                self.logger.error(f"Reconnect attempt failed: {e}", exc_info=True)

            time.sleep(5)

        self.logger.error("❌ Reconnect failed after all attempts")
        return False

    def check_connection_health(self) -> bool:
        """Check if connection is alive and reconnect if needed."""

        # ✅ SHUTDOWN-GUARD
        if getattr(self, "bot", None) and getattr(self.bot, "_shutting_down", False):
            return False

        try:
            if self.ib.isConnected():
                return True

            self.logger.warning("⚠️ Connection lost - attempting reconnect")
            return self.reconnect()

        except Exception as e:
            self.logger.error(f"Connection health check error: {e}", exc_info=True)
            return False