import os
import asyncio
import nest_asyncio
import logging
from dotenv import load_dotenv
from telegram.request import HTTPXRequest
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Импорт утилит
from utils.pandascore import get_upcoming_cs2_matches
from utils.pandascore import get_recent_cs2_matches
from utils.pandascore import get_live_cs2_matches
from utils.pandascore import get_mock_upcoming_matches
from db import init_db, add_subscriber, remove_subscriber

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
    add_subscriber(user_id)
    logger.info(f"/start от пользователя {user_id}")
    await update.message.reply_text("Привет! Я бот для CS2 матчей. Введи /next чтобы узнать ближайшие матчи.")

# Команда /live
async def live_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logger.info(f"/live от пользователя {user_id}")
    matches = await get_live_cs2_matches()

    if not matches:
        await update.message.reply_text("Сейчас нет активных матчей.")
        return

    msg = "LIVE🔴\n"
    for match in matches:
        msg += (
            f"\n🟣 {match['league']} | {match['tournament']}\n"
            f"🆚 {match['teams']}\n"
            f"🖥 {match['stream_url']}\n"
        )

    await update.message.reply_text(msg)

# Команда /next
async def next_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    matches = await get_upcoming_cs2_matches(limit=5)
    logger.info(f"/next от пользователя {user_id}")

    if not matches:
        await update.message.reply_text("Нет ближайших матчей.")
        return

    msg = "Upcoming matches🔜\n"
    for match in matches:
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
    matches = await get_recent_cs2_matches(limit=5)
    logger.info(f"/recent от пользователя {user_id}")

    if not matches:
        await update.message.reply_text("Нет завершённых матчей.")
        return

    msg = "Recent matches🏁\n"
    for match in matches:
        msg += (
            f"\n🆚 {match['teams']}\n"
            f"🟣 {match['league']} | {match['tournament']}\n"
            f"🏆 Победитель: {match['winner']}\n"
        )

    await update.message.reply_text(msg)

# Команда /subscribe
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    add_subscriber(user_id)
    logger.info(f"/subscribe от пользователя {user_id}")
    await update.message.reply_text("Вы подписаны на уведомления о ближайших матчах.")

# Команда /unsubscribe
async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    remove_subscriber(user_id)
    logger.info(f"/unsubscribe от пользователя {user_id}")
    await update.message.reply_text("Вы отписаны от уведомлений.")

# Команда /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот работает.")

# Команда /test_notify
async def test_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    matches = await get_mock_upcoming_matches()

    if not matches:
        await update.message.reply_text("Нет мок-матчей для теста.")
        return

    for match in matches:
        text = (
            f"🔔 [ТЕСТ] Скоро начнётся матч!\n\n"
            f"🟣 {match['league']} | {match['tournament']}\n"
            f"🆚 {match['teams']}\n"
            f"⏳ {match['time_until']}\n"
            f"🖥 {match['stream_url']}"
        )
        try:
            await update.message.reply_text(text)
        except Exception as e:
            logger.warning(f"Ошибка при отправке тест-уведомления: {e}")

# Установка команд
async def set_bot_commands(app):
    commands = [
        BotCommand("start", "Запустить бота и подписаться"),
        BotCommand("next", "Показать ближайшие матчи"),
        BotCommand("live", "Показать текущие матчи"),
        BotCommand("recent", "Показать завершённые матчи"),
        BotCommand("subscribe", "Подписаться на уведомления"),
        BotCommand("unsubscribe", "Отписаться от уведомлений"),
        BotCommand("status", "Проверить, работает ли бот"),
        BotCommand("test_notify", "Отправить тестовое уведомление"),
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
    app.add_handler(CommandHandler("recent", recent_matches))
    app.add_handler(CommandHandler("live", live_matches))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("test_notify", test_notify))

    await set_bot_commands(app)

    logger.info("Бот запущен")
    print("Бот запущен")
    await app.run_polling()

nest_asyncio.apply()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())