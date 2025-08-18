# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    PIP_NO_CACHE_DIR=1

# Ensure Poetry is on PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

WORKDIR /app

# Copy only pyproject to leverage Docker layer caching
COPY pyproject.toml README.md ./

# Configure virtualenvs to be in-project
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# Install dependencies (no code yet for better caching)
RUN poetry install --no-root --no-ansi

# Now copy the rest
COPY src ./src
COPY tests ./tests

# Install the package itself
RUN poetry install --no-ansi

# Default command
CMD ["poetry", "run", "apicache", "--help"]
