import os
import logging
import httpx
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

PANDASCORE_TOKEN = os.getenv("PANDASCORE_TOKEN")
BASE_URL = "https://api.pandascore.co"
HEADERS = {
    "Authorization": f"Bearer {PANDASCORE_TOKEN}"
}

logger = logging.getLogger("tournaments")

TIERS = ["s", "a", "b", "c", "d"]
TIERS_QUERY = ",".join(TIERS)

async def fetch_all_tournaments():
    tournaments = []
    endpoints = ["running", "upcoming"]
    includes = "matches,teams,league,serie"

    async with httpx.AsyncClient(timeout=30.0) as client:
        for endpoint in endpoints:
            page = 1
            while True:
                url = (
                    f"{BASE_URL}/csgo/tournaments/{endpoint}"
                    f"?page={page}&per_page=100"
                    f"&filter[tier]={TIERS_QUERY}"
                    f"&include={includes}"
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
                    league = t.get("league") or {}
                    serie = t.get("serie") or {}
                    teams = t.get("teams", [])
                    matches_raw = t.get("matches", [])

                    # 🧠 Новый код — сопоставляем команды
                    # 🧠 Новый код — сопоставляем команды по ID
                    teams_by_id = {team["id"]: team for team in teams if team.get("id")}

                    matches = []
                    for m in matches_raw:
                        stream_url = extract_stream_url(m.get("streams_list", []))
                        opponents = m.get("opponents", [])

                        team_1 = {}
                        team_2 = {}

                        # Оппонент 1
                        if len(opponents) > 0 and isinstance(opponents[0], dict):
                            opp1 = opponents[0].get("opponent")
                            if isinstance(opp1, dict):
                                team_1 = teams_by_id.get(opp1.get("id"), {})

                        # Оппонент 2
                        if len(opponents) > 1 and isinstance(opponents[1], dict):
                            opp2 = opponents[1].get("opponent")
                            if isinstance(opp2, dict):
                                team_2 = teams_by_id.get(opp2.get("id"), {})

                        # 🔍 Логируем несопоставленные команды
                        if not team_1 or not team_2:
                            logger.warning(f"❗ Не удалось сопоставить команды для матча {m.get('name')} (ID: {m.get('id')})")

                        matches.append({
                            "id": m["id"],
                            "name": m.get("name"),
                            "status": m.get("status"),
                            "begin_at": m.get("begin_at"),
                            "scheduled_at": m.get("scheduled_at"),
                            "stream_url": stream_url,
                            "team_1": {
                                "id": team_1.get("id"),
                                "name": team_1.get("name"),
                                "acronym": team_1.get("acronym")
                            },
                            "team_2": {
                                "id": team_2.get("id"),
                                "name": team_2.get("name"),
                                "acronym": team_2.get("acronym")
                            }
                        })

                page += 1

    logger.info(f"✅ Загружено {len(tournaments)} турниров с матчами, командами, лигами и сериями")
    return tournaments

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