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
MatchStatus = Literal["running", "finished", "not_started"]

import json
import os
import logging

logger = logging.getLogger("match_reader")

def load_matches_from_cache(cache_path="cache/matches.json"):
    if not os.path.exists(cache_path):
        logger.warning(f"⚠️ Файл кэша матчей {cache_path} не найден")
        return []

    if os.path.getsize(cache_path) == 0:
        logger.warning(f"⚠️ Файл кэша матчей {cache_path} пуст")
        return []

    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке JSON из {cache_path}: {e}")
        return []

def load_tournaments_from_cache(cache_path="cache/tournaments.json"):
    if not os.path.exists(cache_path):
        logger.warning(f"⚠️ Файл кэша турниров {cache_path} не найден")
        return []

    if os.path.getsize(cache_path) == 0:
        logger.warning(f"⚠️ Файл кэша турниров {cache_path} пуст")
        return []

    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке JSON из {cache_path}: {e}")
        return []

# Получает список матчей из кэша по статусу и tier

def get_matches(status: MatchStatus, tier: Literal["sa", "all"], limit: int = 10) -> List[dict]:
    matches = load_matches_from_cache()
    tournaments = load_tournaments_from_cache()
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

        if status == "not_started" and start_time > now:
            filtered.append(match)
        elif status == "running" and match_status == "running":
            filtered.append(match)
        elif status == "finished" and start_time < now:
            filtered.append(match)

    # Сортировка
    reverse = (status == "finished")
    filtered.sort(key=lambda m: m["begin_at"], reverse=reverse)

    return filtered[:limit]