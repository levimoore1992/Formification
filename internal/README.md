# Formulaic - Example Project

```shell
# Create a virtualenv and install dependencies (uses uv)
uv sync

# Apply migrations to the sqlite database and run the server
uv run python manage.py migrate
uv run python manage.py runserver 0.0.0.0:8000
```

```shell
# Create superuser for admin access
uv run python manage.py createsuperuser
```
