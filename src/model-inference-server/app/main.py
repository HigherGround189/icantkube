import os
import mlflow
import logging
import numpy as np
from time import sleep
from app.logging_setup import logging_setup
from app.database import add_inference_result
from app.sensor_data import get_input_data

logging_setup()
logger = logging.getLogger(__name__)

MODEL_NAME = os.getenv("MODEL_NAME")
PREDICTION_INTERVAL = int(os.getenv("PREDICTION_INTERVAL"))

model_uri = f"models:/{MODEL_NAME}/latest"
model = mlflow.sklearn.load_model(model_uri)
logger.info("Model loaded")

while True:
    X = get_input_data()
    predictions = model.predict(X)
    prediction_value = int(np.asarray(predictions).ravel()[0])
    update_result = add_inference_result(prediction_value)

    logger.info(f"Model Prediction: {predictions}, DB Update: {update_result}")
    sleep(PREDICTION_INTERVAL)
