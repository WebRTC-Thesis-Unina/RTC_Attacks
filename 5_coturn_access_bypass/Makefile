DOCKER_COMPOSE := $(shell command -v docker-compose 2> /dev/null || echo "docker compose")

start:
	@cd node && npm i --no-bin-links fs express https socket.io
	@$(DOCKER_COMPOSE) up -d --build

stop:
	@$(DOCKER_COMPOSE) down
	@cd node && rm -r node_modules && rm package*.json

follow-coturn:
	@docker logs coturn --follow

start-stunner:
	@docker exec -it stunner sh