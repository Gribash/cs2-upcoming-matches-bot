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