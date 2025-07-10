import os
import asyncio
from dotenv import load_dotenv
from telegram import BotCommand
from telegram.ext import ApplicationBuilder

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def update():
    app = ApplicationBuilder().token(TOKEN).build()
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
    print("✅ Команды Telegram обновлены.")

asyncio.run(update())
