import mlflow
import numpy as np
from time import sleep
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

MODEL_NAME = os.getenv("MODEL_NAME")

model_uri = f"models:/{MODEL_NAME}/latest"
model = mlflow.sklearn.load_model(model_uri)
logger.info("Model loaded")

while True:
    X = np.array([[5.4, 3.4, 1.5]])
    predictions = model.predict(X)

    logger.info(f"Model Prediction: {predictions}")
    sleep(5)
