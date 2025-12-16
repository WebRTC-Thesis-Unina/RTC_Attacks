DOCKER_COMPOSE := $(shell command -v docker-compose 2> /dev/null || echo "docker compose")

SSH_HOSTNAME ?= 
SSH_IP ?= 
SSH_KEY ?=

start:
	@SSH_HOSTNAME=$(SSH_HOSTNAME) SSH_IP=$(SSH_IP) SSH_KEY=$(SSH_KEY) $(DOCKER_COMPOSE) up -d --build

stop:
	@$(DOCKER_COMPOSE) down
