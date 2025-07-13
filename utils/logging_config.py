import os
import logging

def setup_logging():
    os.makedirs("logs", exist_ok=True)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # --- bot.log ---
    bot_handler = logging.FileHandler("logs/bot.log")
    bot_handler.setLevel(logging.INFO)
    bot_handler.setFormatter(formatter)

    # --- notifications.log ---
    notif_handler = logging.FileHandler("logs/notifications.log")
    notif_handler.setLevel(logging.INFO)
    notif_handler.setFormatter(formatter)

    # --- telegram_http.log ---
    telegram_handler = logging.FileHandler("logs/telegram_http.log")
    telegram_handler.setLevel(logging.INFO)
    telegram_handler.setFormatter(formatter)

    # --- errors.log ---
    error_handler = logging.FileHandler("logs/errors.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # --- консоль ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # --- Настройка логгера для bot.py ---
    bot_logger = logging.getLogger("bot")
    bot_logger.setLevel(logging.INFO)
    bot_logger.addHandler(bot_handler)
    bot_logger.addHandler(console_handler)
    bot_logger.addHandler(error_handler)
    bot_logger.propagate = False

    # --- Настройка логгера для notifications.py ---
    notif_logger = logging.getLogger("notifications")
    notif_logger.setLevel(logging.INFO)
    notif_logger.addHandler(notif_handler)
    notif_logger.addHandler(console_handler)
    notif_logger.addHandler(error_handler)
    notif_logger.propagate = False

    # --- Telegram HTTP-запросы ---
    for name in ["telegram.request", "telegram.ext._httpxrequest"]:
        http_logger = logging.getLogger(name)
        http_logger.setLevel(logging.INFO)
        http_logger.addHandler(telegram_handler)
        http_logger.propagate = False