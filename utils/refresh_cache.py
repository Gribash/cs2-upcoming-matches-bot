import asyncio
from utils.pandascore import fetch_all_tournaments
from utils.cache_writer import write_json_to_cache

import logging
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("refresh")

async def main():
    logger.info("⏳ Обновление кэша турниров вручную...")
    tournaments = await fetch_all_tournaments()
    write_json_to_cache("tournaments", {"tournaments": tournaments})
    logger.info(f"✅ Успешно обновлён кэш: {len(tournaments)} турниров")

if __name__ == "__main__":
    asyncio.run(main())