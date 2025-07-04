import os
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from db import get_all_subscribers, get_notified_match_ids, mark_notified
from utils.pandascore import get_upcoming_cs2_matches

# Загрузка переменных окружения
load_dotenv()
USE_MOCK = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/notifications.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

# Мок-данные для тестов
from datetime import datetime, timedelta, timezone

async def get_mock_upcoming_matches():
    start_time = datetime.now(timezone.utc) + timedelta(minutes=1)
    begin_at_iso = start_time.isoformat()  # формат: 2025-07-04T17:51:00+00:00

    return [
        {
            "id": 999001,
            "teams": "Team Alpha vs Team Beta",
            "league": "Test League",
            "tournament": "Test Cup",
            "time_until": "Начнётся через 1 мин.",
            "stream_url": "https://twitch.tv/test_stream",
            "begin_at": begin_at_iso
        }
    ]

# Логика уведомлений
async def notify_upcoming_matches(bot):
    try:
        matches = await (get_mock_upcoming_matches() if USE_MOCK else get_upcoming_cs2_matches(limit=10))
        subscribers = get_all_subscribers()
        now = datetime.now(timezone.utc)

        for match in matches:
            match_id = match["id"]
            begin_at = match.get("begin_at")
            if not begin_at:
                continue

            try:
                start_time = datetime.fromisoformat(begin_at.replace("Z", "+00:00"))
            except Exception:
                continue

            minutes_to_start = (start_time - now).total_seconds() / 60
            if 0 <= minutes_to_start <= 5:
                text = (
                    f"🔔 Скоро начнётся матч!\n\n"
                    f"🟣 {match['league']} | {match['tournament']}\n"
                    f"🆚 {match['teams']}\n"
                    f"⏳ {match['time_until']}\n"
                    f"🖥 {match['stream_url']}"
                )

                for user_id in subscribers:
                    already_notified = match_id in get_notified_match_ids(user_id)
                    if already_notified:
                        continue

                    try:
                        await bot.send_message(chat_id=user_id, text=text)
                        mark_notified(user_id, match_id)
                        logger.info(f"Отправлено уведомление пользователю {user_id} о матче {match_id}")
                    except Exception as e:
                        logger.warning(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

    except Exception as e:
        logger.error(f"Ошибка в notify_upcoming_matches: {e}")