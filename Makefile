PY_SRCS=src
RUFF_SRCS=src tests
RADON_MIN_MI=65

.PHONY: install check-env migrate run test test-cov lint lint-fix fmt fmt-check type security cc mi check compose-up compose-down compose-logs compose-ps wsl-check wsl-up

# Установить основные и dev-зависимости проекта через Poetry.
install:
	poetry install --with dev

# Проверить, что все обязательные Python-зависимости доступны.
check-env:
	@poetry run python -c "import django, pydantic, pydantic_settings, psycopg, pytest, pytest_django, rest_framework" || (echo "Не установлены зависимости. Выполните: make install"; exit 1)

# Применить все неприменённые миграции базы данных.
migrate:
	poetry run python src/manage.py migrate

# Запустить локальный Django-сервер на порту 9000.
run:
	poetry run python src/manage.py runserver 0.0.0.0:9000

# Запустить весь набор автоматических тестов.
test:
	poetry run pytest

# Запустить тесты и вывести отчёт о покрытии кода.
test-cov:
	poetry run pytest --cov=src --cov-report=term-missing

# Проверить исходный код линтером Ruff.
lint:
	poetry run ruff check $(RUFF_SRCS)

# Автоматически исправить найденные Ruff проблемы в коде.
lint-fix:
	poetry run ruff check $(RUFF_SRCS) --fix

# Отформатировать исходный код и тесты с помощью Ruff.
fmt:
	poetry run ruff format $(RUFF_SRCS)

# Проверить форматирование без изменения файлов.
fmt-check:
	poetry run ruff format --check $(RUFF_SRCS)

# Проверить типы Python-кода с помощью mypy.
type:
	poetry run mypy $(PY_SRCS)

# Выполнить статический анализ безопасности Bandit.
security:
	poetry run bandit -r $(PY_SRCS) -lll -x venv,.venv,tests,migrations

# Проверить цикломатическую сложность функций и модулей.
cc:
	poetry run radon cc -s -a $(PY_SRCS)

# Проверить индекс сопровождаемости исходного кода.
mi:
	poetry run radon mi $(PY_SRCS)

# Выполнить полный quality gate: зависимости, линтинг, форматирование, типы,
# безопасность, метрики сложности и все тесты.
check: check-env lint fmt-check type security cc mi test

# Собрать образы и запустить приложение с PostgreSQL через Docker Compose.
compose-up:
	docker compose -f docker-compose.yaml up --build

# Остановить контейнеры Docker Compose, сохранив данные volume.
compose-down:
	docker compose -f docker-compose.yaml down

# Показать потоковые логи контейнеров приложения и базы данных.
compose-logs:
	docker compose -f docker-compose.yaml logs -f web db

# Показать состояние контейнеров Docker Compose.
compose-ps:
	docker compose -f docker-compose.yaml ps

# Проверить окружение WSL, Docker и Docker Compose.
wsl-check:
	bash scripts/wsl-check.sh

# Проверить окружение WSL и запустить приложение через Docker Compose.
wsl-up: wsl-check
	docker compose -f docker-compose.yaml up --build
