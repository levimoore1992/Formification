.PHONY: setup migrate seed run lint

PY_SOURCES := $(shell find . -name '*.py' \
	-not -path './.venv/*' \
	-not -path './formification.egg-info/*' \
	-not -path '*/node_modules/*' \
	-not -path '*/dist/*' \
	-not -path './db.sqlite3')

setup: ## Install dependencies with uv
	uv sync

migrate: ## Apply migrations to the sqlite database
	uv run python manage.py migrate

seed: ## Load mock demo data (users, forms, fields, rules, submissions)
	uv run python manage.py shell -c "import runpy; runpy.run_path('.seed_demo.py')"

run: ## Run the demo server
	uv run python manage.py runserver 0.0.0.0:8000

lint: ## Format with black and lint with flake8 (mirrors the CI checks)
	uv run black $(PY_SOURCES)
	uv run flake8 $(PY_SOURCES) --ignore=E501,F405,W503

.PHONY: e2e e2e-setup

e2e-setup: ## Install Playwright's chromium (once)
	uv run playwright install chromium

e2e: ## Run browser tests against Django's isolated test database
	uv run pytest internal/e2e
