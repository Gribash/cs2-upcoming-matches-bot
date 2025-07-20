import pytest
import logging
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
                "begin_at": now.isoformat(),
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
    caplog.set_level(logging.WARNING, logger="matches_cache_reader")

    invalid_match = {
        "id": 9999,
        "begin_at": "not-a-date",
        "status": "not_started",
        "tournament": {"tier": "s"},
    }

    write_json_to_cache("matches", {"matches": [invalid_match]})
    result = get_matches(status="upcoming", tier="sa", limit=5)

    assert all(m.get("id") != 9999 for m in result)
    assert any("Невозможно распарсить дату" in msg for msg in caplog.messages)