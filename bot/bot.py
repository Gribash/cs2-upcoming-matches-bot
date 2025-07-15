import os
import asyncio
import nest_asyncio
import logging
from dotenv import load_dotenv
from telegram.request import HTTPXRequest
from telegram import Update, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Импорт утилит
from utils.match_cache_reader import get_matches
from utils.tournament_cache_reader import get_tournament_name_by_id
from utils.match_formatter import format_match_info
from db import (
    init_db,
    add_subscriber,
    update_is_active,
    get_subscriber_tier,
    is_subscriber_active,
    update_tier,
)

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("Не задан TELEGRAM_BOT_TOKEN в .env")

# Инициализация базы данных
init_db()

# Настройка логирования
from utils.logging_config import setup_logging
setup_logging()
logger = logging.getLogger("bot")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    add_subscriber(user_id, tier="sa")
    update_is_active(user_id, True)
    logger.info(f"/start от пользователя {user_id}")
    await update.message.reply_text(
        "Привет! Я бот для CS2 матчей. Ты автоматически подписан на уведомления о матчах топ-турниров (S и A tier).\n\n"
        "Введи /next, чтобы узнать ближайшие матчи."
    )

# Команда /live
async def live_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logger.info(f"/live от пользователя {user_id}")

    tier = get_subscriber_tier(user_id) or "all"
    logger.info(f"Tier пользователя {user_id}: {tier}")
    matches = get_matches(status="live", tier=tier, limit=8)

    logger.info(f"Найдено {len(matches)} live матчей для пользователя {user_id}")

    if not matches:
        await update.message.reply_text("Сейчас нет активных матчей.")
        return

    for match in matches:
        match_info = format_match_info(match)
        league = match_info["league_name"]
        tournament = match_info["tournament_name"]
        teams = match_info["teams"]
        stream_url = match_info["stream_url"]

        message_text = f"<b>🔴 LIVE</b>\n<b>Турнир:</b> {league} | {tournament}"

        if stream_url and stream_url.startswith("http"):
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(text=f"🟪 {teams}", url=stream_url)]
            ])
        else:
            message_text += f"\n<b>Матч:</b> {teams}\n⚠️ <i>Трансляция отсутствует</i>"
            keyboard = None

        await context.bot.send_message(
            chat_id=user_id,
            text=message_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

# Команда /next
async def next_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logger.info(f"/next от пользователя {user_id}")

    tier = get_subscriber_tier(user_id) or "all"
    logger.info(f"Tier пользователя {user_id}: {tier}")
    matches = get_matches(status="upcoming", tier=tier, limit=8)

    logger.info(f"Найдено {len(matches)} предстоящих матчей для пользователя {user_id}")

    if not matches:
        await update.message.reply_text("Нет ближайших матчей.")
        return

    for match in matches:
        match_info = format_match_info(match)
        league = match_info["league_name"]
        tournament = match_info["tournament_name"]
        teams = match_info["teams"]
        stream_url = match_info["stream_url"]
        time_until = match.get("time_until", "время неизвестно")

        if stream_url and stream_url.startswith("http"):
            message_text = (
                f"<b>⏳ Ближайший матч</b>\n"
                f"<b>Турнир:</b> {league} | {tournament}\n"
                f"<b>Начнётся через:</b> {time_until}"
            )
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(text=f"🟪 {teams}", url=stream_url)]
            ])
        else:
            message_text = (
                f"<b>⏳ Ближайший матч</b>\n"
                f"<b>Турнир:</b> {league} | {tournament}\n"
                f"<b>Матч:</b> {teams}\n"
                f"<b>Начнётся через:</b> {time_until}\n"
                f"⚠️ <i>Трансляция отсутствует</i>"
            )
            keyboard = None

        await context.bot.send_message(
            chat_id=user_id,
            text=message_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

# Команда /recent
async def recent_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logger.info(f"/recent от пользователя {user_id}")

    tier = get_subscriber_tier(user_id) or "all"
    logger.info(f"Tier пользователя {user_id}: {tier}")
    matches = get_matches(status="past", tier=tier, limit=8)

    logger.info(f"Найдено {len(matches)} прошедших матчей для пользователя {user_id}")

    if not matches:
        await update.message.reply_text("Нет завершённых матчей.")
        return

    for match in matches[:5]:
        match_info = format_match_info(match)
        league = match_info["league_name"]
        tournament = match_info["tournament_name"]
        teams = match_info["teams"]
        winner = match.get("winner_id", "Победитель неизвестен")

        msg = (
            f"<b>🏁 Завершённый матч</b>\n"
            f"<b>Турнир:</b> {league} | {tournament}\n"
            f"<b>Матч:</b> {teams}\n"
            f"🏆 <b>Победитель ID:</b> {winner}"
        )

        await context.bot.send_message(
            chat_id=user_id,
            text=msg,
            parse_mode="HTML"
        )

# Команда /subscribe
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    add_subscriber(user_id, tier="sa")
    logger.info(f"/subscribe от пользователя {user_id}")
    await update.message.reply_text(
        "Вы подписаны на уведомления о ближайших матчах S и A-tier турниров."
    )

# Команда /unsubscribe
async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    update_is_active(user_id, False)
    logger.info(f"/unsubscribe от пользователя {user_id}")
    await update.message.reply_text("Вы отписаны от уведомлений.")

# Команда /subscribe_all
async def subscribe_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    add_subscriber(user_id, tier="all")
    logger.info(f"/subscribe_all от пользователя {user_id}")
    await update.message.reply_text(
        "Теперь вы подписаны на все матчи (включая B, C и D турниры)."
    )

# Установка команд
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

# Главный запуск
async def main():
    request = HTTPXRequest(connect_timeout=15.0, read_timeout=30.0)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).request(request).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("next", next_matches))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    app.add_handler(CommandHandler("subscribe_all", subscribe_all))
    app.add_handler(CommandHandler("recent", recent_matches))
    app.add_handler(CommandHandler("live", live_matches))

    await set_bot_commands(app)

    logger.info("Бот запущен")
    print("Бот запущен")
    await app.run_polling()

nest_asyncio.apply()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())