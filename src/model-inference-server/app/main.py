import mlflow
import pymysql
import numpy as np
from time import sleep
import os
import logging
from app.logging_setup import logging_setup

logging_setup()
logger = logging.getLogger(__name__)

MODEL_NAME = os.getenv("MODEL_NAME")
PREDICTION_INTERVAL = int(os.getenv("PREDICTION_INTERVAL"))

def get_db_config() -> dict:
    return {
        "host": os.getenv("DB_HOST"),
        "port": 3306,
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME"),
        "cursorclass": pymysql.cursors.DictCursor,
        "connect_timeout": 5,
        "read_timeout": 10,
        "write_timeout": 10,
    }

def parse_csv_numbers(value: str | None) -> list[float] | None:
    if value is None:
        return None
    text = value.strip()
    if text == "":
        return None
    items = []
    for part in text.split(","):
        if part is None:
            continue
        token = part.strip()
        if token == "":
            continue
        try:
            items.append(int(token))
        except ValueError:
            try:
                items.append(float(token))
            except ValueError:
                continue
    return items if items else None

def add_inference_result(inference_result: int):
    if not MODEL_NAME:
        raise RuntimeError("MODEL_NAME is required")

    select_query = (
        "SELECT name, last_inference_results "
        "FROM machines "
        "WHERE name = %s "
        "LIMIT 1"
    )
    update_query = (
        "UPDATE machines "
        "SET last_inference_results = %s "
        "WHERE name = %s"
    )

    conn = pymysql.connect(**get_db_config())

    try:
        with conn.cursor() as cursor:
            cursor.execute(select_query, (MODEL_NAME,))
            row = cursor.fetchone()

            if row is None:
                logger.warning("No machine row found for model %s", MODEL_NAME)
                return {"updated": False, "reason": "machine_not_found", "name": MODEL_NAME}

            current = parse_csv_numbers(row.get("last_inference_results")) or []
            if len(current) >= 10:
                current.pop(0)
            current.append(inference_result)
            serialized = ",".join(str(value) for value in current)

            cursor.execute(update_query, (serialized, MODEL_NAME))
            conn.commit()

            return {
                "updated": cursor.rowcount > 0,
                "name": MODEL_NAME,
                "lastInferenceResults": current,
            }
    finally:
        conn.close()

model_uri = f"models:/{MODEL_NAME}/latest"
model = mlflow.sklearn.load_model(model_uri)
logger.info("Model loaded")

while True:
    X = np.array([[5.4, 3.4, 1.5]])
    predictions = model.predict(X)
    prediction_value = int(np.asarray(predictions).ravel()[0])
    update_result = add_inference_result(prediction_value)

    logger.info(f"Model Prediction: {predictions}, DB Update: {update_result}")
    sleep(PREDICTION_INTERVAL)
