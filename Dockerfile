# syntax=docker/dockerfile:1
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    PIP_NO_CACHE_DIR=1

ENV PATH="$POETRY_HOME/bin:$PATH"

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

# Leverage layer caching
COPY pyproject.toml poetry.lock* README.md ./

# In-project venv
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# Install deps (no code yet)
RUN poetry install --no-root --no-ansi

# Copy source (tests not needed in runtime image)
COPY src ./src

# Install the package itself (adds console script 'apicache')
RUN poetry install --no-ansi

# Make venv binaries available; no poetry needed at runtime
ENV PATH="/app/.venv/bin:${PATH}"

# Non-root user and writable data dir
RUN useradd -m app && mkdir -p /app/data && chown -R app:app /app
USER app

# Overridable defaults for cache/output
ENV APICACHE_OUTPUT_DIR="/app/data" \
    APICACHE_DB_PATH="/app/data/cache.db" \
    API_BASE_URL=""

# Default command
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["apicache-cli-av", "--help"]
