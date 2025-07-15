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
INTERVAL_SECONDS = 3600  # 1 час

async def update_tournament_cache():
    try:
        logger.info("🔄 Загрузка турниров...")

        tournaments_raw = await fetch_all_tournaments()
        logger.info(f"📥 Загружено турниров: {len(tournaments_raw)}")

        simplified = [
            {
                "id": t["id"],
                "name": t["name"],
                "slug": t.get("slug"),
                "tier": t.get("tier"),
                "status": t.get("status"),
                "league_id": t.get("league_id"),
                "league_name": t.get("league", {}).get("name")
            }
            for t in tournaments_raw
        ]

        cache_payload = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "tournaments": simplified
        }

        write_json_to_cache(CACHE_FILENAME, cache_payload)
        logger.info(f"✅ Кэш турниров обновлён: {len(simplified)} записей")
        logger.info(f"🕒 Время обновления кэша: {cache_payload['updated_at']}")

    except Exception as e:
        logger.exception(f"🔥 Ошибка при обновлении турниров: {e}")

# Цикл с немедленным первым запуском
async def run_periodic_update():
    while True:
        await update_tournament_cache()
        await asyncio.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    logger.info("🚀 Запуск фонового обновления турниров (цикл)")
    asyncio.run(run_periodic_update())