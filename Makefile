PY_SRCS=src
RADON_MIN_MI=65

.PHONY: lint fmt type security cc mi check

lint:
	poetry run ruff check $(PY_SRCS) --fix

fmt:
	poetry run ruff format $(PY_SRCS)

type:
	poetry run mypy $(PY_SRCS)

security:
	poetry run bandit -r $(PY_SRCS) -lll -x venv,.venv,tests,migrations

cc:
	poetry run radon cc -s -a $(PY_SRCS)

mi:
	poetry run radon mi $(PY_SRCS)

check: lint fmt type security cc mi