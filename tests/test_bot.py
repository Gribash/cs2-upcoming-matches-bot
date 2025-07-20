import pytest
from types import SimpleNamespace
from telegram import Message
from telegram.ext import ContextTypes
from bot import bot

@pytest.fixture
def fake_update():
    return SimpleNamespace(
        effective_chat=SimpleNamespace(id=123456),
        message=SimpleNamespace(reply_text=lambda text: None)
    )

@pytest.fixture
def fake_context():
    return SimpleNamespace(bot=None)

@pytest.mark.asyncio
async def test_start_command(fake_update, fake_context):
    await bot.start(fake_update, fake_context)

@pytest.mark.asyncio
async def test_next_matches_command(fake_update, fake_context, monkeypatch):
    monkeypatch.setattr("bot.bot.get_matches", lambda **kwargs: [])
    await bot.next_matches(fake_update, fake_context)

@pytest.mark.asyncio
async def test_live_matches_command(fake_update, fake_context, monkeypatch):
    monkeypatch.setattr("bot.bot.get_matches", lambda **kwargs: [])
    await bot.live_matches(fake_update, fake_context)

@pytest.mark.asyncio
async def test_recent_matches_command(fake_update, fake_context, monkeypatch):
    monkeypatch.setattr("bot.bot.get_matches", lambda **kwargs: [])
    await bot.recent_matches(fake_update, fake_context)

@pytest.mark.asyncio
async def test_subscribe_command(fake_update, fake_context):
    await bot.subscribe(fake_update, fake_context)

@pytest.mark.asyncio
async def test_unsubscribe_command(fake_update, fake_context):
    await bot.unsubscribe(fake_update, fake_context)

@pytest.mark.asyncio
async def test_subscribe_all_command(fake_update, fake_context):
    await bot.subscribe_all(fake_update, fake_context)