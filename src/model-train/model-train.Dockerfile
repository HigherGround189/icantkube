FROM ghcr.io/astral-sh/uv:python3.11-trixie-slim

WORKDIR /model-train

COPY pyproject.toml .

RUN uv sync

COPY app ./app

EXPOSE 80

CMD ["uv", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:80", "app.main:app"]