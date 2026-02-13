import requests

SENSOR_DATA_ENDPOINT = "http://sensor-data-service/get_next_line"

machines_list = requests.get(SENSOR_DATA_ENDPOINT, params={"name": "Wittman"})
print(machines_list)
