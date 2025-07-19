import os
import json
import logging
from datetime import datetime, timezone
from typing import List

from utils.cache_writer import read_json_from_cache, MATCHES_CACHE_NAME
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("match_cache_reader")

TIER_SA = {"s", "a"}

def get_matches(status: str, tier: str = "all", limit: int = 10) -> List[dict]:
    cache_data = read_json_from_cache(MATCHES_CACHE_NAME)
    if not cache_data:
        logger.warning("Кэш матчей не найден или повреждён")
        return []

    all_matches = cache_data.get("matches", [])
    now = datetime.now(timezone.utc)

    def match_status_filter(match: dict) -> bool:
        begin_at_str = match.get("begin_at")
        if not begin_at_str:
            return False

        try:
            begin_at = datetime.fromisoformat(begin_at_str)
        except ValueError:
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
        match_tier = match.get("tournament", {}).get("tier")
        return match_tier in TIER_SA

    filtered_matches = [
        m for m in all_matches if match_status_filter(m) and tier_filter(m)
    ]

    filtered_matches.sort(
        key=lambda m: m.get("begin_at") or "",
        reverse=(status == "past")
    )

    return filtered_matches[:limit]