# apicache

A tiny Typer-based CLI that fetches data from an API and caches results in SQLite using SQLModel.

## Features
- Typer CLI
- HTTPX for API requests
- SQLModel + SQLite cache
- Poetry for packaging
- Ruff/Black/Mypy for linting/formatting/types
- pytest + coverage
- Dockerized runtime

## Quickstart

1. Install Poetry
2. Install deps
3. Run the CLI

See detailed steps at the end.

## CLI Overview

The CLI provides a `fetch` command that hits a sample API (JSONPlaceholder by default) and caches results locally in `data/cache.db`.

```text
apicache fetch --resource posts --id 1
```

## Development

- Lint: `ruff check .` and `black .`
- Type-check: `mypy .`
- Test: `pytest`

## Docker

Build and run using the provided `Dockerfile`.

---

## Detailed setup

- Install Poetry
- `poetry install`
- `poetry run apicache --help`

