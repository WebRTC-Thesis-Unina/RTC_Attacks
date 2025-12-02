start:
	@cd node && npm i --no-bin-links fs express https socket.io
	@docker-compose up -d --build

stop:
	@docker-compose down
	@cd node && rm -r node_modules && rm package*.json

follow-coturn:
	@docker logs coturn --follow

start-stunner:
	@docker exec -it stunner sh