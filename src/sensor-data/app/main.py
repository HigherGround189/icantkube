import csv
import random
from fastapi import FastAPI
import redis
import logging
logger = logging.getLogger(__name__)

CSV_FILE = "/machines/iris.csv"
REDIS_KEY = "csv_last_index"

# Load CSV into memory
with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = list(csv.DictReader(f))
    if not reader:
        raise ValueError("CSV is empty or has no headers")
    CSV_LINES = reader

app = FastAPI(title="CSV Sequential with Redis")

def connect_redis(db=0):
    candidates = [
        {"host": "redis-master.redis.svc.cluster.local", "port":6379},
        {"host": "redis", "port":6379} # local testing
    ]
    for i, cfg in enumerate(candidates):
        try:
            r = redis.Redis(
                **cfg,
                socket_connect_timeout=5,
                socket_timeout=5,
                decode_responses=True,
                db=db
            )
            response = r.ping()
            if response:
                logger.info(f"Connected to Redis Successfully at {cfg["host"]}:{cfg["port"]}")
                return r
        except redis.ConnectionError as conerr:
            logger.warning(f"Failed to connect to Redis at {cfg["host"]}:{cfg["port"]}: {conerr}")
            if i < len(candidates) - 1:
                logger.info("Trying next redis candidate...")

    logger.warning("Redis unavailable, continuing without tracking")
    return None

r = connect_redis()


def get_last_index():
    """Get the last index from Redis or pick a random one if not set."""
    last_index = r.get(REDIS_KEY)
    if last_index is None:
        last_index = random.randint(0, len(CSV_LINES) - 1)
        r.set(REDIS_KEY, last_index)
    else:
        last_index = int(last_index)
    return last_index


def set_last_index(idx: int):
    """Save the last index to Redis."""
    r.set(REDIS_KEY, idx)


@app.get("/next_line")
def next_line():
    """
    Return the next CSV line sequentially, starting with a random line on first request.
    Wraps around and updates Redis.
    """
    last_index = get_last_index()
    line = CSV_LINES[last_index]

    # Increment index and wrap around randomly when end reached
    next_index = last_index + 1
    if next_index >= len(CSV_LINES):
        next_index = random.randint(0, len(CSV_LINES) - 1)

    set_last_index(next_index)
    return line

@app.get("/health")
def health():
    """Show Redis stored index and total CSV lines."""
    last_index = get_last_index()
    return {"status": "ok", "lines_in_memory": len(CSV_LINES), "last_index": last_index}
