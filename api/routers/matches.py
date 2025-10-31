from typing import List

from fastapi import APIRouter, Query, Depends

from api.services import matches_service
from api.core.rate_limit import rate_limit_dependency


router = APIRouter(prefix="/matches", tags=["matches"]) 


@router.get("/upcoming", dependencies=[Depends(rate_limit_dependency)])
def upcoming_matches(tier: str = Query(default="1", pattern="^(1|all)$"), limit: int = Query(default=50, ge=1, le=200)):
    return matches_service.get_matches(status="upcoming", tier=tier, limit=limit)


@router.get("/live", dependencies=[Depends(rate_limit_dependency)])
def live_matches(tier: str = Query(default="1", pattern="^(1|all)$"), limit: int = Query(default=50, ge=1, le=200)):
    return matches_service.get_matches(status="running", tier=tier, limit=limit)


@router.get("/recent", dependencies=[Depends(rate_limit_dependency)])
def recent_matches(tier: str = Query(default="1", pattern="^(1|all)$"), limit: int = Query(default=50, ge=1, le=200)):
    return matches_service.get_matches(status="past", tier=tier, limit=limit)


