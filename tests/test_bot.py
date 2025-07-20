import pytest
from telegram import Update
from telegram.ext import ContextTypes
from unittest.mock import AsyncMock, MagicMock
import bot.bot as bot_module


@pytest.fixture
def fake_update():
    update = MagicMock(spec=Update)
    update.effective_chat.id = 123456
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def fake_context():
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot.send_message = AsyncMock()
    return context


@pytest.mark.asyncio
async def test_start_command(fake_update, fake_context):
    await bot_module.start(fake_update, fake_context)
    fake_update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_next_matches_command(fake_update, fake_context):
    await bot_module.next_matches(fake_update, fake_context)
    fake_context.bot.send_message.assert_called()


@pytest.mark.asyncio
async def test_live_matches_command(fake_update, fake_context):
    await bot_module.live_matches(fake_update, fake_context)
    fake_context.bot.send_message.assert_called()


@pytest.mark.asyncio
async def test_recent_matches_command(fake_update, fake_context):
    await bot_module.recent_matches(fake_update, fake_context)
    fake_context.bot.send_message.assert_called()


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