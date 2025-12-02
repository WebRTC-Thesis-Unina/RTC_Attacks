start:
	@docker compose up -d --build

stop:
	@docker compose down

follow-coturn:
	@docker logs coturn --follow

start-stunner:
	@docker exec -it stunner sh