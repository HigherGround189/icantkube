import mlflow
import numpy as np
from time import sleep
import os

MODEL_NAME = os.getenv("MODEL_NAME")

model_uri = f"models:/{MODEL_NAME}/latest"
model = mlflow.sklearn.load_model(model_uri)
print("Model loaded")

while True:
    X = np.array([[5.4, 3.4, 1.5]])
    predictions = model.predict(X)

    print(f"Model Prediction: {predictions}")
    sleep(5)

