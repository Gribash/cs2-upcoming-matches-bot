# 🕹️ CS2 Upcoming Matches Bot

Telegram-бот для отслеживания матчей по Counter-Strike 2 с поддержкой уведомлений о live и предстоящих матчах. Работает через PandaScore API.
Размещен на сервере 05.07.2025.
---

## 🚀 Возможности

- Команда `/start` — подписывает пользователя на уведомления
- Команда `/next` — показывает ближайшие матчи
- Команда `/live` — показывает текущие live-матчи
- Команда `/recent` — показывает завершённые матчи
- Команда `/subscribe` и `/unsubscribe` — управление подпиской
- Команда `/test_notify` — тестирование уведомлений на мок-данных
- Поддержка Docker и Supervisor для продакшн-запуска

---

## 🧱 Технологии

- Python 3.11+
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) 20.x
- `httpx` для API-запросов
- SQLite для хранения подписчиков
- Docker, Supervisor
- PandaScore API

---

## ⚙️ Установка и запуск

### 1. Клонировать репозиторий

git clone https://github.com/username/cs2-matches-bot.git
cd cs2-matches-bot

### 2. Создать `.env` файл

TELEGRAM_BOT_TOKEN=ваш_токен_бота
PANDASCORE_API_TOKEN=ваш_токен_pandascore
USE_MOCK_DATA=false

### 3. Запуск через Docker

docker-compose up --build

### 4. Альтернатива — локальный запуск

`python bot/bot.py`

---

## 🧪 Тестирование

Для проверки отправки уведомлений на тестовых матчах:

1. В `.env` установите:
    
    USE_MOCK_DATA=true
    

2. Запустите:
    
    python bot/notifications.py
    

Бот отправит уведомления с тестовыми матчами тем, кто подписан.

---

## 📁 Структура проекта

```
cs2-matches-bot/
│
├── bot/
│   ├── bot.py                  # Telegram-бот
│   ├── notifications.py        # Фоновая задача с уведомлениями
│
├── utils/
│   └── pandascore.py           # Работа с PandaScore API
│
├── data/
│   └── subscribers.db          # SQLite база подписчиков
│
├── logs/                       # Логи
│
├── .env                        # Переменные окружения (не добавляй в git)
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── supervisor.conf
├── requirements.txt
├── README.md
```

utils/ README

This folder contains all utility modules used for the CS2 bot project. Each file is responsible for a specific part of the caching, API interaction, filtering, or logging infrastructure.

Files Overview

pandascore.py

Purpose:
	•	Handles direct async interaction with the PandaScore API.
	•	Loads tournaments, matches, teams, etc.

tournament_cacher.py

Purpose:
	•	Fetches all active (upcoming/running) tournaments.
	•	Filters only relevant tournaments.
	•	Caches to data/tournaments_cache.json.
	•	Run frequency: every hour.

match_cacher.py

Purpose:
	•	Loads all matches for all cached tournaments.
	•	Saves to data/matches_cache.json.
	•	Run frequency: every 10 minutes.

refresh_cache.py

Purpose:
	•	Calls tournament_cacher and match_cacher sequentially.
	•	Can be scheduled via cron or run via Supervisor.

tournament_cache.py

Purpose:
	•	Reads cached tournaments from JSON.
	•	Provides list or dictionary access.
	•	Used by match_cacher and Telegram bot commands.

match_cache.py

Purpose:
	•	Reads cached matches from JSON.
	•	Returns full list of matches for further filtering.

match_cache_filter.py

Purpose:
	•	Filters cached matches by:
	•	Status: upcoming, live, finished
	•	Tier: sa, all
	•	Used in Telegram bot commands (/next, /live, /recent).

cache_writer.py

Purpose:
	•	Contains utility function write_cache(data, filename) to save any dict/list to JSON.
	•	Prevents code duplication in cache-related modules.

logging_config.py

Purpose:
	•	Sets up unified logging across the project.
	•	Creates and configures:
	•	logs/bot.log: bot command activity
	•	logs/notifications.log: match notifications
	•	logs/telegram_http.log: Telegram API requests
	•	Used by bot.py, notifications.py, etc.

Summary Table

File	Role	Schedule / Usage
pandascore.py	API interaction layer	Called by cacher modules
tournament_cacher.py	Tournament data caching	Every 1 hour
match_cacher.py	Match data caching	Every 10 minutes
refresh_cache.py	Sequential cache update	Used by cron / Supervisor
tournament_cache.py	Load cached tournaments	Used in match cacher/bot
match_cache.py	Load cached matches	Used in bot/notifications
match_cache_filter.py	Filter matches by tier and status	Used in bot commands
cache_writer.py	Write cache to file	Used by cacher modules
logging_config.py	Unified logging setup	Used across all modules


⸻

This structure helps to keep code modular, testable, and easy to maintain.