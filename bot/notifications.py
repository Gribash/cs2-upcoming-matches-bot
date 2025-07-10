import os
import asyncio
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
from db import (
    get_all_subscribers,
    get_notified_match_ids,
    mark_notified,
    get_subscriber_tier
)
from utils.pandascore import get_upcoming_cs2_matches

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/notifications.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

# Основная логика уведомлений
async def notify_upcoming_matches(bot):
    try:
        logger.info("🔍 Запуск проверки матчей...")

        # Подгружаем подписчиков
        subscribers = get_all_subscribers()
        logger.info(f"👥 Найдено подписчиков: {len(subscribers)}")

        # Группировка по tier
        subs_by_tier = {"sa": [], "all": []}
        for user_id in subscribers:
            tier = get_subscriber_tier(user_id)
            subs_by_tier.setdefault(tier, []).append(user_id)
            logger.debug(f"Пользователь {user_id} имеет подписку {tier}")

        logger.info(f"S/A подписчиков: {len(subs_by_tier.get('sa', []))}, ALL подписчиков: {len(subs_by_tier.get('all', []))}")

        # Получаем матчи по уровням
        matches_by_tier = {
            "sa": await get_upcoming_cs2_matches(limit=10, tier="sa"),
            "all": await get_upcoming_cs2_matches(limit=10, tier="all")
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

                if -5 <= minutes_to_start <= 5:
                    text = (
                        f"🔔 Скоро начнётся матч!\n\n"
                        f"🟣 {match['league']} | {match['tournament']}\n"
                        f"🆚 {match['teams']}\n"
                        f"⏳ {match['time_until']}\n"
                        f"🖥 {match['stream_url']}"
                    )

                    for user_id in subs_by_tier.get(tier, []):
                        notified_set = get_notified_match_ids(user_id)
                        already_notified = match_id in notified_set

                        if already_notified:
                            logger.info(f"🔁 Пользователь {user_id} уже уведомлён о матче {match_id}")
                            continue

                        try:
                            await bot.send_message(chat_id=user_id, text=text)
                            mark_notified(user_id, match_id)
                            logger.info(f"✅ Уведомление отправлено пользователю {user_id} о матче {match_id}")
                        except Exception as e:
                            logger.warning(f"⚠️ Ошибка отправки пользователю {user_id}: {e}")
                else:
                    logger.info(f"⏭ Матч {match_id} начинается позже (>{minutes_to_start:.2f} мин.)")

    except Exception as e:
        logger.error(f"🔥 Ошибка в notify_upcoming_matches: {e}")

# Автозапуск
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