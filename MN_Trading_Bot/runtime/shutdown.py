# runtime/shutdown.py
import time

def shutdown(*, bot, broker, logger, timeout=5):
    if getattr(bot, "_shutdown_done", False):
        return

    # ✅ GLOBALER SHUTDOWN-STATE
    bot._shutting_down = True
    bot._shutdown_done = True

    logger.info("Bot shutdown initiated")
    bot.running = False

    elapsed = 0
    while getattr(bot, "trade_in_progress", False) and elapsed < timeout:
        time.sleep(1)
        elapsed += 1

    # ✅ IM SHUTDOWN IMMER DIREKT DISCONNECTEN
    broker.disconnect()

    logger.info("Bot shutdown complete")