import os

MODEL_NAME = os.getenv("MODEL_NAME")
PREDICTION_INTERVAL = int(os.getenv("PREDICTION_INTERVAL"))
SENSOR_DATA_ENDPOINT = "http://sensor-data-service/get_next_line"
