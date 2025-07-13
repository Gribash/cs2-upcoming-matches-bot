import os
import logging
import httpx
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

PANDASCORE_TOKEN = os.getenv("PANDASCORE_TOKEN")
BASE_URL = "https://api.pandascore.co"
HEADERS = {
    "Authorization": f"Bearer {PANDASCORE_TOKEN}"
}

logger = logging.getLogger(__name__)

# Загружаем все турниры и фильтруем нужные поля.
# Используется в tournament_cacher.py

async def fetch_all_tournaments():
    tournaments = []
    page = 1
    per_page = 100

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            url = f"{BASE_URL}/csgo/tournaments?page={page}&per_page={per_page}"
            r = await client.get(url, headers=HEADERS)
            if r.status_code != 200:
                logger.warning(f"Ошибка загрузки турниров: {r.status_code}")
                break

            data = r.json()
            if not data:
                break

            for t in data:
                tournaments.append({
                    "id": t["id"],
                    "name": t.get("name"),
                    "league_id": t.get("league_id"),
                    "tier": t.get("tier", "unknown"),
                    "status": t.get("status", "unknown"),
                })

            page += 1

    return tournaments

# Загружает все матчи по списку ID турниров.
# Используется в match_cacher.py

async def fetch_all_matches(tournament_ids):
    matches = []
    page = 1
    per_page = 100

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            url = f"{BASE_URL}/matches"
            params = {
                "filter[tournament_id]": ",".join(map(str, tournament_ids)),
                "page": page,
                "per_page": per_page,
                "sort": "begin_at"
            }

            r = await client.get(url, headers=HEADERS, params=params)
            if r.status_code != 200:
                logger.warning(f"Ошибка загрузки матчей: {r.status_code}")
                break
            data = r.json()
            if not data:
                break

            matches.extend(data)
            page += 1

    return matches

# Извлекает ссылку на основную трансляцию из списка потоков.
# Используется в match_cacher.py и notifications.py

def extract_stream_url(streams_list: list) -> str:
    if not streams_list:
        return None

    for stream in streams_list:
        if stream.get("main") is True:
            return stream.get("raw_url")

    for stream in streams_list:
        if stream.get("raw_url"):
            return stream["raw_url"]

    return None

# Форматирует время до начала матча.
# Используется в match_cacher.py и notifications.py

def format_time_until(start_time_iso: str) -> str:
    try:
        start_time = datetime.fromisoformat(start_time_iso.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = start_time - now

        if delta.total_seconds() < 0:
            return "⏱ Уже начался"

        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes = remainder // 60

        parts = []
        if days > 0:
            parts.append(f"{days} дн.")
        if hours > 0:
            parts.append(f"{hours} ч.")
        if minutes > 0:
            parts.append(f"{minutes} мин.")

        return " ".join(parts) if parts else "Несколько минут"
    except Exception:
        return "Время неизвестно"