import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional

# Константы
CACHE_DIR = "cache"
MATCHES_CACHE_NAME = "matches"

# Настройка логгера
logger = logging.getLogger("cache_writer")
logger.setLevel(logging.DEBUG if os.getenv("DEV_MODE") == "true" else logging.INFO)

# Создание директории, если не существует
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(name: str) -> str:
    path = os.path.join(CACHE_DIR, f"{name}.json")
    logger.debug(f"[get_cache_path] Путь к кэшу: {path}")
    return path

def write_json_to_cache(name: str, data: dict):
    path = get_cache_path(name)
    tmp_path = path + ".tmp"

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
        logger.info(f"[write_json_to_cache] Кэш '{name}' успешно записан ({path})")
    except Exception as e:
        logger.exception(f"[write_json_to_cache] Ошибка при записи кэша '{name}': {e}")

def read_json_from_cache(name: str) -> dict:
    path = get_cache_path(name)
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            else:
                logger.warning(f"⚠️ Кэш-файл {name} содержит не словарь, возвращаю пустой словарь.")
                return {}
        except Exception as e:
            logger.warning(f"❌ Ошибка чтения кэша {name}: {e}")
            return {}
        
def get_cache_last_modified(name: str) -> Optional[datetime]:
    path = get_cache_path(name)

    if not os.path.exists(path):
        logger.debug(f"[get_cache_last_modified] Кэш '{name}' не найден")
        return None

    try:
        ts = os.path.getmtime(path)
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        logger.debug(f"[get_cache_last_modified] Время последнего изменения кэша '{name}': {dt}")
        return dt
    except Exception as e:
        logger.warning(f"[get_cache_last_modified] Ошибка получения времени изменения '{name}': {e}")
        return None