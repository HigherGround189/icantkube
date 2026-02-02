FROM ghcr.io/astral-sh/uv:python3.11-trixie-slim

WORKDIR /app

COPY pyproject.toml .

RUN uv sync

COPY main ./app

EXPOSE 80

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers", "--forwarded-allow-ips", "*"]
