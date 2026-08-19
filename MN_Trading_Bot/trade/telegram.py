# trade/telegram.py

import requests

def send_telegram_notification(
    *,
    enabled: bool,
    chat_id: str,
    bot_token: str,
    message: str,
    logger,
):
    """
    Send Telegram notification.
    Logic identical to Bot.send_telegram_notification.
    """

    if not enabled:
        return

    if not chat_id:
        logger.warning("Telegram enabled but chat_id missing")
        return

    if not bot_token:
        logger.warning(
            "Telegram notifications enabled but bot_token not configured. "
            "Update telegram_settings.json."
        )
        return

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
        }

        response = requests.post(url, data=data, timeout=5)

        if response.status_code == 200:
            logger.info("✅ Telegram notification sent")
        else:
            logger.warning(
                f"Telegram API returned status {response.status_code}"
            )

    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {e}")