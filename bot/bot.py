import os
import asyncio
import nest_asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest

from utils.matches_cache_reader import get_matches
from utils.logging_config import setup_logging
from bot.db import (
    init_db,
    add_subscriber,
    update_is_active,
    get_subscriber_tier,
)

# ✅ Новый импорт для отправки карточек матчей
from utils.telegram_messenger import send_match_batch

# Загрузка токена
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("Не задан TELEGRAM_BOT_TOKEN")

# Инициализация
init_db()
os.makedirs("logs", exist_ok=True)
setup_logging()
logger = logging.getLogger("bot")

# --- Команды ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    add_subscriber(user_id, tier="sa")
    update_is_active(user_id, True)
    logger.info(f"/start от пользователя {user_id}")
    await update.message.reply_text(
        "Привет! Я буду отправлять тебе уведомления перед началом матчей.\n"
        "По-умолчанию, я отслеживаю только тир-1 турниры.\n"
        "Но ты можешь подписаться на все матчи через /subscribe_all"
    )

async def next_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logger.info(f"/next от пользователя {user_id}")
    tier = get_subscriber_tier(user_id) or "all"
    matches = get_matches(status="upcoming", tier=tier, limit=8)
    await send_match_batch(
        update, context,
        matches=matches,
        prefix_text="⏳ <b>БЛИЖАЙШИЕ МАТЧИ</b>",
        show_time_until=True,
        empty_text="Нет ближайших матчей"
    )

async def live_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logger.info(f"/live от пользователя {user_id}")
    tier = get_subscriber_tier(user_id) or "all"
    matches = get_matches(status="running", tier=tier, limit=8)
    await send_match_batch(
        update, context,
        matches=matches,
        prefix_text="🔴 <b>LIVE-МАТЧИ</b>",
        stream_button=True,
        empty_text="Сейчас нет активных матчей"
    )

async def recent_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logger.info(f"/recent от пользователя {user_id}")
    tier = get_subscriber_tier(user_id) or "all"
    matches = get_matches(status="past", tier=tier, limit=8)
    await send_match_batch(
        update, context,
        matches=matches,
        prefix_text="🏁 <b>ЗАВЕРШЕННЫЕ МАТЧИ</b>",
        show_winner=True,
        empty_text="Нет результатов недавних матчей"
    )

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logger.info(f"/subscribe_top_tiers от пользователя {user_id}")
    add_subscriber(user_id, tier="sa")
    update_is_active(user_id, True)
    await update.message.reply_text("Вы подписаны на топ-турниры")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logger.info(f"/unsubscribe от пользователя {user_id}")
    update_is_active(user_id, False)
    await update.message.reply_text("Вы отписаны от уведомлений")

async def subscribe_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logger.info(f"/subscribe_all_tiers от пользователя {user_id}")
    add_subscriber(user_id, tier="all")
    update_is_active(user_id, True)
    await update.message.reply_text("Теперь вы подписаны на все турниры")

async def set_bot_commands(app):
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("next", "Показать ближайшие матчи"),
        BotCommand("live", "Показать текущие матчи"),
        BotCommand("recent", "Показать недавние матчи"),
        BotCommand("subscribe_top_tiers", "Подписаться на топ-турниры"),
        BotCommand("unsubscribe", "Отписаться от уведомлений"),
        BotCommand("subscribe_all_tiers", "Подписаться на все турниры"),
    ]
    await app.bot.set_my_commands(commands)

async def main():
    request = HTTPXRequest(connect_timeout=15.0, read_timeout=30.0)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).request(request).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("next", next_matches))
    app.add_handler(CommandHandler("live", live_matches))
    app.add_handler(CommandHandler("recent", recent_matches))
    app.add_handler(CommandHandler("subscribe_top_tiers", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    app.add_handler(CommandHandler("subscribe_all_tiers", subscribe_all))

    await set_bot_commands(app)
    logger.info("Бот запущен")
    await app.run_polling()

nest_asyncio.apply()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())