import os
import asyncio
import nest_asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.ext import CallbackQueryHandler
from utils.translations import t
from bot.db import update_language, get_subscriber_language

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

    lang = get_subscriber_language(user_id)
    await update.message.reply_text(t("greeting", lang))

async def next_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logger.info(f"/next от пользователя {user_id}")
    tier = get_subscriber_tier(user_id) or "all"
    lang = get_subscriber_language(user_id)
    matches = get_matches(status="upcoming", tier=tier, limit=8)
    await send_match_batch(
        update, context,
        matches=matches,
        prefix_text=t("prefix_upcoming", lang),
        show_time_until=True,
        empty_text=t("no_upcoming", lang)
    )

async def live_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logger.info(f"/live от пользователя {user_id}")
    tier = get_subscriber_tier(user_id) or "all"
    lang = get_subscriber_language(user_id)
    matches = get_matches(status="running", tier=tier, limit=8)
    await send_match_batch(
        update, context,
        matches=matches,
        prefix_text=t("prefix_live", lang),
        stream_button=True,
        empty_text=t("no_live", lang)
    )

async def recent_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logger.info(f"/recent от пользователя {user_id}")
    tier = get_subscriber_tier(user_id) or "all"
    lang = get_subscriber_language(user_id)
    matches = get_matches(status="past", tier=tier, limit=8)
    await send_match_batch(
        update, context,
        matches=matches,
        prefix_text=t("prefix_recent", lang),
        show_winner=True,
        empty_text=t("no_recent", lang)
    )

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logger.info(f"/subscribe_top_tiers от пользователя {user_id}")
    add_subscriber(user_id, tier="sa")
    update_is_active(user_id, True)
    lang = get_subscriber_language(user_id)
    await update.message.reply_text(t("subscribed_top", lang))

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logger.info(f"/unsubscribe от пользователя {user_id}")
    update_is_active(user_id, False)
    lang = get_subscriber_language(user_id)
    await update.message.reply_text(t("unsubscribed", lang))

async def subscribe_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logger.info(f"/subscribe_all_tiers от пользователя {user_id}")
    add_subscriber(user_id, tier="all")
    update_is_active(user_id, True)
    lang = get_subscriber_language(user_id)
    await update.message.reply_text(t("subscribed_all", lang))

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    lang = get_subscriber_language(user_id)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("English", callback_data="lang_en")],
        [InlineKeyboardButton("Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("Português", callback_data="lang_pt")],
    ])
    await update.message.reply_text(t("choose_language", lang), reply_markup=keyboard)

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    lang_code = query.data.replace("lang_", "")
    update_language(user_id, lang_code)

    await query.edit_message_text(t("language_updated", lang_code))

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
    app.add_handler(CommandHandler("language", language))
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))

    await set_bot_commands(app)
    logger.info("Бот запущен")
    await app.run_polling()

nest_asyncio.apply()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())