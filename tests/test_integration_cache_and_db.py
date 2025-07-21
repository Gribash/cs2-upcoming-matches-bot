import sys
import os
import pytest
from datetime import datetime, timedelta, timezone

# Добавляем корень проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot.db import (
    get_all_subscribers,
    mark_notified_bulk,
    get_notified_match_ids,
    get_subscriber_tier
)
from utils.matches_cache_reader import get_matches
from utils.cache_writer import write_json_to_cache


@pytest.fixture
def sample_cache(monkeypatch, tmp_path):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    monkeypatch.setattr("utils.cache_writer.CACHE_DIR", str(cache_dir))
    monkeypatch.setattr("utils.matches_cache_reader.CACHE_DIR", str(cache_dir))
    return cache_dir


# --- Тесты БД ---
def test_get_all_subscribers():
    subscribers = get_all_subscribers()
    assert isinstance(subscribers, list)
    for sub in subscribers:
        assert isinstance(sub, int)


def test_mark_notified_bulk():
    test_user_id = 999999
    test_match_id = 888888
    mark_notified_bulk([(test_user_id, test_match_id)])
    notified = get_notified_match_ids(test_user_id)
    assert test_match_id in notified


def test_get_subscriber_tier():
    test_user_id = 999999
    tier = get_subscriber_tier(test_user_id)
    assert tier in ["sa", "all", None]


# --- Тесты кэша ---
def test_get_matches_structure(sample_cache):
    matches_data = {
        "matches": [
            {
                "id": 1,
                "begin_at": datetime.now(timezone.utc).isoformat(),
                "status": "not_started",
                "tournament": {"tier": "a"}
            }
        ]
    }
    write_json_to_cache("matches", matches_data)
    matches = get_matches(status="upcoming", tier="all", limit=5)
    assert isinstance(matches, list)
    for match in matches:
        assert isinstance(match, dict)
        assert "id" in match
        assert "begin_at" in match
        assert "status" in match


def test_match_filtering_logic(sample_cache):
    now = datetime.now(timezone.utc)
    matches_data = {
        "matches": [
            {
                "id": 1,
                "begin_at": (now + timedelta(minutes=10)).isoformat(),
                "status": "not_started",
                "tournament": {"tier": "s"}
            },
            {
                "id": 2,
                "begin_at": (now - timedelta(minutes=10)).isoformat(),
                "status": "finished",
                "tournament": {"tier": "a"}
            },
            {
                "id": 3,
                "begin_at": now.isoformat(),
                "status": "running",
                "tournament": {"tier": "a"}
            },
            {
                "id": 4,
                "begin_at": (now + timedelta(minutes=20)).isoformat(),
                "status": "not_started",
                "tournament": {"tier": "c"}
            },
        ]
    }

    write_json_to_cache("matches", matches_data)

    upcoming = get_matches(status="upcoming", tier="sa", limit=10)
    assert any(m["id"] == 1 for m in upcoming)
    assert all(m["tournament"]["tier"].lower() in ["s", "a"] for m in upcoming)

    past = get_matches(status="past", tier="all", limit=10)
    assert any(m["id"] == 2 for m in past)

    running = get_matches(status="running", tier="all", limit=10)
    assert any(m["id"] == 3 for m in running)
    assert all(m["status"] == "running" for m in running)