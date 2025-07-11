import os
import asyncio
import nest_asyncio
import logging
from dotenv import load_dotenv
from telegram.request import HTTPXRequest
from telegram import Update, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Импорт утилит
from utils.pandascore import get_upcoming_cs2_matches, get_recent_cs2_matches, get_live_cs2_matches
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

# Инициализация базы данных
init_db()

# Убедись, что папка для логов существует
os.makedirs("logs", exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

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

    tier = get_subscriber_tier(user_id)
    logger.info(f"Tier пользователя {user_id}: {tier}")
    matches = await get_live_cs2_matches(tier=tier)

    logger.info(f"Найдено {len(matches)} live матчей для пользователя {user_id}")

    if not matches:
        await update.message.reply_text("Сейчас нет активных матчей.")
        return

    # Показываем до 8 матчей
    for match in matches[:8]:
        league = match.get("league", "Без лиги")
        tournament = match.get("tournament", "Без турнира")
        teams = match.get("teams", "Команды неизвестны")
        stream_url = match.get("stream_url")

        logger.info(f"LIVE матч: {league} | {tournament} | {teams} | {stream_url}")

        # Текст сообщения без названия команд
        message_text = (
            f"<b>LIVE 🔴</b>\n"
            f"<b>Турнир:</b> {league} | {tournament}"
        )

        # Кнопка с названием матча
        if stream_url:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"{teams}", url=stream_url)]
            ])
        else:
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

    tier = get_subscriber_tier(user_id)
    logger.info(f"Tier пользователя {user_id}: {tier}")
    matches = await get_upcoming_cs2_matches(limit=8, tier=tier)

    logger.info(f"Найдено {len(matches)} предстоящих матчей для пользователя {user_id}")

    if not matches:
        await update.message.reply_text("Нет ближайших матчей.")
        return

    msg = "Upcoming matches🔜\n"
    for match in matches:
        logger.info(f"Матч: {match['league']} | {match['tournament']} | {match['teams']} | {match['begin_at']}")
        msg += (
            f"\n🟣 {match['league']} | {match['tournament']} \n"
            f"🆚 {match['teams']}\n"
            f"⏳ {match['time_until']}\n"
            f"🖥 {match['stream_url']}\n"
        )

    await update.message.reply_text(msg)

# Команда /recent
async def recent_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logger.info(f"/recent от пользователя {user_id}")

    tier = get_subscriber_tier(user_id)
    logger.info(f"Tier пользователя {user_id}: {tier}")
    matches = await get_recent_cs2_matches(limit=8, tier=tier)

    logger.info(f"Найдено {len(matches)} прошедших матчей для пользователя {user_id}")

    if not matches:
        await update.message.reply_text("Нет завершённых матчей.")
        return

    msg = "Recent matches🏁\n"
    for match in matches:
        logger.info(f"Прошедший матч: {match['league']} | {match['tournament']} | {match['teams']} | Победитель: {match['winner']}")
        msg += (
            f"\n🆚 {match['teams']}\n"
            f"🟣 {match['league']} | {match['tournament']}\n"
            f"🏆 Победитель: {match['winner']}\n"
        )

    await update.message.reply_text(msg)

# Команда /subscribe
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    add_subscriber(user_id, tier='sa')
    update_is_active(user_id, True)
    logger.info(f"/subscribe от пользователя {user_id}")
    await update.message.reply_text("Вы подписаны на уведомления о ближайших матчах S и A-tier турниров.")

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
    update_is_active(user_id, True)
    update_tier(user_id, "all")
    logger.info(f"/subscribe_all от пользователя {user_id}")
    await update.message.reply_text("Теперь вы подписаны на все матчи (включая B, C и D турниры).")

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
    request = HTTPXRequest(connect_timeout=15.0, read_timeout=20.0)
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