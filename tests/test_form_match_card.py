import pytest
from telegram import InlineKeyboardMarkup
from utils.form_match_card import build_match_card


@pytest.fixture
def basic_match():
    return {
        "id": 123,
        "league": {"name": "ESL"},
        "tournament": {"name": "Pro League"},
        "serie": {"full_name": "Season 20"},
        "opponents": [
            {"id": 1, "name": "Team A"},
            {"id": 2, "name": "Team B"}
        ],
        "status": "upcoming",
        "begin_at": "2099-12-31T15:00:00Z",
        "stream_url": "http://example.com/stream"
    }


def test_build_card_basic(basic_match):
    message, keyboard = build_match_card(basic_match, stream_button=True)
    assert "Team A vs Team B" in message
    assert isinstance(keyboard, InlineKeyboardMarkup)


def test_show_time_until(basic_match, monkeypatch):
    monkeypatch.setattr("utils.form_match_card.format_time_until", lambda dt, lang: "через 1 час")
    message, _ = build_match_card(basic_match, show_time_until=True, lang="ru")
    assert "Начнётся через:" in message
    assert "через 1 час" in message


def test_show_winner(basic_match):
    basic_match["status"] = "finished"
    basic_match["winner_id"] = 1
    message, _ = build_match_card(basic_match, show_winner=True, lang="ru")
    assert "🏆 Победитель:" in message
    assert "Team A" in message


def test_missing_stream(basic_match):
    basic_match["stream_url"] = None
    message, keyboard = build_match_card(basic_match, stream_button=True, lang="ru")
    assert keyboard is None
    assert "Трансляция отсутствует" in message


def test_fallback_fields():
    incomplete_match = {
        "opponents": [],
        "status": "upcoming"
    }
    message, keyboard = build_match_card(incomplete_match, lang="ru")
    assert "Team1 vs Team2" in message
    assert "?" in message