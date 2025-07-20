#!/bin/sh
while true; do
  echo "Запуск очистки базы: $(date)"
  python utils/cleanup_db.py
  sleep 86400  # 24 часа = 86400 секунд
done