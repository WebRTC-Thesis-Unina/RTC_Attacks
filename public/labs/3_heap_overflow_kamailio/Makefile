DOCKER_COMPOSE := $(shell command -v docker-compose 2> /dev/null || echo "docker compose")

start:
	@$(DOCKER_COMPOSE) up -d --build

stop:
	@$(DOCKER_COMPOSE) down

start-attacks:
	@docker exec -it sipp101 bash
