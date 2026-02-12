import requests

MACHINE_DATA_ENDPOINT = "http://machines-data/all"
SENSOR_DATA_ENDPOINT = "http://sensor-data-service/get_next_line"

machines_list = requests.get(MACHINE_DATA_ENDPOINT)
print(machines_list)
