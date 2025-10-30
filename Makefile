DOCKER_COMPOSE := docker compose
ENV ?= dev
DOCKER_COMPOSE_FILE := $(if $(filter prod,$(ENV)),-f docker-compose.prod.yml,-f docker-compose.yml)
DOCKER_COMPOSE_CMD := $(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FILE)

.PHONY: up build down stop exec logs ps reup migrate help

## -----------------------------
## Base Commands
## -----------------------------

up:
	$(DOCKER_COMPOSE_CMD) up -d

build:
	$(DOCKER_COMPOSE_CMD) build --no-cache

down:
	$(DOCKER_COMPOSE_CMD) down

stop:
	$(DOCKER_COMPOSE_CMD) stop

## -----------------------------
## Utility Commands
## -----------------------------

exec:
	$(DOCKER_COMPOSE_CMD) exec app bash

logs:
	$(DOCKER_COMPOSE_CMD) logs -f app

ps:
	$(DOCKER_COMPOSE_CMD) ps

reup: down up

## -----------------------------
## Migration
## -----------------------------

migrate:
	$(DOCKER_COMPOSE_CMD) run --rm migrate

## -----------------------------
## Help
## -----------------------------

help:
	@echo "Usage: make [target] [ENV=dev|prod]"
	@echo ""
	@echo "Targets:"
	@echo "  up        Start containers (default: dev)"
	@echo "  build     Build containers without cache"
	@echo "  down      Stop and remove containers, networks, and volumes"
	@echo "  stop      Stop containers only"
	@echo "  exec      Enter app container bash shell"
	@echo "  logs      Show app logs"
	@echo "  ps        Show container status"
	@echo "  reup      Restart environment (down + up)"
	@echo "  migrate   Run Alembic migrations"
	@echo ""
	@echo "Examples:"
	@echo "  make up              # Start dev environment"
	@echo "  make up ENV=prod     # Start prod environment"
	@echo "  make migrate ENV=prod"
