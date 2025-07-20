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
	rm -f ./data
	scp $(SSH_USER)@$(SSH_HOST):$(SSH_PATH)/data/subscribers.db ./data

get-cache:
	rm -rf ./cache
	scp -r $(SSH_USER)@$(SSH_HOST):$(SSH_PATH)/cache ./cache

refresh-cache:
	ssh $(SSH_USER)@$(SSH_HOST) '\
		cd $(SSH_PATH) && \
		rm -rf cache/* && \
		docker-compose exec -T bot python utils/refresh_cache.py \
	'

# ✅ Запуск всех тестов
test:
	pytest tests/ -v --color=yes --tb=short

# ✅ Покрытие кода (coverage) по модулям bot и utils
coverage:
	pytest --cov=bot --cov=utils tests/ --cov-report=term-missing