import sqlite3
from datetime import datetime, timedelta, timezone
import logging
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("db")

DB_PATH = "data/subscribers.db"

def cleanup_notified_matches(days=2):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "DELETE FROM notified_matches WHERE timestamp < ?",
            (cutoff_str,)
        )
        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        logger.info(f"🧹 Удалено старых записей: {deleted}")
    except Exception as e:
        logger.exception(f"Ошибка при очистке notified_matches: {e}")

if __name__ == "__main__":
    cleanup_notified_matches()