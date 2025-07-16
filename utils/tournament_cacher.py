import os
import asyncio
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

from utils.pandascore import fetch_all_tournaments
from utils.cache_writer import write_json_to_cache
from utils.logging_config import setup_logging

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
os.makedirs("logs", exist_ok=True)
setup_logging()
logger = logging.getLogger("tournaments")
logger.setLevel(logging.INFO)

# Параметры
CACHE_FILENAME = "tournaments.json"
INTERVAL_SECONDS = 1800  # Интервал обновления кэша (30 минут)

async def update_tournaments_cache():
    try:
        logger.info("🔄 Обновление кэша турниров...")

        result = await fetch_all_tournaments()
        if not result or not isinstance(result, list):
            logger.warning("⚠️ Получен пустой или некорректный список турниров")
            return

        wrapped = {
            "tournaments": result,
            "updated_at": datetime.now(timezone.utc).isoformat()
}
        write_json_to_cache(CACHE_FILENAME, wrapped)
        logger.info(f"✅ Кэш турниров обновлён ({len(result)} шт.)")

    except Exception as e:
        logger.exception(f"❌ Ошибка при обновлении турниров: {e}")

async def run_periodic_update():
    while True:
        await update_tournaments_cache()
        await asyncio.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    logger.info("🚀 Запуск фонового обновления турниров (цикл)")
    asyncio.run(run_periodic_update())