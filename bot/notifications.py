import os
import asyncio
import logging
from datetime import datetime, timezone
from telegram import Bot
from telegram.error import Forbidden
from dotenv import load_dotenv

from bot.db import (
    get_all_subscribers,
    get_notified_match_ids,
    mark_notified_bulk,
    update_is_active,
    get_subscriber_tier,
    get_subscriber_language,
)
from utils.matches_cache_reader import get_matches
from utils.logging_config import setup_logging
from utils.form_match_card import build_match_card
from utils.translations import t

# Загрузка переменных окружения
load_dotenv()
os.makedirs("logs", exist_ok=True)
setup_logging()
logger = logging.getLogger("notifications")
logger.setLevel(logging.DEBUG if os.getenv("DEV_MODE") == "true" else logging.INFO)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
INTERVAL = int(os.getenv("NOTIFY_INTERVAL_SECONDS", 60))
bot = Bot(token=TELEGRAM_BOT_TOKEN)


# --- Рассылка уведомления ---
async def send(user_id, match_id, match_name, message, keyboard, successful_notifications):
    try:
        await bot.send_message(chat_id=user_id, text=message, parse_mode="HTML", reply_markup=keyboard)
        logger.info(f"✅ Уведомление отправлено: {user_id} -> {match_name} ({match_id})")
        successful_notifications.append((user_id, match_id))
        logger.debug(f"📝 Добавлено к записи: {user_id} -> матч {match_id}")
    except Forbidden:
        logger.warning(f"🚫 Пользователь {user_id} заблокировал бота. Помечаем как неактивного.")
        update_is_active(user_id, False)
    except Exception as e:
        logger.warning(f"⚠️ Ошибка при отправке пользователю {user_id}: {e}")


# --- Основная логика уведомлений ---
async def notify_upcoming_matches():
    try:
        logger.debug("🔍 Запуск проверки матчей...")

        subscribers = get_all_subscribers() or []
        logger.debug(f"👥 Найдено подписчиков: {len(subscribers)}")

        # Группируем пользователей по tier
        tier_by_user = {
            user_id: get_subscriber_tier(user_id) or "all"
            for user_id in subscribers
        }

        subs_by_tier = {"sa": [], "all": []}
        for user_id, tier in tier_by_user.items():
            tier = tier if tier in ["sa", "all"] else "all"
            subs_by_tier[tier].append(user_id)

        logger.debug(f"S/A: {len(subs_by_tier['sa'])}, ALL: {len(subs_by_tier['all'])}")

        # Уже уведомлённые пользователи
        notified_ids_by_user = {
            user_id: set(get_notified_match_ids(user_id))
            for user_id in subscribers
        }

        now = datetime.now(timezone.utc)

        # Загружаем матчи из кэша
        matches_by_tier = {
            "sa": get_matches(status="upcoming", tier="sa", limit=20),
            "all": get_matches(status="upcoming", tier="all", limit=20),
        }

        successful_notifications = []

        # Проходим по матчам для каждого tier
        for tier, matches in matches_by_tier.items():
            for match in matches:
                match_id = match.get("id")
                begin_at = match.get("begin_at")

                if not begin_at:
                    logger.warning(f"⚠️ Нет begin_at у матча {match_id}")
                    continue

                # Определяем время старта матча
                try:
                    start_time = datetime.fromisoformat(begin_at.replace("Z", "+00:00"))
                except Exception as e:
                    logger.warning(f"❌ Ошибка разбора времени: {e}")
                    continue

                # Считаем минуты до начала
                minutes_to_start = (start_time - now).total_seconds() / 60

                # Проверка окна уведомлений (-5/+5 минут от начала)
                if -5 <= minutes_to_start <= 5:
                    match_name = match.get("name", "?")

                    tasks = []

                    # Отправляем уведомления каждому пользователю
                    for user_id in subs_by_tier.get(tier, []):
                        if match_id in notified_ids_by_user.get(user_id, set()):
                            logger.debug(f"🔁 Уже уведомлён: {user_id} -> матч {match_id}")
                            continue

                        # Получаем язык пользователя
                        lang = get_subscriber_language(user_id)

                        # Логируем наличие stream_url
                        stream_url = match.get("stream_url")
                        if stream_url:
                            logger.debug(f"🎥 Матч {match_id}: stream_url найден -> {stream_url}")
                        else:
                            logger.debug(f"🚫 Матч {match_id}: stream_url отсутствует")

                        # Формируем сообщение с кнопкой
                        message, keyboard = build_match_card(
                            match,
                            stream_button=True,
                            lang=lang
                        )

                        prefix = t("prefix_starting", lang)
                        final_message = prefix + message

                        tasks.append(send(user_id, match_id, match_name, final_message, keyboard, successful_notifications))

                    # Выполняем все отправки
                    await asyncio.gather(*tasks)

                    # Отмечаем уведомления в базе
                    if successful_notifications:
                        logger.info(f"💾 Отмечено {len(successful_notifications)} уведомлений в базе.")
                        mark_notified_bulk(successful_notifications)
                else:
                    logger.debug(f"⏭ Матч {match_id} не попадает в окно уведомления")

    except Exception as e:
        logger.exception(f"🔥 Ошибка в notify_upcoming_matches: {e}")


# --- Циклический запуск ---
async def main():
    while True:
        await notify_upcoming_matches()
        await asyncio.sleep(INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())