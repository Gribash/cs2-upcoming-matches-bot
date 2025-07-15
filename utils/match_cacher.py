import os
import asyncio
import logging
import json 
from datetime import datetime, timezone
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
        tournament_ids = [t["id"] for t in tournaments if isinstance(t, dict) and t.get("status") in ["running", "upcoming"]]

        if not tournament_ids:
            logger.warning("⚠️ Нет активных турниров для загрузки матчей.")
            return

        logger.debug(f"📋 Турниры: {tournament_ids}")

        matches_raw = await fetch_all_matches(tournament_ids)
        logger.info(f"📥 Загружено матчей: {len(matches_raw)}")
       
        if matches_raw:
            logger.info(f"🔬 Пример streams: {json.dumps(matches_raw[0].get('streams', []), indent=2)}")

        simplified = []
        for m in matches_raw:
            begin_at = m.get("begin_at")
            stream_url = extract_stream_url(m.get("streams", []))

            opponents = [
                {
                    "name": opp["opponent"].get("name"),
                    "acronym": opp["opponent"].get("acronym")
                }
                for opp in m.get("opponents", [])
                if opp.get("opponent") and opp["opponent"].get("name")
            ]

            simplified.append({
                "id": m.get("id"),
                "tournament_id": m.get("tournament_id"),
                "tournament_name": m.get("tournament", {}).get("name"),
                "league_name": m.get("league", {}).get("name"),
                "begin_at": begin_at,
                "time_until": format_time_until(begin_at) if begin_at else None,
                "status": m.get("status"),
                "stream_url": stream_url,
                "winner_id": m.get("winner_id"),
                "opponents": opponents
            })

        cache_payload = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "matches": simplified
        }

        write_json_to_cache(CACHE_FILENAME, cache_payload)
        logger.info(f"✅ Кэш матчей обновлён: {len(simplified)} записей")
        logger.info(f"🕒 Время обновления кэша: {cache_payload['updated_at']}")

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