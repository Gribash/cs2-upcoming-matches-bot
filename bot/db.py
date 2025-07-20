import sqlite3
import os
import logging
from utils.logging_config import setup_logging

# Путь к базе данных
DB_PATH = "data/subscribers.db"

# Настройка логгера
setup_logging()
logger = logging.getLogger("db")
logger.setLevel(logging.DEBUG if os.getenv("DEV_MODE") == "true" else logging.INFO)

# Инициализация базы данных и таблиц
def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            user_id INTEGER PRIMARY KEY,
            tier TEXT DEFAULT 'sa' CHECK(tier IN ('sa', 'all')),
            is_active INTEGER DEFAULT 1,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_subscribers_active ON subscribers (is_active);
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

def add_subscriber(user_id: int, tier: str = "sa"):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("""
            INSERT INTO subscribers (user_id, tier, is_active)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id) DO UPDATE SET
                tier = excluded.tier,
                is_active = 1
        """, (user_id, tier))

        conn.commit()
        conn.close()
        logger.info(f"Подписчик {user_id} добавлен/обновлён с tier={tier}")
    except Exception as e:
        logger.error(f"Ошибка при добавлении/обновлении подписчика {user_id}: {e}")

def remove_subscriber(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        logger.info(f"Отключаем уведомления для пользователя {user_id}.")
        conn.execute("UPDATE subscribers SET is_active = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        logger.info(f"Пользователь {user_id} отмечен как неактивный.")

def get_all_subscribers() -> list[int]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT user_id FROM subscribers WHERE is_active = 1")
        users = [row[0] for row in cursor.fetchall()]
        logger.debug(f"Получено {len(users)} активных подписчиков из базы: {users}")
        return users

def get_subscriber_tier(user_id: int) -> str:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT tier FROM subscribers WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        tier = row[0] if row else "sa"
        logger.debug(f"Tier для пользователя {user_id}: {tier}")
        return tier

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
        ids = [row[0] for row in cursor.fetchall()]
        logger.debug(f"Получено {len(ids)} уведомлений для пользователя {user_id}: {ids}")
        return set(ids)
    
def update_is_active(user_id: int, is_active: bool):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE subscribers SET is_active = ? WHERE user_id = ?", (1 if is_active else 0, user_id))
        conn.commit()
        logger.info(f"Пользователь {user_id} обновлён: is_active = {is_active}")

def is_subscriber_active(user_id: int) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT is_active FROM subscribers WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        result = row is not None and row[0] == 1
        logger.debug(f"Проверка активности пользователя {user_id}: {result}")
        return result
    
def update_tier(user_id: int, tier: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE subscribers SET tier = ? WHERE user_id = ?",
            (tier, user_id)
        )
        conn.commit()
        logger.info(f"У пользователя {user_id} обновлён уровень подписки на {tier}.")

def create_indexes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_match
        ON notified_matches(user_id, match_id);
    """)
    conn.commit()
    conn.close()