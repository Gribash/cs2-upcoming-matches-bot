import os
import json
from datetime import datetime, timezone
from typing import List, Literal

# Пути к кэш-файлам
MATCH_CACHE_FILE = "cache/matches.json"
TOURNAMENT_CACHE_FILE = "cache/tournaments.json"

# Допустимые tier-группы
TIER_SA = ["s", "a"]
TIER_ALL = ["s", "a", "b", "c", "d"]

# Тип статуса матчей
MatchStatus = Literal["upcoming", "live", "past"]

def _load_matches_from_cache() -> List[dict]:
    if not os.path.exists(MATCH_CACHE_FILE):
        return []
    with open(MATCH_CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("data", [])

def _load_tournaments_from_cache() -> List[dict]:
    if not os.path.exists(TOURNAMENT_CACHE_FILE):
        return []
    with open(TOURNAMENT_CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_matches(status: MatchStatus, tier: Literal["sa", "all"], limit: int = 10) -> List[dict]:
    """
    Возвращает отфильтрованные матчи из кэша по статусу и tier.
    """
    matches = _load_matches_from_cache()
    tournaments = _load_tournaments_from_cache()
    now = datetime.now(timezone.utc)

    # Фильтруем турниры по уровню
    allowed_tiers = TIER_SA if tier == "sa" else TIER_ALL
    allowed_tournament_ids = {
        t["id"] for t in tournaments if t.get("tier", "").lower() in allowed_tiers
    }

    filtered = []

    for match in matches:
        begin_at = match.get("begin_at")
        tournament_id = match.get("tournament_id")
        match_status = match.get("status")

        # Пропускаем если нет времени начала или турнир не в разрешённом списке
        if not begin_at or tournament_id not in allowed_tournament_ids:
            continue

        try:
            start_time = datetime.fromisoformat(begin_at.replace("Z", "+00:00"))
        except Exception:
            continue

        if status == "upcoming" and start_time > now:
            filtered.append(match)
        elif status == "live" and match_status == "running":
            filtered.append(match)
        elif status == "past" and start_time < now:
            filtered.append(match)

    # Сортировка
    reverse = (status == "past")
    filtered.sort(key=lambda m: m["begin_at"], reverse=reverse)

    return filtered[:limit]