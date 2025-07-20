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
from utils.matches_cache_reader import get_matches
from utils.logging_config import setup_logging
from utils.pandascore import format_time_until

# Загрузка переменных окружения
load_dotenv()
os.makedirs("logs", exist_ok=True)
setup_logging()
logger = logging.getLogger("notifications")
logger.setLevel(logging.DEBUG if os.getenv("DEV_MODE") == "true" else logging.INFO)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
INTERVAL = int(os.getenv("NOTIFY_INTERVAL_SECONDS", 60))
bot = Bot(token=TELEGRAM_BOT_TOKEN)


async def notify_upcoming_matches():
    try:
        logger.debug("🔍 Запуск проверки матчей...")

        # Получаем подписчиков
        subscribers = get_all_subscribers() or []
        logger.debug(f"👥 Найдено подписчиков: {len(subscribers)}")

        subs_by_tier = {"sa": [], "all": []}
        for user_id in subscribers:
            tier = get_subscriber_tier(user_id)
            tier = tier if tier in ["sa", "all"] else "all"
            subs_by_tier[tier].append(user_id)

        logger.debug(f"S/A: {len(subs_by_tier['sa'])}, ALL: {len(subs_by_tier['all'])}")

        now = datetime.now(timezone.utc)

        # Загружаем матчи из кэша
        matches_by_tier = {
            "sa": get_matches(status="upcoming", tier="sa", limit=20),
            "all": get_matches(status="upcoming", tier="all", limit=20),
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
                    # --- Формируем сообщение ---
                    league = match.get("league", {}).get("name", "?")
                    tournament = match.get("tournament", {}).get("name", "?")
                    serie = match.get("serie", {}).get("full_name", "?")
                    match_name = match.get("name", "?")

                    message = f"<b>🔔 Матч начинается!</b>\n"
                    message += f"{league} | {tournament}\n{serie}\n<b>{match_name}</b>\n"

                    # --- Формируем кнопку трансляции ---
                    stream_url = match.get("stream_url")
                    opponents = match.get("opponents", [])
                    team1 = opponents[0].get("name") if len(opponents) > 0 else "Team1"
                    team2 = opponents[1].get("name") if len(opponents) > 1 else "Team2"
                    teams_text = f"{team1} vs {team2}"

                    if stream_url and stream_url.startswith("http"):
                        keyboard = InlineKeyboardMarkup([
                            [InlineKeyboardButton(text=f"🟪 {teams_text}", url=stream_url)]
                        ])
                    else:
                        message += "\n <i>Трансляция отсутствует</i>"
                        keyboard = None

                    # --- Рассылка уведомлений ---
                    for user_id in subs_by_tier.get(tier, []):
                        already_notified = match_id in get_notified_match_ids(user_id)
                        if already_notified:
                            logger.debug(f"🔁 Пользователь {user_id} уже уведомлён о матче {match_id}")
                            continue

                        try:
                            await bot.send_message(
                                chat_id=user_id,
                                text=message,
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