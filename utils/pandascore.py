import os
import logging
import httpx
from dotenv import load_dotenv
from datetime import datetime, timezone
from utils.logging_config import setup_logging
from utils.translations import t

load_dotenv()

PANDASCORE_TOKEN = os.getenv("PANDASCORE_TOKEN")
BASE_URL = "https://api.pandascore.co"
HEADERS = {
    "Authorization": f"Bearer {PANDASCORE_TOKEN}"
}

setup_logging()
logger = logging.getLogger("pandascore")

def process_match(match: dict) -> dict:
    opponents = []
    for opponent in match.get("opponents", []):
        team = opponent.get("opponent", {})
        opponents.append({
            "id": team.get("id"),
            "name": team.get("name"),
            "acronym": team.get("acronym"),
            "image_url": team.get("image_url")
        })

    streams = match.get("streams_list", [])
    main_stream = next((s for s in streams if s.get("main")), None)
    stream_url = main_stream.get("raw_url") if main_stream else None

    return {
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
    }


async def fetch_all_matches() -> dict:
    all_matches = []
    endpoints = ["running", "upcoming", "past"]

    async with httpx.AsyncClient(timeout=10) as client:
        for endpoint in endpoints:
            url = f"{BASE_URL}/csgo/matches/{endpoint}"
            try:
                response = await client.get(url, headers=HEADERS)
                response.raise_for_status()
                raw_matches = response.json()
                processed = [process_match(m) for m in raw_matches]
                all_matches.extend(processed)
                logger.info(f"✅ Загружено {len(processed)} матчей из {endpoint}")
            except Exception as e:
                logger.warning(f"❌ Ошибка при загрузке матчей ({endpoint}): {e}")

    return {
        "matches": all_matches,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }


def format_time_until(start_time_iso: str, lang: str = "en") -> str:
    try:
        start_time = datetime.fromisoformat(start_time_iso.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = start_time - now

        if delta.total_seconds() < 0:
            return t("already_started", lang)

        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes = remainder // 60

        parts = []
        if days > 0:
            parts.append(f"{days} {t('day_short', lang)}")
        if hours > 0:
            parts.append(f"{hours} {t('hour_short', lang)}")
        if minutes > 0:
            parts.append(f"{minutes} {t('minute_short', lang)}")

        return " ".join(parts) if parts else t("few_minutes", lang)
    except Exception:
        return t("unknown_time", lang)