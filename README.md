## 📁 Структура проекта

```
CS_upcoming_matches_bot/
│
├── bot/                         # Основной код бота
│   ├── __init__.py
│   ├── bot.py                   # Telegram-бот: команды, логика взаимодействия
│   ├── db.py                    # Работа с SQLite-базой (подписчики, уведомления)
│   └── notifications.py         # Уведомления о ближайших матчах
│
├── cache/
│   └── matches.json             # Кэш с данными матчей и турниров
│
├── data/
│   └── subscribers.db           # SQLite-база подписчиков
│
├── logs/                        # Логи всех процессов
│   ├── bot.log
│   ├── db.log
│   ├── errors.log
│   ├── matches.log
│   ├── notifications.log
│   ├── *.stdout.log / *.stderr.log
│
├── tests/
│   └── test_notifications.py    # Pytest-тесты
│
├── utils/                       # Утилиты и вспомогательные скрипты
│   ├── cache_writer.py
│   ├── cleanup_db.py
│   ├── cleanup_loop.sh
│   ├── form_match_card.py       # Формирование текста и клавиатуры матча
│   ├── logging_config.py
│   ├── match_cacher.py          # Фоновая загрузка матчей в кэш
│   ├── matches_cache_reader.py  # Чтение матчей из кэша
│   ├── pandascore.py            # Работа с PandaScore API (в т.ч. форматирование времени)
│   └── telegram_messenger.py    # Единая логика отправки карточек матчей
│
├── .env                         # Переменные окружения (tokenы, настройки)
├── .gitignore                   # Исключения Git
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── deploy.sh                    # Скрипт деплоя на сервер
├── requirements.txt
├── supervisord.conf             # Настройка процессов (bot, notifications, match_cacher)
└── README.md                    # Описание проекта (этот файл)
```

---

## 📌 Описание проекта

**CS Upcoming Matches Bot** — Telegram-бот, присылающий уведомления о ближайших, текущих и завершённых матчах по Counter-Strike 2 (CS2), с данными от [PandaScore API](https://pandascore.co/).

### 🧹 Возможности

* `/start` — подписка и запуск бота
* `/next` — ближайшие матчи
* `/live` — текущие live-матчи (с кнопкой трансляции, если есть)
* `/recent` — завершённые матчи (с победителем)
* `/subscribe` — подписка на тир-1 турниры
* `/subscribe_all` — подписка на все турниры
* `/unsubscribe` — остановить уведомления

### ⚙️ Архитектура

* Все матчи кэшируются каждые 10 минут (`match_cacher.py`)
* Бот читает данные только из `matches.json`
* Уведомления рассылаются за 5 минут до начала матча
* Используется SQLite для хранения подписчиков и истории уведомлений
* Supervisor запускает бота, уведомления и матч-кэшер

---

## 🚀 Установка и запуск

### 1. Настройка переменных окружения

Создайте `.env` в корне:

```env
TELEGRAM_BOT_TOKEN=xxx
PANDASCORE_TOKEN=xxx
DEV_MODE=true
USE_MOCK_DATA=false
NOTIFY_INTERVAL_SECONDS=60
```

### 2. Сборка и запуск через Docker

```bash
make deploy
```

Выполнится:

* Git pull
* Резервная копия
* Пересборка контейнера
* Перезапуск Supervisor с ботом, уведомлениями и матч-кэшером

---

## 🧪 API (FastAPI) — локальная разработка

### Запуск API в Docker

```bash
make run-api
```

API будет доступен по адресу: `http://localhost:8080/api`.

Проверка здоровья:

```bash
curl http://localhost:8080/api/health
```

Доступные эндпоинты:

- `GET /api/matches/upcoming?tier=1|all&limit=50`
- `GET /api/matches/live?tier=1|all&limit=50`
- `GET /api/matches/recent?tier=1|all&limit=50`

### Тесты API

```bash
make test-api
```

