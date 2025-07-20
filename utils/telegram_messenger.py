from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

from utils.form_match_card import build_match_card

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
    empty_text: str = "Матчи не найдены"
):
    user_id = update.effective_chat.id

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
            stream_button_text=f"{match_team_names(match)}" if stream_button else ""
        )

        await context.bot.send_message(
            chat_id=user_id,
            text=message_text,
            parse_mode="HTML",
            reply_markup=keyboard if stream_button else None
        )


def match_team_names(match: dict) -> str:
    opponents = match.get("opponents", [])
    team1 = opponents[0].get("name") if len(opponents) > 0 else "Team1"
    team2 = opponents[1].get("name") if len(opponents) > 1 else "Team2"
    return f"{team1} vs {team2}"