import os
import json
from typing import List, Literal

TOURNAMENT_CACHE_FILE = "cache/tournaments.json"

# Уровни турниров
TIER_SA = ["s", "a"]
TIER_ALL = ["s", "a", "b", "c", "d"]

def load_tournaments_from_cache() -> List[dict]:
    if not os.path.exists(TOURNAMENT_CACHE_FILE):
        return []
    with open(TOURNAMENT_CACHE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("tournaments", [])

# Получаем список турниров из кэша по tier и статусу
def get_tournaments(tier: Literal["sa", "all"] = "all", status_filter: List[str] = None) -> List[dict]:
    tournaments = load_tournaments_from_cache()
    
    allowed_tiers = TIER_SA if tier == "sa" else TIER_ALL
    allowed_tiers = [t.lower() for t in allowed_tiers]

    filtered = []
    for t in tournaments:
        t_tier = t.get("tier", "").lower()
        t_status = t.get("status", "").lower()
        
        if t_tier not in allowed_tiers:
            continue

        if status_filter and t_status not in status_filter:
            continue

        filtered.append(t)

    return filtered

def get_tournament_name_by_id(tournament_id: int) -> str | None:
    tournaments = load_tournaments_from_cache()
    for t in tournaments:
        if t.get("id") == tournament_id:
            return t.get("name")
    return None

def get_matches_from_cache(
    tier: Literal["sa", "all"] = "all",
    status: Literal["upcoming", "live", "finished"] = "upcoming",
    limit: int = 10
) -> List[dict]:
    tournaments = get_tournaments(tier=tier, status_filter=None)
    matches = []

    for t in tournaments:
        for match in t.get("matches", []):
            if match.get("status") == status:
                matches.append(match)

    # Сортировка по begin_at
    matches = [
        m for m in matches
        if m.get("begin_at")
    ]
    matches.sort(key=lambda m: m["begin_at"])

    return matches[:limit]

from datetime import datetime
from typing import Literal

def get_upcoming_matches(tier: Literal["sa", "all"] = "all", limit: int = 5) -> List[dict]:
    tournaments = get_tournaments(tier=tier)
    matches = []

    for t in tournaments:
        for m in t.get("matches", []):
            if m.get("status") == "upcoming" and m.get("begin_at"):
                matches.append((m, m["begin_at"]))

    matches.sort(key=lambda x: x[1])
    return [m[0] for m in matches[:limit]]

def get_live_matches(tier: Literal["sa", "all"] = "all", limit: int = 5) -> List[dict]:
    tournaments = get_tournaments(tier=tier)
    matches = []

    for t in tournaments:
        for m in t.get("matches", []):
            if m.get("status") == "running":
                matches.append(m)

    return matches[:limit]

def get_recent_matches(tier: Literal["sa", "all"] = "all", limit: int = 5) -> List[dict]:
    tournaments = get_tournaments(tier=tier)
    matches = []

    for t in tournaments:
        for m in t.get("matches", []):
            if m.get("status") == "finished" and m.get("begin_at"):
                matches.append((m, m["begin_at"]))

    matches.sort(key=lambda x: x[1], reverse=True)
    return [m[0] for m in matches[:limit]]