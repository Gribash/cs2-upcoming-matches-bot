from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

from utils.form_match_card import build_match_card
from bot.db import get_subscriber_language

logger = logging.getLogger("telegram_messenger")


async def send_match_batch(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    matches: list[dict],
    prefix_text: str,
    show_time_until: bool = False,
    show_winner: bool = False,
    stream_button: bool = False,
    empty_text: str = "Матчи не найдены",
    lang: str = None,
):
    user_id = update.effective_chat.id
    lang = lang or get_subscriber_language(user_id)

    if not matches:
        await context.bot.send_message(chat_id=user_id, text=empty_text)
        logger.info(f"❗ Пользователь {user_id}: {empty_text}")
        return

    await context.bot.send_message(chat_id=user_id, text=prefix_text, parse_mode="HTML")

    for match in matches:
        message_text, keyboard = build_match_card(
            match,
            show_time_until=show_time_until,
            show_winner=show_winner,
            stream_button=stream_button,
            lang=lang
        )

        await context.bot.send_message(
            chat_id=user_id,
            text=message_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )