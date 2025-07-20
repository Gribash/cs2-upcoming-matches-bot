import pytest
from unittest.mock import AsyncMock, MagicMock

from utils.telegram_messenger import send_match_batch, match_team_names


@pytest.fixture
def fake_update():
    class FakeChat:
        id = 12345

    class FakeUpdate:
        effective_chat = FakeChat()

    return FakeUpdate()


@pytest.fixture
def fake_context():
    mock_context = MagicMock()
    mock_context.bot.send_message = AsyncMock()
    return mock_context


@pytest.fixture
def example_match():
    return {
        "id": 1,
        "league": {"name": "ESL"},
        "tournament": {"name": "Pro League"},
        "serie": {"full_name": "Season 20"},
        "opponents": [
            {"id": 1, "name": "Team A"},
            {"id": 2, "name": "Team B"}
        ],
        "status": "upcoming",
        "begin_at": "2099-12-31T15:00:00Z",
        "stream_url": "http://example.com"
    }


@pytest.mark.asyncio
async def test_send_match_batch_basic(fake_update, fake_context, example_match):
    await send_match_batch(
        update=fake_update,
        context=fake_context,
        matches=[example_match],
        prefix_text="Матчи:",
    )

    assert fake_context.bot.send_message.await_count == 2
    fake_context.bot.send_message.assert_any_await(
        chat_id=12345,
        text="Матчи:",
        parse_mode="HTML"
    )


@pytest.mark.asyncio
async def test_send_match_batch_empty(fake_update, fake_context):
    await send_match_batch(
        update=fake_update,
        context=fake_context,
        matches=[],
        prefix_text="Матчи:",
        empty_text="Нет матчей"
    )

    fake_context.bot.send_message.assert_awaited_once_with(
        chat_id=12345,
        text="Нет матчей"
    )


def test_match_team_names():
    match = {
        "opponents": [
            {"name": "Team A"},
            {"name": "Team B"}
        ]
    }
    assert match_team_names(match) == "Team A vs Team B"

    # тест для одного соперника
    match2 = {"opponents": [{"name": "Solo"}]}
    assert match_team_names(match2) == "Solo vs Team2"

    # тест без соперников
    match3 = {"opponents": []}
    assert match_team_names(match3) == "Team1 vs Team2"