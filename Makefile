COMPOSE = docker compose -f infra/compose.yaml --env-file .env

up:
	$(COMPOSE) up

up-build:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

restart-%:
	$(COMPOSE) restart $*

build-%:
	$(COMPOSE) build $*
