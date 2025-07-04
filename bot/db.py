import sqlite3
import os
import logging

# Путь к базе данных
DB_PATH = "data/subscribers.db"

# Настройка логгера
logger = logging.getLogger(__name__)

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Таблица подписчиков
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            user_id INTEGER PRIMARY KEY
        );
    """)

    # Таблица уведомлений о матчах
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notified_matches (
            user_id INTEGER NOT NULL,
            match_id INTEGER NOT NULL,
            notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, match_id)
        );
    """)

    conn.commit()
    conn.close()
    logger.info("База данных и таблицы инициализированы.")

def add_subscriber(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR IGNORE INTO subscribers (user_id) VALUES (?)", (user_id,))
        conn.commit()
        logger.info(f"Пользователь {user_id} добавлен в подписчики.")

def remove_subscriber(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        logger.info(f"Попытка удалить пользователя {user_id} из подписчиков.")
        cursor = conn.execute("DELETE FROM subscribers WHERE user_id = ?", (user_id,))
        conn.commit()
        logger.info(f"Удалено строк: {cursor.rowcount}")

def get_all_subscribers() -> list[int]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT user_id FROM subscribers")
        users = [row[0] for row in cursor.fetchall()]
        logger.info(f"Получено {len(users)} подписчиков из базы.")
        return users

def was_notified(user_id: int, match_id: int) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT 1 FROM notified_matches WHERE user_id = ? AND match_id = ?",
            (user_id, match_id)
        )
        result = cursor.fetchone() is not None
        logger.debug(f"Проверка уведомления: user_id={user_id}, match_id={match_id}, result={result}")
        return result

def mark_notified(user_id: int, match_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO notified_matches (user_id, match_id) VALUES (?, ?)",
            (user_id, match_id)
        )
        conn.commit()
        logger.info(f"Пометка: пользователь {user_id} уведомлён о матче {match_id}.")

def get_notified_match_ids(user_id: int) -> set:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT match_id FROM notified_matches WHERE user_id = ?", (user_id,))
        ids = {row[0] for row in cursor.fetchall()}
        logger.debug(f"Получено {len(ids)} уведомлений для пользователя {user_id}")
        return ids