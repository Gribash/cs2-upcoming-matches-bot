import os
import logging
import time
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import httpx

load_dotenv()

PANDASCORE_TOKEN = os.getenv("PANDASCORE_TOKEN")
BASE_URL = "https://api.pandascore.co"
HEADERS = {
    "Authorization": f"Bearer {PANDASCORE_TOKEN}"
}

logger = logging.getLogger(__name__)

# Кэш для турниров
_tournament_cache = {
    "data": [],
    "timestamp": 0
}

# Карта уровней турниров по подписке
TIER_MAP = {
    "sa": ["S", "A"],
    "all": ["S", "A", "B", "C", "D"]
}

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

        return "Начнётся через " + " ".join(parts) if parts else "Скоро"
    except Exception:
        return "время неизвестно"

def extract_stream_url(streams_list: list) -> str:
    if not streams_list:
        return "Трансляция недоступна"

    for stream in streams_list:
        if stream.get("main") is True:
            return stream.get("raw_url", "Трансляция недоступна")

    for stream in streams_list:
        if "raw_url" in stream and stream["raw_url"]:
            return stream["raw_url"]

    return "Трансляция недоступна"

async def get_top_tournament_ids(tiers=["S", "A", "B", "C", "D"], limit=50, ttl_seconds=3600):
    now = time.time()
    if now - _tournament_cache["timestamp"] < ttl_seconds:
        logger.info(f"Используем кэш: {_tournament_cache['data']}")
        return _tournament_cache["data"]

    all_ids = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        for status in ["running", "upcoming"]:
            url = f"{BASE_URL}/csgo/tournaments/{status}"
            params = {
                "filter[tier]": ",".join(tiers).lower(),
                "per_page": limit
            }

            try:
                logger.info(f"Запрос турниров: {url} с params: {params}")
                response = await client.get(url, headers=HEADERS, params=params)
                response.raise_for_status()
                tournaments = response.json()
                ids = [t["id"] for t in tournaments]
                all_ids.extend(ids)
                logger.info(f"Получено {len(tournaments)} турниров со статусом '{status}': {[{'id': t['id'], 'name': t.get('name'), 'tier': t.get('tier')} for t in tournaments]}")
            except httpx.HTTPStatusError as e:
                logger.error(f"[Ошибка {e.response.status_code}] {e.request.url}")
            except httpx.RequestError as e:
                logger.error(f"[Ошибка подключения к {url}] {e}")

    _tournament_cache["data"] = all_ids
    _tournament_cache["timestamp"] = now
    return all_ids

async def get_upcoming_cs2_matches(limit=5, tier="sa"):
    tiers = TIER_MAP.get(tier, ["S", "A"])
    tournament_ids = await get_top_tournament_ids(tiers=tiers)
    if not tournament_ids:
        logger.error("Не удалось получить ID турниров.")
        return []

    url = f"{BASE_URL}/csgo/matches/upcoming"
    params = {
        #"filter[tournament_id]": ",".join(map(str, tournament_ids)),
        "sort": "begin_at",
        "per_page": limit
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            matches = response.json()

        logger.info(f"Успешно получено {len(matches)} предстоящих матчей CS2")
        result = []
        for match in matches:
            teams = " vs ".join(
                [t["opponent"]["name"] for t in match.get("opponents", []) if t.get("opponent")]
            ) or "TBD"
            stream_url = extract_stream_url(match.get("streams_list", []))

            formatted = {
                "id": match["id"],
                "name": match.get("name", teams),
                "teams": teams,
                "begin_at": match.get("begin_at"),
                "time_until": format_time_until(match.get("begin_at", "")),
                "league": match.get("league", {}).get("name", "Неизвестная лига"),
                "tournament": match.get("tournament", {}).get("name", "Неизвестный турнир"),
                "stream_url": stream_url
            }
            result.append(formatted)

        logger.debug(f"Список матчей к возврату: {result}")
        return result

    except httpx.RequestError as e:
        logger.error(f"[Ошибка получения предстоящих матчей] {e}")
        return []

async def get_live_cs2_matches(tier="sa"):
    tiers = TIER_MAP.get(tier, ["S", "A"])
    tournament_ids = await get_top_tournament_ids(tiers=tiers)
    if not tournament_ids:
        logger.warning("Не удалось получить турниры для live матчей.")
        return []

    url = f"{BASE_URL}/csgo/matches/running"
    params = {
        "filter[tournament_id]": ",".join(map(str, tournament_ids)),
        "per_page": 10,
        "sort": "begin_at"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            matches = response.json()

        logger.info(f"Успешно получено {len(matches)} live матчей CS2")

        result = [
            {
                "id": match["id"],
                "name": match.get("name", ""),
                "teams": " vs ".join(
                    [t["opponent"]["name"] for t in match.get("opponents", []) if t.get("opponent")]
                ) or "TBD",
                "league": match.get("league", {}).get("name", "Неизвестная лига"),
                "tournament": match.get("tournament", {}).get("name", "Неизвестный турнир"),
                "stream_url": extract_stream_url(match.get("streams_list", []))
            }
            for match in matches
        ]
        logger.debug(f"Live матчи: {result}")
        return result

    except httpx.RequestError as e:
        logger.error(f"[Ошибка получения live матчей] {e}")
        return []

async def get_recent_cs2_matches(limit=5, tier="sa"):
    url = f"{BASE_URL}/csgo/matches/past"
    params = {
        "per_page": limit,
        "sort": "-begin_at"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            matches = response.json()

        logger.info(f"Успешно получено {len(matches)} прошедших матчей CS2")

        result = [
            {
                "id": match["id"],
                "name": match.get("name", ""),
                "teams": " vs ".join(
                    [t["opponent"]["name"] for t in match.get("opponents", []) if t.get("opponent")]
                ) or "TBD",
                "league": match.get("league", {}).get("name", "Неизвестная лига"),
                "tournament": match.get("tournament", {}).get("name", "Неизвестный турнир"),
                "winner": match["winner"]["name"] if match.get("winner") else "Неизвестно",
            }
            for match in matches
        ]
        logger.debug(f"Прошедшие матчи: {result}")
        return result

    except httpx.RequestError as e:
        logger.error(f"[Ошибка получения прошедших матчей] {e}")
        return []