import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

from utils.pandascore import fetch_all_matches, extract_stream_url, format_time_until
from utils.tournament_cache_reader import load_tournaments_from_cache
from utils.cache_writer import write_json_to_cache
from utils.logging_config import setup_logging

# Загрузка .env
load_dotenv()

# Настройка логирования
os.makedirs("logs", exist_ok=True)
setup_logging()
logger = logging.getLogger("matches")
logger.setLevel(logging.INFO)

# Параметры
CACHE_FILENAME = "matches.json"
INTERVAL_SECONDS = 600  # 10 минут

async def update_match_cache():
    try:
        logger.info("🔄 Загрузка матчей по кэшированным турнирам...")

        tournaments = load_tournaments_from_cache()
        tournament_ids = [t["id"] for t in tournaments if t.get("status") in ["running", "upcoming"]]

        if not tournament_ids:
            logger.warning("⚠️ Нет активных турниров для загрузки матчей.")
            return

        logger.debug(f"📋 Турниры: {tournament_ids}")

        matches_raw = await fetch_all_matches(tournament_ids)
        logger.info(f"📥 Загружено матчей: {len(matches_raw)}")

        simplified = []
        for m in matches_raw:
            teams = " vs ".join(
                [t["opponent"]["name"] for t in m.get("opponents", []) if t.get("opponent")]
            ) or "TBD"

            stream_url = extract_stream_url(m.get("streams", []))
            begin_at = m.get("begin_at")

            simplified.append({
                "id": m.get("id"),
                "tournament_id": m.get("tournament_id"),
                "teams": teams,
                "begin_at": begin_at,
                "time_until": format_time_until(begin_at) if begin_at else None,
                "status": m.get("status"),
                "stream_url": stream_url,
                "winner_id": m.get("winner_id"),
            })

        write_json_to_cache(CACHE_FILENAME, simplified)
        logger.info(f"✅ Кэш матчей обновлён: {len(simplified)} записей")

    except Exception as e:
        logger.exception(f"🔥 Ошибка при обновлении матчей: {e}")

# Цикл с немедленным первым запуском
async def run_periodic_update():
    while True:
        await update_match_cache()
        await asyncio.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    logger.info("🚀 Запуск фонового обновления матчей (цикл)")
    asyncio.run(run_periodic_update())