DOCKER_COMPOSE := docker compose
ENV ?= dev
DOCKER_COMPOSE_FILE := $(if $(filter prod,$(ENV)),-f docker-compose.prod.yml,-f docker-compose.yml)
DOCKER_COMPOSE_CMD := $(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FILE)

.PHONY: up build down stop exec logs ps reup migrate downgrade history heads current makemigration help

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

exec:
	$(DOCKER_COMPOSE_CMD) exec app /bin/bash

logs:
	$(DOCKER_COMPOSE_CMD) logs -f app

ps:
	$(DOCKER_COMPOSE_CMD) ps

reup: down up

## -----------------------------
## Alembic Migrations
## -----------------------------

# Apply all migrations
migrate:
	$(DOCKER_COMPOSE_CMD) run --rm migrate alembic upgrade head

# Rollback one step
downgrade:
	$(DOCKER_COMPOSE_CMD) run --rm migrate alembic downgrade -1

# Show migration history
history:
	$(DOCKER_COMPOSE_CMD) run --rm migrate alembic history

# Show current revision
current:
	$(DOCKER_COMPOSE_CMD) run --rm migrate alembic current

# Create a new migration (name required: e.g. make makemigration name=add_users)
makemigration:
	@if [ -z "$(name)" ]; then \
		echo "❌ ERROR: Please provide a migration name. Usage: make makemigration name=add_users"; \
		exit 1; \
	fi
	@echo "🆕 Creating new migration: $(name)"
	$(DOCKER_COMPOSE_CMD) run --rm migrate alembic revision --autogenerate -m "$(name)"

## -----------------------------
## Help
## -----------------------------

help:
	@echo "Usage: make [target] [ENV=dev|prod]"
	@echo ""
	@echo "Targets:"
	@echo "  up              Start containers (default: dev)"
	@echo "  build           Build containers without cache"
	@echo "  down            Stop and remove containers, networks, and volumes"
	@echo "  stop            Stop containers only"
	@echo "  exec            Enter app container shell"
	@echo "  logs            Show app logs"
	@echo "  ps              Show container status"
	@echo "  reup            Restart environment (down + up)"
	@echo ""
	@echo "Migration commands:"
	@echo "  migrate         Run Alembic upgrade head"
	@echo "  downgrade       Rollback one migration step"
	@echo "  history         Show migration history"
	@echo "  current         Show current DB revision"
	@echo "  makemigration   Create new migration (usage: make makemigration name=add_users)"
	@echo ""
	@echo "Examples:"
	@echo "  make migrate ENV=prod"
	@echo "  make downgrade ENV=dev"
	@echo "  make makemigration name=add_user_table"
