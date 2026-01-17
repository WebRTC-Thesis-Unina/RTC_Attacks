DOCKER_COMPOSE := $(shell command -v docker-compose 2> /dev/null || echo "docker compose")

SERVICE ?= 

start:
	@$(DOCKER_COMPOSE) up -d

stop:
	@$(DOCKER_COMPOSE) down

start-attacks:
	@docker exec -it attacker sh

build:
	@$(DOCKER_COMPOSE) build $(SERVICE)