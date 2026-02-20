import requests
from app.constants import SENSOR_DATA_ENDPOINT, MODEL_NAME

def get_input_data():
    raw_input_data = requests.get(SENSOR_DATA_ENDPOINT, params={"name": MODEL_NAME})
    input = raw_input_data.json()["data"]
    input_array = list(input.values())[:-1]

    return input_array
