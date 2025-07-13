import os
import json
from datetime import datetime
from typing import List, Dict

CACHE_DIR = "cache"

os.makedirs(CACHE_DIR, exist_ok=True)

def write_json_to_cache(filename: str, data: List[Dict]) -> None:
    """
    Сохраняет данные в JSON-файл в папку cache, с предварительной очисткой старых данных.
    """
    path = os.path.join(CACHE_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def read_json_from_cache(filename: str) -> List[Dict]:
    """
    Читает данные из JSON-файла, если он существует. Возвращает список.
    """
    path = os.path.join(CACHE_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_cache_last_modified(filename: str) -> str:
    """
    Возвращает дату последнего изменения кэша в формате ISO или "".
    """
    path = os.path.join(CACHE_DIR, filename)
    if not os.path.exists(path):
        return ""
    timestamp = os.path.getmtime(path)
    return datetime.utcfromtimestamp(timestamp).isoformat()