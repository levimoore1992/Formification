.PHONY: setup migrate seed run

setup: ## Install dependencies with uv
	uv sync

migrate: ## Apply migrations to the sqlite database
	uv run python manage.py migrate

seed: ## Load mock demo data (users, forms, fields, rules, submissions)
	uv run python manage.py shell -c "import runpy; runpy.run_path('.seed_demo.py')"

run: ## Run the demo server
	uv run python manage.py runserver 0.0.0.0:8000