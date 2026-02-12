import mlflow
import numpy as np
from time import sleep
import os
import logging
from app.logging_setup import logging_setup

logging_setup()
logger = logging.getLogger(__name__)

MODEL_NAME = os.getenv("MODEL_NAME")
PREDICTION_INTERVAL = int(os.getenv("PREDICTION_INTERVAL"))

model_uri = f"models:/{MODEL_NAME}/latest"
model = mlflow.sklearn.load_model(model_uri)
logger.info("Model loaded")

while True:
    X = np.array([[5.4, 3.4, 1.5]])
    predictions = model.predict(X)

    logger.info(f"Model Prediction: {predictions}")
    sleep(PREDICTION_INTERVAL)
