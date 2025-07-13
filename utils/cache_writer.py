import os
import json
from datetime import datetime
from typing import List, Dict

CACHE_DIR = "cache"

os.makedirs(CACHE_DIR, exist_ok=True)

# Сохраняет данные в JSON-файл в папку cache, с предварительной очисткой старых данных.

def write_json_to_cache(filename: str, data: List[Dict]) -> None:
    path = os.path.join(CACHE_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Читает данные из JSON-файла в папке cache, если он существует. Возвращает список.

def read_json_from_cache(filename: str) -> List[Dict]:
    path = os.path.join(CACHE_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Возвращает дату последнего изменения кэша в формате ISO или пустую строку, если файл не существует.

def get_cache_last_modified(filename: str) -> str:
    path = os.path.join(CACHE_DIR, filename)
    if not os.path.exists(path):
        return ""
    timestamp = os.path.getmtime(path)
    from datetime import datetime, timezone
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()