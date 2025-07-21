import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, Message, User, Chat, CallbackQuery
from telegram.ext import ContextTypes
import bot.bot as bot_module


@pytest.fixture
def fake_update():
    user = User(id=123456, is_bot=False, first_name="Test")
    chat = Chat(id=123456, type="private")
    message = MagicMock(spec=Message)
    message.chat = chat
    message.from_user = user
    message.text = "test"
    message.reply_text = AsyncMock()
    message.reply_html = AsyncMock()

    update = MagicMock(spec=Update)
    update.effective_chat = chat
    update.effective_user = user
    update.message = message
    return update


@pytest.fixture
def fake_context():
    context = MagicMock()
    return context


@pytest.mark.asyncio
async def test_start_command(fake_update, fake_context):
    await bot_module.start(fake_update, fake_context)
    fake_update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_next_matches_command(fake_update, fake_context):
    with patch("bot.bot.send_match_batch", new_callable=AsyncMock) as mock_send:
        await bot_module.next_matches(fake_update, fake_context)
        mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_live_matches_command(fake_update, fake_context):
    with patch("bot.bot.send_match_batch", new_callable=AsyncMock) as mock_send:
        await bot_module.live_matches(fake_update, fake_context)
        mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_recent_matches_command(fake_update, fake_context):
    with patch("bot.bot.send_match_batch", new_callable=AsyncMock) as mock_send:
        await bot_module.recent_matches(fake_update, fake_context)
        mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_subscribe_command(fake_update, fake_context):
    await bot_module.subscribe(fake_update, fake_context)
    fake_update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_unsubscribe_command(fake_update, fake_context):
    await bot_module.unsubscribe(fake_update, fake_context)
    fake_update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_subscribe_all_command(fake_update, fake_context):
    await bot_module.subscribe_all(fake_update, fake_context)
    fake_update.message.reply_text.assert_called_once()