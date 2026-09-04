PY_SRCS=src
RUFF_SRCS=src tests
RADON_MIN_MI=65

.PHONY: install check-env migrate run test test-cov lint lint-fix fmt fmt-check type security cc mi check compose-up compose-down compose-logs compose-ps wsl-check wsl-up

install:
	poetry install --with dev

check-env:
	@poetry run python -c "import django, pydantic, pydantic_settings, psycopg, pytest, pytest_django, rest_framework" || (echo "Не установлены зависимости. Выполните: make install"; exit 1)

migrate:
	poetry run python src/manage.py migrate

run:
	poetry run python src/manage.py runserver 0.0.0.0:9000

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=src --cov-report=term-missing

lint:
	poetry run ruff check $(RUFF_SRCS)

lint-fix:
	poetry run ruff check $(RUFF_SRCS) --fix

fmt:
	poetry run ruff format $(RUFF_SRCS)

fmt-check:
	poetry run ruff format --check $(RUFF_SRCS)

type:
	poetry run mypy $(PY_SRCS)

security:
	poetry run bandit -r $(PY_SRCS) -lll -x venv,.venv,tests,migrations

cc:
	poetry run radon cc -s -a $(PY_SRCS)

mi:
	poetry run radon mi $(PY_SRCS)

check: check-env lint fmt-check type security cc mi test

compose-up:
	docker compose up --build

compose-down:
	docker compose down

compose-logs:
	docker compose logs -f web db

compose-ps:
	docker compose ps

wsl-check:
	bash scripts/wsl-check.sh

wsl-up: wsl-check
	docker compose up --build
