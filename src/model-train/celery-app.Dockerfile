FROM ghcr.io/astral-sh/uv:python3.11-trixie-slim

WORKDIR /model-train

COPY pyproject.toml .

RUN uv sync

COPY app ./app

CMD ["uv", "run", "celery", "-A", "app.tasks", "worker", "-l", "info", "-c", "4"]