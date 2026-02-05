import redis
import os
import mlflow
import minio

from app.logging import logging_setup
logging_setup()
import logging
logger = logging.getLogger(__name__)

from app.config import load_apps

APPS = load_apps()

def connect_redis(db: int=0):
    """
    Find connection to redis database
    
    db: int
        Number (index) of the database to connect within redis.
    """
    redis_con = APPS["redis-connection"]

    candidates = [
        {"host": redis_con["url"], "port":redis_con["port"]},
        {"host": "localhost", "port":6370} # local testing
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

def connect_mlflow():
    """
    Find connection to mlflow
    """
    os.environ['MLFLOW_TRACKING_USERNAME'] = os.environ.get("username", '')
    os.environ['MLFLOW_TRACKING_PASSWORD'] = os.environ.get("password", '')

    mlflow_con = APPS["mlflow-connection"]

    candidates = [
        {"host": mlflow_con["url"]},
        {"host": "http://localhost:5200"} # local testing
    ]
    for i, uri in enumerate(candidates):
        try:
            mlflow.set_tracking_uri(uri["host"])
            experiments = mlflow.search_experiments(max_results=1)
            if experiments:
                logger.info(f"Connected to MLflow Succefully!")
                return True
        except Exception as e:
            logger.warning(f"Failed to connect to MLflow: {uri["host"]}: {e}")
            if i < len(candidates) - 1:
                logger.info("Trying next MLFlow candidate...")

    logger.warning("MLflow unavailable, continuing without tracking")
    return False

def connect_minio():
    """
    Find connection to MinIO database
    """
    access_key = os.environ.get("access_key_id")
    secret_key = os.environ.get("secret_access_key")

    minio_con = APPS["minio-connection"]

    candidates = [
        {"host": minio_con["url"]}
    ]
    for i, cfg in enumerate(candidates):
        try:
            m = minio.Minio(
                **cfg,
                access_key=access_key,
                secret_key=secret_key,
                http=False,
            )
            response = m.list_buckets()
            if response:
                logger.info(f"Connected to MinIO Successfully at {cfg["host"]}")
                return m
        except minio.ConnectionError as conerr:
            logger.warning(f"Failed to connect to MinIO at {cfg["host"]}: {conerr}")
            if i < len(candidates) - 1:
                logger.info("Trying next MinIO candidate...")

    logger.warning("MinIO unavailable, continuing without tracking")
    return None