import os
import logging

def setup_logging():
    os.makedirs("logs", exist_ok=True)

    loggers = {
        "bot": "logs/bot.log",
        "notifications": "logs/notifications.log",
        "matches": "logs/matches.log",
        "db": "logs/db.log",
        "error": "logs/errors.log"
    }

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    for name, path in loggers.items():
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.propagate = False  # Отключаем передачу в root-логгер

        # ✅ Проверка на существующие хендлеры
        if not logger.handlers:
            file_handler = logging.FileHandler(path)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    # Отдельно можно настроить консольный вывод (один раз для root)
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(console_handler)