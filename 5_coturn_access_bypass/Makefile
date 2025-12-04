DOCKER_COMPOSE := $(shell command -v docker-compose 2> /dev/null || echo "docker compose")

start:
	@$(DOCKER_COMPOSE) up -d --build

stop:
	@$(DOCKER_COMPOSE) down

follow-coturn:
	@docker logs coturn --follow

start-stunner:
	@docker exec -it stunner sh