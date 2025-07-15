import os
import json
import logging
from datetime import datetime, timezone
from typing import List, Literal

# Пути к кэш-файлам
MATCH_CACHE_FILE = "cache/matches.json"
TOURNAMENT_CACHE_FILE = "cache/tournaments.json"

# Допустимые tier-группы
TIER_SA = ["s", "a"]
TIER_ALL = ["s", "a", "b", "c", "d"]

# Тип статуса матчей
MatchStatus = Literal["live", "past", "upcoming"]

logger = logging.getLogger("match_reader")

def load_matches_from_cache(cache_path: str = MATCH_CACHE_FILE) -> List[dict]:
    if not os.path.exists(cache_path):
        logger.warning(f"⚠️ Файл кэша матчей {cache_path} не найден")
        return []

    if os.path.getsize(cache_path) == 0:
        logger.warning(f"⚠️ Файл кэша матчей {cache_path} пуст")
        return []

    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("matches", [])
    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке JSON из {cache_path}: {e}")
        return []

def load_tournaments_from_cache(cache_path: str = TOURNAMENT_CACHE_FILE) -> List[dict]:
    if not os.path.exists(cache_path):
        logger.warning(f"⚠️ Файл кэша турниров {cache_path} не найден")
        return []

    if os.path.getsize(cache_path) == 0:
        logger.warning(f"⚠️ Файл кэша турниров {cache_path} пуст")
        return []

    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("tournaments", [])
    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке JSON из {cache_path}: {e}")
        return []

def get_matches(status: MatchStatus, tier: Literal["sa", "all"], limit: int = 10) -> List[dict]:
    matches = load_matches_from_cache()
    tournaments = load_tournaments_from_cache()
    now = datetime.now(timezone.utc)

    allowed_tiers = TIER_SA if tier == "sa" else TIER_ALL
    allowed_tournament_ids = {
        t["id"] for t in tournaments if isinstance(t, dict) and t.get("tier", "").lower() in allowed_tiers
    }

    filtered = []

    for match in matches:
        begin_at = match.get("begin_at")
        match_status = match.get("status")
        tournament_id = match.get("tournament_id")

        if not begin_at or tournament_id not in allowed_tournament_ids:
            continue

        try:
            start_time = datetime.fromisoformat(begin_at.replace("Z", "+00:00"))
        except Exception:
            continue

        # 🧠 Ручное определение статуса
        if status == "live" and match_status == "running":
            filtered.append(match)
        elif status == "upcoming" and match_status == "not_started" and start_time > now:
            filtered.append(match)
        elif status == "past" and match_status == "finished":
            filtered.append(match)

    reverse = (status == "past")
    filtered.sort(key=lambda m: m.get("begin_at") or "", reverse=reverse)

    return filtered[:limit]