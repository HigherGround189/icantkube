FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

WORKDIR /app

COPY pyproject.toml .

RUN uv sync

COPY app ./app

RUN apt-get update && apt-get install -y micro

EXPOSE 80

CMD ["uv", "run", "python", "app/main.py"]
