start:
	@cd node && npm i --no-bin-links fs express https mongoose@5.7.4
	@docker-compose up -d --build

stop:
	@docker-compose down
	@cd node && rm -r node_modules && rm package*.json