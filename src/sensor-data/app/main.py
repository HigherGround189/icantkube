import csv
import random
from fastapi import FastAPI, HTTPException
import redis
import logging
import boto3
import threading
import os
import io
from contextlib import asynccontextmanager


logger = logging.getLogger(__name__)


S3_ENDPOINT = "http://rustfs"
BUCKET = "datasets"
REDIS_KEY_PREFIX = "csv_last_index"

@asynccontextmanager
async def lifespan(app: FastAPI):

    response = s3.list_objects_v2(Bucket=BUCKET)

    if "Contents" not in response:
        raise RuntimeError("No files found in bucket")

    for obj in response["Contents"]:
        key = obj["Key"]

        if not key.lower().endswith(".csv"):
            continue

        name = os.path.splitext(os.path.basename(key))[0]
        logger.info(f"Loading CSV: {name}")

        csv_obj = s3.get_object(Bucket=BUCKET, Key=key)
        body = csv_obj["Body"].read()

        reader = list(
            csv.DictReader(io.StringIO(body.decode("utf-8")))
        )

        if not reader:
            logger.warning(f"{name} is empty, skipping")
            continue

        CSV_DATA[name] = reader

        if r and not r.exists(redis_key(name)):
            r.set(redis_key(name), random.randint(0, len(reader) - 1))

    if not CSV_DATA:
        raise RuntimeError("No CSVs loaded")

    logger.info(f"Loaded datasets: {list(CSV_DATA.keys())}")

    yield  

    logger.info("Shutting down app")


app = FastAPI(title="CSV with Redis + RustFS",
              lifespan=lifespan)

CSV_DATA: dict[str, list[dict]] = {}
lock = threading.Lock()


def connect_redis(db=0):
    candidates = [
        {"host": "redis", "port":6379} 
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

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=os.environ.get("access_key_id"),
    aws_secret_access_key=os.environ.get("secret_access_key"),
)

def redis_key(name: str) -> str:
    return f"{REDIS_KEY_PREFIX}:{name}"


def get_last_index(name: str, size: int) -> int:
    if not r:
        return random.randint(0, size - 1)

    key = redis_key(name)
    val = r.get(key)

    if val is None:
        idx = random.randint(0, size - 1)
        r.set(key, idx)
        return idx

    return int(val)



def set_last_index(name: str, idx: int):
    if r:
        r.set(redis_key(name), idx)


@app.get("/get_next_line")
def get_next_line(name: str):
    if name not in CSV_DATA:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset '{name}' not found",
        )

    rows = CSV_DATA[name]

    with lock:
        idx = get_last_index(name, len(rows))
        line = rows[idx]

        next_idx = idx + 1
        if next_idx >= len(rows):
            next_idx = random.randint(0, len(rows) - 1)

        set_last_index(name, next_idx)

    return {
        "dataset": name,
        "row_index": idx,
        "data": line,
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "datasets": {
            name: {
                "rows": len(rows),
                "last_index": (
                    r.get(redis_key(name)) if r else "redis_disabled"
                ),
            }
            for name, rows in CSV_DATA.items()
        },
    }