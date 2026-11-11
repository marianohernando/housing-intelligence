SHELL := /bin/bash
.DEFAULT_GOAL := help
-include .env
POSTGRES_PORT ?= 5440
DATABASE_URL ?= postgresql+psycopg://housing:housing@localhost:$(POSTGRES_PORT)/housing
TEST_DATABASE_URL ?= postgresql+psycopg://housing:housing@localhost:$(POSTGRES_PORT)/housing_test
export

ALEMBIC := uv run alembic -c infra/migrations/alembic.ini
GATE ?= 00

.PHONY: help dev up down logs migrate migrate-down seed lint format typecheck test test-unit test-db \
        schemas catalog-validate catalog-harvest catalog-draft catalog-curate ingest ingest-all features supabase-migrate supabase-sync secret-scan evidence ci web-install

help: ## Show targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'

dev: up migrate seed ## Boot db+redis, migrate and seed
	@echo "Postgres: localhost:$${POSTGRES_PORT:-5440}  Redis: localhost:$${REDIS_PORT:-6390}"

up: ## Start db and redis
	docker compose up -d --wait db redis

down: ## Stop local services
	docker compose down

logs: ## Tail service logs
	docker compose logs -f

migrate: ## Apply migrations to DATABASE_URL
	$(ALEMBIC) upgrade head

migrate-down: ## Revert last migration
	$(ALEMBIC) downgrade -1

seed: ## Sync catalog YAML into registry tables
	uv run hi-ingest catalog sync

lint: ## Ruff + ESLint
	uv run ruff check .
	uv run ruff format --check .
	@if [ -d node_modules ]; then npm run -w apps/web lint; else echo "skip web lint (run npm ci)"; fi

format: ## Auto-format Python
	uv run ruff format .
	uv run ruff check --fix .

typecheck: ## Pyright + tsc
	uv run pyright
	@if [ -d node_modules ]; then npm run -w apps/web typecheck; else echo "skip web typecheck (run npm ci)"; fi

test: test-unit test-db ## All tests

test-unit: ## Unit + data contract tests (no DB, no network)
	uv run pytest tests/unit tests/data -q
	@if [ -d node_modules ]; then npm run -w apps/web test -- --run; else echo "skip web tests (run npm ci)"; fi

test-db: ## Integration tests against TEST_DATABASE_URL
	uv run pytest -m db tests/integration -q

schemas: ## Regenerate JSON Schemas from Pydantic contracts
	uv run python scripts/export_schemas.py

catalog-validate: ## Validate every catalog YAML
	uv run pytest tests/data -q

catalog-harvest: ## Harvest candidate datasets (SOURCE=ckan_cm for one)
	uv run hi-ingest catalog harvest $(if $(SOURCE),--source $(SOURCE),--all)

catalog-draft: ## Score candidates and write dataset drafts + report
	uv run hi-ingest catalog draft

catalog-curate: ## Apply curation files (candidates -> curated datasets)
	for f in data/catalog/curation/*.yaml; do uv run hi-ingest catalog curate $$f; done

ingest: ## Run a dataset pipeline: make ingest DATASET=cm_secciones_censales
	@test -n "$(DATASET)" || (echo "DATASET is required" && exit 2)
	uv run hi-ingest run $(DATASET)

ingest-all: ## Geography + every declared pipeline, then features
	uv run hi-ingest run-all
	uv run hi-features compute

features: ## Recompute every feature (Gold)
	uv run hi-features compute

supabase-migrate: ## Apply migrations to SUPABASE_DATABASE_URL
	@test -n "$(SUPABASE_DATABASE_URL)" || (echo "SUPABASE_DATABASE_URL is required (.env)" && exit 2)
	@$(ALEMBIC) -x url="$(SUPABASE_DATABASE_URL)" upgrade head

supabase-sync: ## Copy local tables to Supabase: make supabase-sync PROFILE=demo|full
	@test -n "$(SUPABASE_DATABASE_URL)" || (echo "SUPABASE_DATABASE_URL is required (.env)" && exit 2)
	scripts/supabase_sync.sh $(or $(PROFILE),demo)

secret-scan: ## gitleaks over full git history (requires gitleaks binary)
	gitleaks git --config .gitleaks.toml --redact --no-banner .

evidence: ## Generate evidence folder: make evidence GATE=00
	uv run python scripts/evidence.py --gate $(GATE)

web-install: ## Install JS deps
	npm ci

ci: lint typecheck test-unit secret-scan ## Local equivalent of PR CI
