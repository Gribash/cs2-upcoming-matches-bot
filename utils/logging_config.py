import os
import logging

def setup_logging():
    os.makedirs("logs", exist_ok=True)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # --- Общие хендлеры ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    error_handler = logging.FileHandler("logs/errors.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # --- Специфичные хендлеры для каждого модуля ---
    loggers_config = {
        "bot": "logs/bot.log",
        "notifications": "logs/notifications.log",
        "matches": "logs/matches.log",
        "telegram_http": "logs/telegram_http.log",
        "db": "logs/db.log",
    }

    for name, filepath in loggers_config.items():
        handler = logging.FileHandler(filepath)
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.addHandler(console_handler)
        logger.addHandler(error_handler)
        logger.propagate = False

    # --- Telegram HTTP-запросы ---
    for http_name in ["telegram.request", "telegram.ext._httpxrequest"]:
        http_logger = logging.getLogger(http_name)
        http_logger.setLevel(logging.INFO)
        http_handler = logging.FileHandler(loggers_config["telegram_http"])
        http_handler.setLevel(logging.INFO)
        http_handler.setFormatter(formatter)
        http_logger.addHandler(http_handler)
        http_logger.propagate = False