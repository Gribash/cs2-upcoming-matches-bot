import os
import json
import logging
from datetime import datetime, timezone
from typing import List

from utils.cache_writer import read_json_from_cache, MATCHES_CACHE_NAME
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("matches_cache_reader")

TIER_SA = {"s", "a"}

def get_matches(status: str, tier: str = "all", limit: int = 10) -> List[dict]:
    cache_data = read_json_from_cache(MATCHES_CACHE_NAME)

    if not isinstance(cache_data, dict):
        logger.error(f"❌ Кэш {MATCHES_CACHE_NAME} имеет неверный формат: ожидался словарь.")
        return []

    all_matches = cache_data.get("matches", [])
    if not isinstance(all_matches, list):
        logger.error(f"❌ Кэш {MATCHES_CACHE_NAME}['matches'] не является списком.")
        return []

    now = datetime.now(timezone.utc)

    def match_status_filter(match: dict) -> bool:
        begin_at_str = match.get("begin_at")
        if not begin_at_str:
            return False

        try:
            begin_at = datetime.fromisoformat(begin_at_str.replace("Z", "+00:00"))
        except ValueError:
            logger.warning(f"⚠️ Невозможно распарсить дату: {begin_at_str}")
            return False

        if status == "running":
            return match.get("status") == "running"
        elif status == "upcoming":
            return begin_at > now
        elif status == "past":
            return begin_at < now and match.get("status") != "running"
        else:
            return False

    def tier_filter(match: dict) -> bool:
        if tier == "all":
            return True
        match_tier = match.get("tournament", {}).get("tier", "").lower()
        return match_tier in TIER_SA

    try:
        filtered_matches = [
            m for m in all_matches if match_status_filter(m) and tier_filter(m)
        ]

        filtered_matches.sort(
            key=lambda m: m.get("begin_at") or "",
            reverse=(status == "past")
        )

        logger.info(f"📊 Получено {len(filtered_matches)} матчей по фильтрам: status={status}, tier={tier}")
        return filtered_matches[:limit]

    except Exception as e:
        logger.exception(f"🔥 Ошибка при фильтрации матчей: {e}")
        return []