import os
import logging
import httpx
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

PANDASCORE_TOKEN = os.getenv("PANDASCORE_TOKEN")
BASE_URL = "https://api.pandascore.co"
HEADERS = {
    "Authorization": f"Bearer {PANDASCORE_TOKEN}"
}

logger = logging.getLogger("matches")

async def fetch_all_matches() -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{BASE_URL}/csgo/matches/running", headers=HEADERS)
        response.raise_for_status()
        raw_matches = response.json()

    matches = []

    for match in raw_matches:
        # Упрощаем opponents
        opponents = []
        for opponent in match.get("opponents", []):
            team = opponent.get("opponent")
            opponents.append({
                "id": team.get("id"),
                "name": team.get("name"),
                "acronym": team.get("acronym"),
                "image_url": team.get("image_url")
            })

        # Ищем главный стрим
        streams = match.get("streams_list", [])
        main_stream = next((s for s in streams if s.get("main")), None)
        stream_url = main_stream.get("raw_url") if main_stream else None

        # Формируем словарь
        matches.append({
            "id": match["id"],
            "name": match["name"],
            "status": match["status"],
            "begin_at": match["begin_at"],
            "scheduled_at": match.get("scheduled_at"),
            "end_at": match.get("end_at"),
            "modified_at": match.get("modified_at"),
            "number_of_games": match.get("number_of_games"),
            "results": match.get("results", []),
            "winner_id": match.get("winner_id"),
            "opponents": opponents,
            "stream_url": stream_url,
            "league": {
                "id": match["league"]["id"],
                "name": match["league"]["name"],
                "image_url": match["league"].get("image_url")
            },
            "tournament": {
                "id": match["tournament"]["id"],
                "name": match["tournament"]["name"],
                "tier": match["tournament"].get("tier"),
                "region": match["tournament"].get("region")
            },
            "serie": {
                "season": match["serie"].get("season"),
                "full_name": match["serie"].get("full_name"),
                "year": match["serie"].get("year")
            }
        })

    return {
        "matches": matches,
        "updated_at": datetime.now(timezone.utc).isoformat()
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

        return " ".join(parts) if parts else "Несколько минут"
    except Exception:
        return "Время неизвестно"