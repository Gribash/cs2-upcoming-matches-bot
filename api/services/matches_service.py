from typing import List

from utils.matches_cache_reader import get_matches as read_matches


def _tier_param_to_internal(tier: str) -> str:
    # API exposes: '1' | 'all'. Internal utils expect 'all' or tier by letters.
    return "all" if tier == "all" else "sa"  # temporary heuristic: Tier1 ~= S/A


def get_matches(status: str, tier: str, limit: int) -> List[dict]:
    internal_tier = _tier_param_to_internal(tier)
    # Map status to existing reader statuses: upcoming, running, past
    mapped_status = status
    return read_matches(status=mapped_status, tier=("all" if internal_tier == "all" else "s"), limit=limit)


