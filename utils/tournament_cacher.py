import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

from utils.pandascore import fetch_all_tournaments
from utils.cache_writer import write_json_to_cache

# Загрузка .env
load_dotenv()

# --- Настройка логирования ---
os.makedirs("logs", exist_ok=True)
tournaments_logger = logging.getLogger("tournaments")
tournaments_logger.setLevel(logging.INFO)
tournaments_logger.propagate = False

file_handler = logging.FileHandler("logs/tournaments.log")
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler.setFormatter(formatter)
tournaments_logger.addHandler(file_handler)

# --- Параметры ---
CACHE_FILENAME = "tournaments.json"
INTERVAL_SECONDS = 3600  # запуск раз в час

# --- Обновление турниров ---
async def update_tournaments():
    try:
        tournaments_logger.info("⏳ Запуск обновления турниров...")

        tournaments = await fetch_all_tournaments()
        tournaments_logger.info(f"📥 Загружено турниров: {len(tournaments)}")

        write_json_to_cache(CACHE_FILENAME, tournaments)
        tournaments_logger.info(f"✅ Кэш турниров обновлён: {len(tournaments)} записей")

    except Exception as e:
        tournaments_logger.exception(f"🔥 Ошибка при обновлении турниров: {e}")

# --- Цикл с немедленным первым запуском ---
async def run_periodic_update():
    while True:
        await update_tournaments()
        await asyncio.sleep(INTERVAL_SECONDS)

# --- Точка входа ---
if __name__ == "__main__":
    tournaments_logger.info("🚀 Запуск фонового обновления турниров (цикл)")
    asyncio.run(run_periodic_update())