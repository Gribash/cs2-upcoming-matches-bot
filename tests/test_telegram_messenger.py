import pytest
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.telegram_messenger import send_match_batch


@pytest.mark.asyncio
async def test_send_match_batch_basic():
    mock_update = MagicMock(spec=Update)
    mock_update.effective_chat.id = 123456
    mock_update.message = MagicMock()

    mock_context = MagicMock()
    mock_context.bot.send_message = AsyncMock()

    matches = [
        {
            "id": 1,
            "league": {"name": "ESL"},
            "tournament": {"name": "Pro League"},
            "serie": {"full_name": "Season 20"},
            "opponents": [{"id": 1, "name": "Team A"}, {"id": 2, "name": "Team B"}],
            "status": "upcoming",
            "begin_at": "2099-12-31T15:00:00Z",
            "stream_url": "http://example.com",
        }
    ]

    await send_match_batch(
        update=mock_update,
        context=mock_context,
        matches=matches,
        prefix_text="Матчи:",
        show_time_until=True,
        lang="ru" 
    )

    # Проверяем, что хотя бы 2 сообщения отправлены (префикс + матч)
    assert mock_context.bot.send_message.call_count >= 2

    # Проверяем, что первое сообщение — это префикс
    first_call_args = mock_context.bot.send_message.call_args_list[0][1]
    assert first_call_args["text"].startswith("Матчи:")

    # Проверяем, что второе сообщение содержит кнопку с названием команд
    second_call_kwargs = mock_context.bot.send_message.call_args_list[1][1]
    reply_markup = second_call_kwargs.get("reply_markup")
    assert isinstance(reply_markup, InlineKeyboardMarkup)
    assert "Team A vs Team B" in str(reply_markup.to_dict())


@pytest.mark.asyncio
async def test_send_match_batch_without_stream():
    mock_update = MagicMock(spec=Update)
    mock_update.effective_chat.id = 123456
    mock_context = MagicMock()
    mock_context.bot.send_message = AsyncMock()

    matches = [
        {
            "id": 2,
            "league": {"name": "ESL"},
            "tournament": {"name": "Pro League"},
            "serie": {"full_name": "Season 20"},
            "opponents": [{"id": 1, "name": "Team C"}, {"id": 2, "name": "Team D"}],
            "status": "upcoming",
            "begin_at": "2099-12-31T15:00:00Z",
            "stream_url": None,
        }
    ]

    await send_match_batch(
        update=mock_update,
        context=mock_context,
        matches=matches,
        prefix_text="Матчи:",
        show_time_until=True,
        lang="ru" 
    )

    # Проверяем, что второй вызов send_message не содержит клавиатуру
    second_call_kwargs = mock_context.bot.send_message.call_args_list[1][1]
    assert second_call_kwargs.get("reply_markup") is None
    assert "Трансляция отсутствует" in second_call_kwargs["text"]


@pytest.mark.asyncio
async def test_send_match_batch_empty():
    mock_update = MagicMock(spec=Update)
    mock_update.effective_chat.id = 123456
    mock_context = MagicMock()
    mock_context.bot.send_message = AsyncMock()

    await send_match_batch(
        update=mock_update,
        context=mock_context,
        matches=[],
        prefix_text="Матчи:",
        empty_text="Пусто",
        lang="ru" 
    )

    mock_context.bot.send_message.assert_called_once()
    args, kwargs = mock_context.bot.send_message.call_args
    assert kwargs["text"] == "Пусто"