FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency metadata first (better layer caching)
COPY pyproject.toml .

# Install dependencies
RUN uv pip install --system --no-cache fastapi uvicorn httpx pyyaml

# Copy application code
COPY app ./app
COPY services.yaml .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
