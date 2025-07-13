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

# Копируем всё содержимое проекта
COPY . /app

# Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Создание директории для логов Supervisor
RUN mkdir -p /app/logs

# Запуск Supervisor
CMD ["/usr/bin/supervisord", "-c", "/app/supervisord.conf"]