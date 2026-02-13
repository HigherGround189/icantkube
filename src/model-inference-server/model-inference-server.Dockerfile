FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

WORKDIR /app

COPY pyproject.toml .

RUN uv sync

COPY app ./app

EXPOSE 80

CMD ["uv", "run", "python", "-m", "app.main"]
