import os
import logging

def setup_logging():
    # Убедимся, что папка для логов существует
    os.makedirs("logs", exist_ok=True)

    # --- Формат логов ---
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # --- Общий лог: bot.log ---
    bot_handler = logging.FileHandler("logs/bot.log")
    bot_handler.setLevel(logging.INFO)
    bot_handler.setFormatter(formatter)

    # --- Telegram HTTP-запросы: telegram_http.log ---
    telegram_handler = logging.FileHandler("logs/telegram_http.log")
    telegram_handler.setLevel(logging.INFO)
    telegram_handler.setFormatter(formatter)

    # --- Ошибки: errors.log ---
    error_handler = logging.FileHandler("logs/errors.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # --- Консоль ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # --- Корневой логгер ---
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(bot_handler)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(error_handler)

    # --- Telegram HTTP-запросы — отдельные логгеры ---
    for name in ["telegram.request", "telegram.ext._httpxrequest"]:
        http_logger = logging.getLogger(name)
        http_logger.setLevel(logging.INFO)
        http_logger.addHandler(telegram_handler)
        http_logger.propagate = False  # чтобы не дублировались в bot.log