DOCKER_COMPOSE := $(shell command -v docker-compose 2> /dev/null || echo "docker compose")

SERVICE ?=

start:
	@$(DOCKER_COMPOSE) up -d

stop:
	@$(DOCKER_COMPOSE) down

start-node:
	@docker exec -it node bash

build:
	@$(DOCKER_COMPOSE) build $(SERVICE)