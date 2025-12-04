start:
	@cd node && npm i --no-bin-links express http socket.io socket.io-file@2.0.31 path
	@docker-compose up -d --build

stop:
	@docker-compose down
	@cd node && rm -r node_modules && rm package*.json