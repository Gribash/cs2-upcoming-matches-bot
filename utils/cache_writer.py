import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from utils.logging_config import setup_logging

CACHE_DIR = "cache"
MATCHES_CACHE_NAME = "matches"

setup_logging()
logger = logging.getLogger("matches")

os.makedirs(CACHE_DIR, exist_ok=True)


def get_cache_path(name: str) -> str:
    return os.path.join(CACHE_DIR, f"{name}.json")


def write_json_to_cache(name: str, data: dict):
    path = get_cache_path(name)
    tmp_path = path + ".tmp"

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        os.replace(tmp_path, path)
        logger.info(f"✅ Кэш-файл {name} успешно сохранён.")
    except Exception as e:
        logger.error(f"❌ Ошибка при сохранении кэша {name}: {e}")


def read_json_from_cache(name: str) -> dict:
    path = get_cache_path(name)
    if not os.path.exists(path):
        logger.warning(f"⚠️ Кэш-файл {name} не найден.")
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                logger.debug(f"📥 Кэш {name} успешно загружен.")
                return data
            else:
                logger.warning(f"⚠️ Кэш-файл {name} содержит несловарь.")
                return {}
    except Exception as e:
        logger.warning(f"❌ Ошибка чтения кэша {name}: {e}")
        return {}


def get_cache_last_modified(name: str) -> Optional[datetime]:
    path = get_cache_path(name)
    if not os.path.exists(path):
        return None

    ts = os.path.getmtime(path)
    return datetime.fromtimestamp(ts, tz=timezone.utc)