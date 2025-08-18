SHELL := bash

.PHONY: install lint format type test cov run

install:
	poetry install

lint:
	poetry run ruff check .

format:
	poetry run ruff check --fix .
	poetry run black .

type:
	poetry run mypy .

test:
	poetry run pytest -q

cov:
	poetry run pytest --cov=apicache --cov-report=term-missing

run:
	poetry run apicache --help
