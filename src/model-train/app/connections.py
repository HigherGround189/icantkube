import redis
import os
import mlflow
import minio
import boto3
from botocore.exceptions import ClientError

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
                logger.info("Trying next Redis candidate...")

    logger.error("Redis cannot be found unavailable")
    raise RuntimeError("Cannot connect to Redis")

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

    logger.error("MLflow cannot be found unavailable")
    raise RuntimeError("Cannot connect to MLflow")

def connect_rustfs():
    """
    Find connection to RustFS database
    """
    access_key = os.environ.get("access_key_id")
    secret_key = os.environ.get("secret_access_key")

    rustfs_con = APPS["rustfs-connection"]

    candidates = [
        {"endpoint_url": rustfs_con["url"]}
    ]
    for i, cfg in enumerate(candidates):
        try:
            s3 = boto3.client(
                "s3",
                **cfg,
                access_key=access_key,
                secret_key=secret_key,
                region_name=rustfs_con.get("region", "us-east-1"),
            )
            response = s3.list_buckets()
            if response:
                logger.info(f"Connected to RustFS Successfully at {cfg["host"]}")
                return s3
        except ClientError as conerr:
            logger.warning(f"Failed to connect to RustFS at {cfg["host"]}: {conerr}")
            if i < len(candidates) - 1:
                logger.info("Trying next RustFS candidate...")

    logger.error("RustFS cannot be found unavailable")
    raise RuntimeError("Cannot connect to RustFS")

def create_or_connect_bucket(client, bucket_name: str):
    """
    To create or connect to existing bucket in RustFS
    
    client: 
        RustFS connection
    bucket_name: str
        Name of bucket to be created or connected
    """
    try:
        client.head_bucket(Bucket=bucket_name)
        logger.info(f"Bucket exists: {bucket_name}")
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code in ("404"):
            logger.info(f"Bucket {bucket_name} not found. Creating...")
            client.create_bucket(Bucket=bucket_name)
            logger.info(f"Bucket created: {bucket_name}")
            return