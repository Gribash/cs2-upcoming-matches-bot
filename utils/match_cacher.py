import asyncio
import logging
import sys

from utils.logging_config import setup_logger
from utils.cache_writer import write_json_to_cache, MATCHES_CACHE_NAME
from utils.pandascore import fetch_all_matches

# Настройка логгера
logger = setup_logger("matches")

# Интервал обновления в секундах
CACHE_INTERVAL_SECONDS = 600  # 10 минут

async def cache_matches_loop(once=False):
    while True:
        try:
            logger.info("Загрузка матчей из PandaScore...")
            match_data = await fetch_all_matches()
            write_json_to_cache(MATCHES_CACHE_NAME, match_data)
            logger.info(f"Сохранено {len(match_data['matches'])} матчей в кэш.")
        except Exception as e:
            logger.error(f"Ошибка при обновлении кэша матчей: {e}", exc_info=True)

        if once:
            break

        await asyncio.sleep(CACHE_INTERVAL_SECONDS)

if __name__ == "__main__":
    once_flag = "--once" in sys.argv
    asyncio.run(cache_matches_loop(once=once_flag))