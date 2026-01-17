DOCKER_COMPOSE := $(shell command -v docker-compose 2> /dev/null || echo "docker compose")

SERVICE ?=

start:
	@$(DOCKER_COMPOSE) up -d

stop:
	@$(DOCKER_COMPOSE) down

start-wireshark:
	@docker exec -it wireshark wireshark

start-sippts:
	@docker exec -it sippts bash

build:
	@$(DOCKER_COMPOSE) build $(SERVICE)