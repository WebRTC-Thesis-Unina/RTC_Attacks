DOCKER_COMPOSE := $(shell command -v docker-compose 2> /dev/null || echo "docker compose")

SERVICE ?=

start:
	@$(DOCKER_COMPOSE) up -d

stop:
	@$(DOCKER_COMPOSE) down

follow-coturn:
	@docker logs coturn --follow

start-stunner:
	@docker exec -it stunner sh

build:
	@$(DOCKER_COMPOSE) build $(SERVICE)