import os
import logging

def setup_logging():
    os.makedirs("logs", exist_ok=True)

    propagate_logs = os.getenv("LOG_PROPAGATE", "0") == "1"  # 🔄 включается через окружение

    loggers = {
        "bot": "logs/bot.log",
        "notifications": "logs/notifications.log",
        "matches": "logs/matches.log",
        "matches_cache_reader": "logs/matches_cache_reader.log",
        "db": "logs/db.log",
        "cache_writer": "logs/cache_writer.log",
        "error": "logs/errors.log"
    }

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    for name, path in loggers.items():
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.propagate = propagate_logs  # 👈 включаем propagate для тестов

        if not logger.handlers:
            file_handler = logging.FileHandler(path)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    # Настройка root-логгера
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(console_handler)