import sqlite3
from datetime import datetime, timedelta, timezone
import logging
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("db")

DB_PATH = "data/subscribers.db"

def cleanup_notified_matches(days=2):
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM notified_matches WHERE notified_at < ?",
                (cutoff_str,)
            )
            deleted = cursor.rowcount
            conn.commit()

        logger.info(f"🧹 Удалено старых записей: {deleted}")
    except Exception as e:
        logger.exception(f"Ошибка при очистке notified_matches: {e}")

if __name__ == "__main__":
    cleanup_notified_matches()