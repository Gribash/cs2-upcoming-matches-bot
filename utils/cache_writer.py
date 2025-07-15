import os
import json
from datetime import datetime
from typing import List, Dict, Any

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# --- Безопасный сериализатор для нестандартных типов (например, datetime)
def safe_serialize(obj: Any):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

# --- Сохраняет данные в JSON-файл в папку cache с отладкой
def write_json_to_cache(filename: str, data: List[Dict]) -> None:
    path = os.path.join(CACHE_DIR, filename)

    print(f"📦 Пишем кэш: {filename}")
    print(f"🔢 Количество объектов: {len(data) if data else 0}")
    if data:
        if isinstance(data, dict) and "matches" in data and isinstance(data["matches"], list) and data["matches"]:
            print(f"🧪 Пример объекта: {json.dumps(data['matches'][0], indent=2, ensure_ascii=False, default=safe_serialize)}")
        elif isinstance(data, dict) and "tournaments" in data and isinstance(data["tournaments"], list) and data["tournaments"]:
            print(f"🧪 Пример объекта: {json.dumps(data['tournaments'][0], indent=2, ensure_ascii=False, default=safe_serialize)}")
        else:
            print("🧪 Нет объектов для примера")

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=safe_serialize)
            f.flush()
            os.fsync(f.fileno())
        print(f"✅ Кэш успешно сохранён в {path}")
    except Exception as e:
        print(f"❌ Ошибка сериализации или записи в кэш: {e}")

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