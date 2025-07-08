# ==== Настройки ====
PROJECT_DIR := $(shell pwd)
ENV_FILE := .env
SSH_USER := root
SSH_HOST := 31.130.149.146
SSH_PATH := /root/cs2-bot
DEPLOY_SCRIPT := deploy.sh

# ==== Локальная разработка ====

run:
	docker-compose --env-file $(ENV_FILE) up --build

stop:
	docker-compose down

logs:
	docker-compose logs -f

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

# ==== Деплой на сервер ====

deploy:
	ssh $(SSH_USER)@$(SSH_HOST) 'cd $(SSH_PATH) && ./$(DEPLOY_SCRIPT)'

# ==== Утилиты ====

status:
	git status

branches:
	git branch -a

whoami:
	@echo "Проект: $(PROJECT_DIR)"