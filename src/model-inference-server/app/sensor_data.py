import requests

SENSOR_DATA_ENDPOINT = "http://sensor-data-service/get_next_line"

def get_input_data():
    raw_input_data = requests.get(SENSOR_DATA_ENDPOINT, params={"name": "Wittman"})
    input = raw_input_data.json()["data"]
    input_array = list(input.values())

    return input_array
