from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from bot.db import add_subscriber, init_db

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот, который уведомит тебя о матчах по CS2!")

async def upcoming(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Здесь будут ближайшие матчи!")

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_subscriber(user_id)
    await update.message.reply_text("Вы успешно подписались на уведомления о матчах!")

def add_handlers(app):
    init_db()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("next", upcoming))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
