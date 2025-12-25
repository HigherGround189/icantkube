FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn

COPY app.py .
COPY dist ./dist

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
