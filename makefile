# ==== Настройки ====
PROJECT_DIR := $(shell pwd)
ENV_FILE := .env
SSH_USER := root
SSH_HOST := cs2-vps
SSH_PATH := /root/cs2-bot
DEPLOY_SCRIPT := deploy.sh

# ==== Локальная разработка ====

run:
	docker-compose --env-file $(ENV_FILE) up --build

stop:
	docker-compose down

logs:
	docker-compose logs -f

run-api:
	docker-compose --env-file $(ENV_FILE) up --build api

stop-api:
	docker-compose stop api

shell:
	docker exec -it $$(docker ps -qf "name=cs2_bot") bash

env-check:
	@cat $(ENV_FILE)

# ==== Работа с git ====

create-feature:
ifndef name
	$(error ❌ Укажи имя фичи: make create-feature name=название)
endif
	git checkout -b feature/$(name)

push-dev:
	git checkout dev
	git add .
	git commit -m "⚙️ WIP: разработка"
	git push origin dev

merge-dev:
	git checkout main
	git merge dev
	git push origin main

pull-main:
	git checkout main
	git pull origin main

push-main:
	git checkout main
	git add .
	git commit -m "🚀 Обновление продакшена"
	git push origin main

# ==== Деплой ====

upload-deploy:
	scp deploy.sh $(SSH_USER)@$(SSH_HOST):$(SSH_PATH)/deploy.sh
	ssh $(SSH_USER)@$(SSH_HOST) "chmod +x $(SSH_PATH)/deploy.sh"

deploy: upload-deploy
	@echo "🚀 Выполняется деплой на сервер $(SSH_HOST)..."
	ssh $(SSH_USER)@$(SSH_HOST) 'cd $(SSH_PATH) && ./$(DEPLOY_SCRIPT)'
	@echo "📄 Логи деплоя доступны в каталоге /root/cs2-bot_deploys/"

sync-prod: pull-main merge-dev deploy

# ==== Утилиты ====

status:
	git status

branches:
	git branch -a

whoami:
	@echo "Проект: $(PROJECT_DIR)"

.PHONY: run stop logs shell env-check create-feature push-dev merge-dev pull-main push-main deploy sync-prod status branches whoami

clear-logs:
	ssh $(SSH_USER)@$(SSH_HOST) 'cd $(SSH_PATH)/logs && rm -f *.log *.err.log *.out.log'

get-logs:
	rm -rf ./logs
	scp -r $(SSH_USER)@$(SSH_HOST):$(SSH_PATH)/logs ./logs

get-data:
	rm -rf ./data
	scp -r $(SSH_USER)@$(SSH_HOST):$(SSH_PATH)/data ./data

get-cache:
	rm -rf ./cache
	scp -r $(SSH_USER)@$(SSH_HOST):$(SSH_PATH)/cache ./cache

refresh-cache:
	ssh $(SSH_USER)@$(SSH_HOST) '\
		cd $(SSH_PATH) && \
		rm -rf cache/* && \
		docker-compose exec -T bot python utils/refresh_cache.py \
	'

# Запуск всех тестов с логированием, доступным для caplog
test:
	PYTHONPATH=. LOG_PROPAGATE=1 pytest

test-api:
	PYTHONPATH=. LOG_PROPAGATE=1 pytest -q -k api

# Запуск тестов с покрытием
coverage:
	PYTHONPATH=. LOG_PROPAGATE=1 pytest --cov=bot --cov=utils tests/ --cov-report=term-missing

# ==== Публикация чистой ветки без node_modules ====

push-clean:
	# 1) Обновляем main и создаём/переписываем ветку cs2matches-online-clean от origin/main
	git fetch origin && \
	git checkout -B cs2matches-online-clean origin/main && \
	\
	# 2) Переносим изменения из текущей рабочей ветки (по умолчанию cs2matches-online)
	#    Добавляйте пути сюда при необходимости; node_modules и .next не затрагиваем
	git checkout cs2matches-online -- \
	  api \
	  web/app \
	  web/components \
	  web/lib \
	  web/package.json \
	  web/tsconfig.json \
	  web/next.config.mjs \
	  web/next-env.d.ts \
	  web/README.md \
	  requirements.txt \
	  docker-compose.yml \
	  makefile \
	  README.md \
	  .gitignore \
	  tests \
	  utils \
	  bot \
	  supervisord.conf \
	  Dockerfile \
	  deploy.sh \
	  cache \
	  .dockerignore \
	  pytest.ini \
	  CS_upcoming_matches_bot.code-workspace && \
	\
	# 3) Коммитим и пушим новую чистую ветку
	git add -A && \
	git commit -m "feat: API (FastAPI) + web (Next.js) scaffold; clean branch without node_modules" || true && \
	git push -u origin cs2matches-online-clean

# ==== Короткие команды пуша ====

push-current:
	# Пушим текущую ветку на origin (удобно, если уже на cs2matches-online-clean)
	git push -u origin HEAD

push-clean:
	# Гарантированно пушим именно cs2matches-online-clean
	@[ "$(shell git rev-parse --abbrev-ref HEAD)" = "cs2matches-online-clean" ] || \
		(echo "❌ Вы не в ветке cs2matches-online-clean" && exit 1)
	git push -u origin cs2matches-online-clean