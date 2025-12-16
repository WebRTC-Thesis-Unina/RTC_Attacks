DOCKER_COMPOSE := $(shell command -v docker-compose 2> /dev/null || echo "docker compose")

start:
	@$(DOCKER_COMPOSE) up -d --build

stop:
	@$(DOCKER_COMPOSE) down

start-wireshark:
	@docker exec -it wireshark wireshark

start-sippts:
	@docker exec -it sippts bash
