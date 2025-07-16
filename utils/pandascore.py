import os
import logging
import httpx
import re
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

PANDASCORE_TOKEN = os.getenv("PANDASCORE_TOKEN")
BASE_URL = "https://api.pandascore.co"
HEADERS = {
    "Authorization": f"Bearer {PANDASCORE_TOKEN}"
}

logger = logging.getLogger("tournaments")

TIERS = ["s", "a", "b", "c", "d"]
TIERS_QUERY = ",".join(TIERS)

def extract_stream_url(streams_list: list) -> str | None:
    if not isinstance(streams_list, list):
        return None

    for stream in streams_list:
        if isinstance(stream, dict) and stream.get("main") and stream.get("raw_url"):
            return stream["raw_url"]

    for stream in streams_list:
        if isinstance(stream, dict) and stream.get("raw_url"):
            return stream["raw_url"]

    return None

def match_teams_by_acronym(match_name: str, teams: list[dict]) -> tuple[dict, dict]:
    if not match_name or "vs" not in match_name.lower():
        return {}, {}

    try:
        # Убираем всё перед "vs", если есть двоеточие
        clean_name = re.split(r":\s*", match_name)[-1]
        parts = [p.strip().lower() for p in clean_name.split("vs")]
        if len(parts) != 2:
            return {}, {}

        acronym_1, acronym_2 = parts
    except Exception:
        return {}, {}

    team_1 = next((t for t in teams if (t.get("acronym") or "").lower() == acronym_1), {})
    team_2 = next((t for t in teams if (t.get("acronym") or "").lower() == acronym_2), {})
    return team_1, team_2

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

                    matches = []
                    for m in matches_raw:
                        stream_url = extract_stream_url(m.get("streams_list", []))
                        name = m.get("name", "")
                        team_1, team_2 = match_teams_by_acronym(name, teams)

                        if not team_1 or not team_2:
                            logger.warning(f"❗ Не удалось сопоставить команды для матча {name} (ID: {m['id']})")

                        matches.append({
                            "id": m["id"],
                            "name": name,
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

                    tournaments.append({
                        "id": t["id"],
                        "name": t.get("name"),
                        "tier": t.get("tier", "unknown"),
                        "status": t.get("status", endpoint),
                        "begin_at": t.get("begin_at"),
                        "end_at": t.get("end_at"),
                        "region": t.get("region"),
                        "league": league.get("name"),
                        "serie": serie.get("full_name"),
                        "teams": [
                            {
                                "id": team.get("id"),
                                "name": team.get("name"),
                                "acronym": team.get("acronym")
                            }
                            for team in teams
                        ],
                        "matches": matches
                    })

                page += 1

    logger.info(f"✅ Загружено {len(tournaments)} турниров с матчами, командами, лигами и сериями")
    return tournaments