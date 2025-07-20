import pytest
from datetime import datetime, timedelta, timezone
from utils.matches_cache_reader import get_matches, TIER_SA
from utils.cache_writer import write_json_to_cache

@pytest.fixture
def sample_matches():
    now = datetime.now(timezone.utc)
    return {
        "matches": [
            {
                "id": 1,
                "begin_at": (now + timedelta(minutes=20)).isoformat(),
                "status": "not_started",
                "tournament": {"tier": "s"},
            },
            {
                "id": 2,
                "begin_at": (now - timedelta(minutes=10)).isoformat(),
                "status": "finished",
                "tournament": {"tier": "a"},
            },
            {
                "id": 3,
                "begin_at": (now.isoformat()),
                "status": "running",
                "tournament": {"tier": "b"},
            },
            {
                "id": 4,
                "begin_at": "invalid-date",
                "status": "upcoming",
                "tournament": {"tier": "s"},
            },
        ]
    }

def test_upcoming_matches_filtering(sample_matches):
    write_json_to_cache("matches", sample_matches)
    results = get_matches(status="upcoming", tier="sa", limit=10)
    assert any(match["id"] == 1 for match in results)
    assert all(match["tournament"]["tier"].lower() in TIER_SA for match in results)

def test_past_matches_filtering(sample_matches):
    write_json_to_cache("matches", sample_matches)
    results = get_matches(status="past", tier="all", limit=10)
    assert any(match["id"] == 2 for match in results)
    assert all(match["status"] != "running" for match in results)

def test_running_matches_filtering(sample_matches):
    write_json_to_cache("matches", sample_matches)
    results = get_matches(status="running", tier="all", limit=10)
    assert any(match["id"] == 3 for match in results)
    assert all(match["status"] == "running" for match in results)

def test_tier_all_accepts_any(sample_matches):
    sample_matches["matches"][0]["tournament"]["tier"] = "C"
    write_json_to_cache("matches", sample_matches)
    results = get_matches(status="upcoming", tier="all", limit=10)
    assert any(match["id"] == 1 for match in results)

def test_invalid_date_skipped(caplog):
    from utils.matches_cache_reader import get_matches
    import logging

    invalid_match = {
        "id": 9999,
        "begin_at": "not-a-date",
        "status": "not_started",
        "tournament": {"tier": "s"},
    }

    matches_data = {
        "matches": [invalid_match]
    }

    from utils.cache_writer import write_json_to_cache
    write_json_to_cache("matches", matches_data)

    caplog.set_level(logging.WARNING)
    result = get_matches(status="upcoming", tier="sa", limit=5)

    assert all("9999" not in str(m.get("id", "")) for m in result)
    assert "Ошибка разбора даты матча" in caplog.text