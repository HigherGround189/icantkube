FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

WORKDIR /machines-data

COPY pyproject.toml .

RUN uv sync

COPY app ./app

EXPOSE 80

CMD ["uv", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:80", "app.main:app", "-k", "uvicorn.workers.UvicornWorker"]
