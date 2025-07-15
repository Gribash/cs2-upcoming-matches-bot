import os
import logging
import httpx
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

PANDASCORE_TOKEN = os.getenv("PANDASCORE_TOKEN")
BASE_URL = "https://api.pandascore.co"
HEADERS = {
    "Authorization": f"Bearer {PANDASCORE_TOKEN}"
}

logger = logging.getLogger("tournaments")

# Загружаем все турниры и фильтруем нужные поля.
# Используется в tournament_cacher.py

# Тиры, которые нам нужны
TIERS = ["s", "a", "b", "c", "d"]
TIERS_QUERY = ",".join(TIERS)

async def fetch_all_tournaments():
    tournaments = []
    endpoints = ["running", "upcoming"]

    async with httpx.AsyncClient(timeout=30.0) as client:
        for endpoint in endpoints:
            page = 1
            while True:
                url = (
                    f"{BASE_URL}/tournaments/{endpoint}"
                    f"?page={page}&per_page=100"
                    f"&filter[tier]={TIERS_QUERY}"
                )
                logger.debug(f"📡 Запрос: {url}")
                r = await client.get(url, headers=HEADERS)

                if r.status_code != 200:
                    logger.warning(f"⚠️ Ошибка при запросе {endpoint} (стр. {page}): {r.status_code}")
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
                        "status": t.get("status", endpoint),  # либо running, либо upcoming
                        "begin_at": t.get("begin_at"),
                        "end_at": t.get("end_at")
                    })

                page += 1

    logger.info(f"✅ Загружено {len(tournaments)} турниров (running + upcoming) с фильтром по tier")
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
                "sort": "begin_at",
                "include": "streams_list"
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

def extract_stream_url(streams_list: list) -> str | None:
    if not isinstance(streams_list, list):
        return None

    # Сначала ищем официальную основную трансляцию
    for stream in streams_list:
        if isinstance(stream, dict) and stream.get("main") and stream.get("raw_url"):
            return stream["raw_url"]

    # Затем — просто первую с raw_url
    for stream in streams_list:
        if isinstance(stream, dict) and stream.get("raw_url"):
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