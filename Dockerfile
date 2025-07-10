FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

# Установка Supervisor и зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        supervisor \
        inotify-tools && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Установка Python-зависимостей
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё содержимое проекта, включая supervisord.conf
COPY . /app

# Создание директории для логов Supervisor
RUN mkdir -p /app/logs

# Запуск Supervisor с конфигом в корне проекта
CMD ["/usr/bin/supervisord", "-c", "/app/supervisord.conf"]