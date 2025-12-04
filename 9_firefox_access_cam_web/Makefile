start:
	@cd node && npm i --no-bin-links express https ws fs path
	@docker-compose up -d --build

stop:
	@docker-compose down
	@cd node && rm -r node_modules && rm package*.json