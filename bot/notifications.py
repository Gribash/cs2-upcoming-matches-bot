import os
import asyncio
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup  # Для отправки сообщений с кнопками
from datetime import datetime, timezone
from dotenv import load_dotenv

# Импорт функций работы с подписчиками и уведомлениями
from db import (
    get_all_subscribers,
    get_notified_match_ids,
    mark_notified,
    get_subscriber_tier
)

# Импорт функции получения предстоящих матчей
from utils.pandascore import get_upcoming_cs2_matches

# Загрузка переменных окружения из .env
load_dotenv()

# Создание папки для логов, если она отсутствует
os.makedirs("logs", exist_ok=True)

# Настройка логирования
from utils.logging_config import setup_logging
setup_logging()

logger = logging.getLogger(__name__)

# Основная функция, которая вызывается циклически: отправляет уведомления о матчах
async def notify_upcoming_matches(bot):
    try:
        logger.info("🔍 Запуск проверки матчей...")

        # Загружаем список всех подписчиков из базы
        subscribers = get_all_subscribers()
        logger.info(f"👥 Найдено подписчиков: {len(subscribers)}")

        # Группировка подписчиков по их уровню подписки (tier)
        subs_by_tier = {"sa": [], "all": []}
        for user_id in subscribers:
            tier = get_subscriber_tier(user_id)  # Возвращает 'sa' или 'all'
            subs_by_tier.setdefault(tier, []).append(user_id)
            logger.debug(f"Пользователь {user_id} имеет подписку {tier}")

        logger.info(f"S/A подписчиков: {len(subs_by_tier.get('sa', []))}, ALL подписчиков: {len(subs_by_tier.get('all', []))}")

        # Загружаем список предстоящих матчей отдельно для каждой группы tier
        matches_by_tier = {
            "sa": await get_upcoming_cs2_matches(limit=10, tier="sa"),
            "all": await get_upcoming_cs2_matches(limit=10, tier="all")
        }

        # Получаем текущее UTC-время
        now = datetime.now(timezone.utc)
        logger.info(f"🕒 Текущее UTC время: {now.isoformat()}")

        # Обрабатываем матчи по каждому tier
        for tier, matches in matches_by_tier.items():
            logger.info(f"📦 Получено {len(matches)} матчей для tier={tier}")
            for match in matches:
                match_id = match.get("id")
                begin_at = match.get("begin_at")

                logger.info(f"[{tier.upper()}] Обработка матча {match_id} | Время начала: {begin_at}")
                logger.debug(f"Матч: {match}")

                # Если нет времени начала — пропускаем
                if not begin_at:
                    logger.warning(f"⚠️ У матча {match_id} нет begin_at")
                    continue

                # Преобразуем строку времени начала в объект datetime
                try:
                    start_time = datetime.fromisoformat(begin_at.replace("Z", "+00:00"))
                except Exception as e:
                    logger.error(f"❌ Ошибка разбора begin_at для матча {match_id}: {e}")
                    continue

                # Считаем, сколько минут осталось до начала матча
                minutes_to_start = (start_time - now).total_seconds() / 60
                logger.info(f"⏳ До начала матча {match_id}: {minutes_to_start:.2f} мин")

                # Отправляем уведомление, если матч скоро начнётся (в пределах [-6, +5] минут)
                if -6 <= minutes_to_start <= 5:
                    # Получаем информацию для форматирования сообщения
                    league = match.get("league", "Без лиги")
                    tournament = match.get("tournament", "Без турнира")
                    teams = match.get("teams", "Команды неизвестны")
                    stream_url = match.get("stream_url")
                    time_until = match.get("time_until", "время неизвестно")

                    # Формируем сообщение и кнопку
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

                    # Перебираем всех подписчиков нужного tier
                    for user_id in subs_by_tier.get(tier, []):
                        notified_set = get_notified_match_ids(user_id)
                        already_notified = match_id in notified_set

                        if already_notified:
                            logger.info(f"🔁 Пользователь {user_id} уже уведомлён о матче {match_id}")
                            continue

                        # Отправляем сообщение
                        try:
                            await bot.send_message(
                                chat_id=user_id,
                                text=text,
                                parse_mode="HTML",
                                reply_markup=keyboard
                            )
                            # Помечаем, что уведомление отправлено
                            mark_notified(user_id, match_id)
                            logger.info(f"✅ Уведомление отправлено пользователю {user_id} о матче {match_id}")
                        except Exception as e:
                            logger.warning(f"⚠️ Ошибка отправки пользователю {user_id}: {e}")
                else:
                    logger.info(f"⏭ Матч {match_id} начинается позже (>{minutes_to_start:.2f} мин.)")

    except Exception as e:
        logger.error(f"🔥 Ошибка в notify_upcoming_matches: {e}")

# Если файл запущен напрямую — запускаем цикл уведомлений
if __name__ == "__main__":
    from telegram import Bot

    # Загружаем токен Telegram из .env
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # Интервал между проверками матчей (в секундах)
    INTERVAL = int(os.getenv("NOTIFY_INTERVAL_SECONDS", 60))

    # Инициализируем Telegram-бота
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    # Основной цикл — бесконечно вызываем notify_upcoming_matches с паузой
    async def main():
        while True:
            await notify_upcoming_matches(bot)
            await asyncio.sleep(INTERVAL)

    # Запускаем цикл событий
    asyncio.run(main())