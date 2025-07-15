import os
import asyncio
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timezone
from dotenv import load_dotenv

from db import (
    get_all_subscribers,
    get_notified_match_ids,
    mark_notified,
    get_subscriber_tier
)

from utils.match_cache_reader import get_matches
from utils.match_formatter import format_match_info
from utils.logging_config import setup_logging

load_dotenv()
os.makedirs("logs", exist_ok=True)
setup_logging()
logger = logging.getLogger("notifications")

async def notify_upcoming_matches(bot):
    try:
        logger.info("🔍 Запуск проверки матчей...")

        subscribers = get_all_subscribers() or []
        logger.info(f"👥 Найдено подписчиков: {len(subscribers)}")

        subs_by_tier = {"sa": [], "all": []}
        for user_id in subscribers:
            tier = get_subscriber_tier(user_id)
            tier = tier if tier in ["sa", "all"] else "all"
            subs_by_tier.setdefault(tier, []).append(user_id)
            logger.debug(f"Пользователь {user_id} имеет подписку {tier}")

        logger.info(f"S/A подписчиков: {len(subs_by_tier.get('sa', []))}, ALL подписчиков: {len(subs_by_tier.get('all', []))}")

        matches_by_tier = {
            "sa": get_matches(status="upcoming", limit=10, tier="sa"),
            "all": get_matches(status="upcoming", limit=10, tier="all")
        }

        now = datetime.now(timezone.utc)
        logger.info(f"🕒 Текущее UTC время: {now.isoformat()}")

        for tier, matches in matches_by_tier.items():
            logger.info(f"📦 Получено {len(matches)} матчей для tier={tier}")
            for match in matches:
                match_id = match.get("id")
                begin_at = match.get("begin_at")

                logger.info(f"[{tier.upper()}] Обработка матча {match_id} | Время начала: {begin_at}")
                logger.debug(f"Матч: {match}")

                if not begin_at:
                    logger.warning(f"⚠️ У матча {match_id} нет begin_at")
                    continue

                try:
                    start_time = datetime.fromisoformat(begin_at.replace("Z", "+00:00"))
                except Exception as e:
                    logger.error(f"❌ Ошибка разбора begin_at для матча {match_id}: {e}")
                    continue

                minutes_to_start = (start_time - now).total_seconds() / 60
                logger.info(f"⏳ До начала матча {match_id}: {minutes_to_start:.2f} мин")

                if -6 <= minutes_to_start <= 5:
                    match_info = format_match_info(match)
                    league = match_info["league_name"]
                    tournament = match_info["tournament_name"]
                    teams = match_info["teams"]
                    stream_url = match_info["stream_url"]
                    time_until = match.get("time_until", "время неизвестно")

                    if stream_url and stream_url.startswith("http"):
                        text = (
                            f"<b>🔔 Скоро начнётся матч!</b>\n"
                            f"<b>Турнир:</b> {league} | {tournament}\n"
                            f"<b>Начнётся через:</b> {time_until}"
                        )
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text=f"🟪 {teams}", url=stream_url)]
                        ])
                    else:
                        text = (
                            f"<b>🔔 Скоро начнётся матч!</b>\n"
                            f"<b>Турнир:</b> {league} | {tournament}\n"
                            f"<b>Матч:</b> {teams}\n"
                            f"<b>Начнётся через:</b> {time_until}\n"
                            f"⚠️ <i>Трансляция отсутствует</i>"
                        )
                        keyboard = None

                    for user_id in subs_by_tier.get(tier, []):
                        notified_set = get_notified_match_ids(user_id)
                        already_notified = match_id in notified_set

                        if already_notified:
                            logger.info(f"🔁 Пользователь {user_id} уже уведомлён о матче {match_id}")
                            continue

                        try:
                            await bot.send_message(
                                chat_id=user_id,
                                text=text,
                                parse_mode="HTML",
                                reply_markup=keyboard
                            )
                            mark_notified(user_id, match_id)
                            logger.info(f"✅ Уведомление отправлено пользователю {user_id} о матче {match_id}")
                        except Exception as e:
                            logger.warning(f"⚠️ Ошибка отправки пользователю {user_id}: {e}")
                else:
                    logger.info(f"⏭ Матч {match_id} начинается позже (>{minutes_to_start:.2f} мин.)")

    except Exception as e:
        logger.error(f"🔥 Ошибка в notify_upcoming_matches: {e}")

if __name__ == "__main__":
    from telegram import Bot

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    INTERVAL = int(os.getenv("NOTIFY_INTERVAL_SECONDS", 60))
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    async def main():
        while True:
            await notify_upcoming_matches(bot)
            await asyncio.sleep(INTERVAL)

    asyncio.run(main())