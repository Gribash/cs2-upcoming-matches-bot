up:
	docker-compose up --build

down:
	docker-compose down

logs:
	docker-compose logs -f --tail=100

rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up

bash:
	docker exec -it cs2_bot /bin/bash