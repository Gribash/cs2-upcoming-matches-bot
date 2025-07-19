import os
import json
from datetime import datetime, timezone
from typing import Optional

CACHE_DIR = "cache"
MATCHES_CACHE_NAME = "matches"

os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(name: str) -> str:
    return os.path.join(CACHE_DIR, f"{name}.json")

def write_json_to_cache(name: str, data: dict):
    path = get_cache_path(name)
    tmp_path = path + ".tmp"

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    os.replace(tmp_path, path)

def read_json_from_cache(name: str) -> Optional[dict]:
    path = get_cache_path(name)
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

def get_cache_last_modified(name: str) -> Optional[datetime]:
    path = get_cache_path(name)
    if not os.path.exists(path):
        return None

    ts = os.path.getmtime(path)
    return datetime.fromtimestamp(ts, tz=timezone.utc)