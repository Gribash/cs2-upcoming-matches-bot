import asyncio
import logging
from utils.pandascore import fetch_all_matches  
from utils.cache_writer import write_json_to_cache
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("refresh_cache")

async def main():
    logger.info("⏳ Обновление кэша матчей вручную...")
    matches = await fetch_all_matches()
    write_json_to_cache("matches", {"matches": matches})
    logger.info(f"✅ Успешно обновлён кэш: {len(matches)} матчей")

if __name__ == "__main__":
    asyncio.run(main())