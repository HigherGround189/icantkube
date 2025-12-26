FROM python:3.11-slim

WORKDIR /app

RUN pip install --upgrade pip && pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY app.py .
COPY dist ./dist

CMD ["/app/.venv/bin/uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
