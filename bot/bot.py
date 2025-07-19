import os
import asyncio
import nest_asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest

from utils.matches_cache_reader import get_matches
from utils.pandascore import format_time_until
from utils.logging_config import setup_logging
from db import (
    init_db,
    add_subscriber,
    update_is_active,
    get_subscriber_tier,
    update_tier,
)

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
        "Привет! Ты подписан на уведомления о матчах топ-турниров (S и A tier).\n"
        "Введи /next, чтобы узнать ближайшие матчи."
    )

async def send_match(update: Update, context: ContextTypes.DEFAULT_TYPE, match: dict, prefix: str, keyboard=None):
    user_id = update.effective_chat.id

    league = match.get("league", {}).get("name", "?")
    tournament = match.get("tournament", {}).get("name", "?")
    serie = match.get("serie", {}).get("full_name", "?")
    match_name = match.get("name", "?")

    message = (
        f"<b>{prefix}</b>\n"
        f"<b>Турнир:</b> {league} | {tournament} | {serie}\n"
        f"<b>Матч:</b> {match_name}"
    )

    await context.bot.send_message(
        chat_id=user_id,
        text=message,
        parse_mode="HTML",
        reply_markup=keyboard
    )

async def next_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    tier = get_subscriber_tier(user_id) or "all"
    matches = get_matches(status="upcoming", tier=tier, limit=8)

    if not matches:
        await update.message.reply_text("Нет ближайших матчей.")
        return

    for match in matches:
        await send_match(update, context, match, "⏳ Ближайший матч")

async def live_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    tier = get_subscriber_tier(user_id) or "all"
    matches = get_matches(status="running", tier=tier, limit=8)

    if not matches:
        await update.message.reply_text("Сейчас нет активных матчей.")
        return

    for match in matches:
        prefix = "🔴 LIVE"
        stream_url = match.get("stream_url")
        opponents = match.get("opponents", [])

        def get_team(opponent):
            return opponent.get("acronym") or opponent.get("name") or "?"

        team_1 = get_team(opponents[0]) if len(opponents) > 0 else "?"
        team_2 = get_team(opponents[1]) if len(opponents) > 1 else "?"
        teams_text = f"{team_1} vs {team_2}"

        if stream_url and stream_url.startswith("http"):
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(text=f"📺 {teams_text}", url=stream_url)]
            ])
        else:
            keyboard = None

        await send_match(update, context, match, prefix, keyboard)

async def recent_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    tier = get_subscriber_tier(user_id) or "all"
    matches = get_matches(status="past", tier=tier, limit=8)

    if not matches:
        await update.message.reply_text("Нет завершённых матчей.")
        return

    for match in matches:
        await send_match(update, context, match, "🏁 Завершённый матч")

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    add_subscriber(user_id, tier="sa")
    update_is_active(user_id, True)
    await update.message.reply_text("Вы подписаны на уведомления о ближайших матчах S и A-tier турниров.")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    update_is_active(user_id, False)
    await update.message.reply_text("Вы отписаны от уведомлений.")

async def subscribe_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    add_subscriber(user_id, tier="all")
    update_is_active(user_id, True)
    await update.message.reply_text("Теперь вы подписаны на все матчи всех уровней (включая B, C и D).")

async def set_bot_commands(app):
    commands = [
        BotCommand("start", "Запустить бота и подписаться"),
        BotCommand("next", "Показать ближайшие матчи"),
        BotCommand("live", "Показать текущие матчи"),
        BotCommand("recent", "Показать завершённые матчи"),
        BotCommand("subscribe", "Подписаться на уведомления"),
        BotCommand("unsubscribe", "Отписаться от уведомлений"),
        BotCommand("subscribe_all", "Подписаться на все матчи всех уровней"),
    ]
    await app.bot.set_my_commands(commands)

async def main():
    request = HTTPXRequest(connect_timeout=15.0, read_timeout=30.0)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).request(request).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("next", next_matches))
    app.add_handler(CommandHandler("live", live_matches))
    app.add_handler(CommandHandler("recent", recent_matches))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    app.add_handler(CommandHandler("subscribe_all", subscribe_all))

    await set_bot_commands(app)
    logger.info("Бот запущен")
    await app.run_polling()

nest_asyncio.apply()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())