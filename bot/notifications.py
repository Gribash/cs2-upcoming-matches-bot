import os
import asyncio
import logging
from datetime import datetime, timezone
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

from db import (
    get_all_subscribers,
    get_notified_match_ids,
    mark_notified,
    get_subscriber_tier,
)
from utils.tournament_cache_reader import get_upcoming_matches
from utils.logging_config import setup_logging
from utils.pandascore import format_time_until

# Загрузка переменных окружения
load_dotenv()
os.makedirs("logs", exist_ok=True)
setup_logging()
logger = logging.getLogger("notifications")
logger.setLevel(logging.INFO)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
INTERVAL = int(os.getenv("NOTIFY_INTERVAL_SECONDS", 60))
bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def notify_upcoming_matches():
    try:
        logger.info("🔍 Запуск проверки матчей...")

        # Получаем подписчиков
        subscribers = get_all_subscribers() or []
        logger.info(f"👥 Найдено подписчиков: {len(subscribers)}")

        subs_by_tier = {"sa": [], "all": []}
        for user_id in subscribers:
            tier = get_subscriber_tier(user_id)
            tier = tier if tier in ["sa", "all"] else "all"
            subs_by_tier[tier].append(user_id)

        logger.info(f"S/A: {len(subs_by_tier['sa'])}, ALL: {len(subs_by_tier['all'])}")

        now = datetime.now(timezone.utc)

        # Загружаем матчи из кэша
        matches_by_tier = {
            "sa": get_upcoming_matches(tier="sa", limit=20),
            "all": get_upcoming_matches(tier="all", limit=20),
        }

        for tier, matches in matches_by_tier.items():
            for match in matches:
                match_id = match.get("id")
                begin_at = match.get("begin_at")

                if not begin_at:
                    logger.warning(f"⚠️ Нет begin_at у матча {match_id}")
                    continue

                try:
                    start_time = datetime.fromisoformat(begin_at.replace("Z", "+00:00"))
                except Exception as e:
                    logger.warning(f"❌ Ошибка разбора времени: {e}")
                    continue

                minutes_to_start = (start_time - now).total_seconds() / 60

                if -6 <= minutes_to_start <= 5:
                    # Формируем сообщение
                    time_until = format_time_until(begin_at)
                    team1 = match.get("team_1", {}).get("acronym", "Team1")
                    team2 = match.get("team_2", {}).get("acronym", "Team2")
                    teams = f"{team1} vs {team2}"

                    league = match.get("league", "Unknown League")
                    serie = match.get("serie", "Unknown Serie")
                    stream_url = match.get("stream_url")

                    if stream_url and stream_url.startswith("http"):
                        text = (
                            f"<b>🔔 Скоро начнётся матч!</b>\n"
                            f"<b>Турнир:</b> {league} | {serie}\n"
                            f"<b>Начнётся через:</b> {time_until}"
                        )
                        keyboard = InlineKeyboardMarkup([
                            [InlineKeyboardButton(text=f"🟪 {teams}", url=stream_url)]
                        ])
                    else:
                        text = (
                            f"<b>🔔 Скоро начнётся матч!</b>\n"
                            f"<b>Турнир:</b> {league} | {serie}\n"
                            f"<b>Матч:</b> {teams}\n"
                            f"<b>Начнётся через:</b> {time_until}\n"
                            f"⚠️ <i>Трансляция отсутствует</i>"
                        )
                        keyboard = None

                    # Рассылка уведомлений
                    for user_id in subs_by_tier.get(tier, []):
                        already_notified = match_id in get_notified_match_ids(user_id)
                        if already_notified:
                            logger.info(f"🔁 Пользователь {user_id} уже уведомлён о матче {match_id}")
                            continue

                        try:
                            await bot.send_message(
                                chat_id=user_id,
                                text=text,
                                parse_mode="HTML",
                                reply_markup=keyboard,
                            )
                            mark_notified(user_id, match_id)
                            logger.info(f"✅ Уведомление отправлено: {user_id} -> матч {match_id}")
                        except Exception as e:
                            logger.warning(f"⚠️ Ошибка при отправке пользователю {user_id}: {e}")
                else:
                    logger.debug(f"⏭ Матч {match_id} не попадает в окно уведомления")

    except Exception as e:
        logger.exception(f"🔥 Ошибка в notify_upcoming_matches: {e}")

# Циклический запуск
async def main():
    while True:
        await notify_upcoming_matches()
        await asyncio.sleep(INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())