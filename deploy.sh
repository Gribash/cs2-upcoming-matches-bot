#!/bin/bash

set -e  # Остановить скрипт при ошибке
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DEPLOY_DIR="/root/cs2-bot"
BACKUP_DIR="/root/cs2-bot_backup/cs2-bot_$TIMESTAMP"
DEPLOY_LOG="/root/cs2-bot_deploys/deploy_$TIMESTAMP.log"

echo "=== 🚀 Начало деплоя: $TIMESTAMP ===" | tee -a "$DEPLOY_LOG"

# 1. Создание резервной копии
echo "📦 Создание резервной копии текущей версии..." | tee -a "$DEPLOY_LOG"
mkdir -p "$(dirname "$BACKUP_DIR")"
cp -r "$DEPLOY_DIR" "$BACKUP_DIR"
echo "✅ Резервная копия сохранена в $BACKUP_DIR" | tee -a "$DEPLOY_LOG"

# 2. Переход в директорию проекта и получение изменений
cd "$DEPLOY_DIR"
echo "⬇️ Получение изменений из Git..." | tee -a "$DEPLOY_LOG"
git reset --hard HEAD >> "$DEPLOY_LOG" 2>&1

# Удаление неотслеживаемого deploy.sh (если он не под git)
if ! git ls-files --error-unmatch deploy.sh >/dev/null 2>&1; then
  echo "🧹 Удаление незакоммиченного deploy.sh перед pull..." | tee -a "$DEPLOY_LOG"
  rm -f deploy.sh
fi

git pull origin main >> "$DEPLOY_LOG" 2>&1

# 3. Пересборка и перезапуск контейнера
echo "🔄 Перезапуск Docker..." | tee -a "$DEPLOY_LOG"
docker-compose down >> "$DEPLOY_LOG" 2>&1
docker-compose up --build -d >> "$DEPLOY_LOG" 2>&1

echo "✅ Деплой завершён успешно!" | tee -a "$DEPLOY_LOG"