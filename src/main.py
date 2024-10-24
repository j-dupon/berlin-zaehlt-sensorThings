import requests
import json
import time
from sync import sync
from TelraamAPI import TelraamAPI
from sensorThings_entities.Sensor import Sensor
from sensorThings_entities.ObservedProperty import ObservedProperty

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
	CONFIG = json.load(read_file)

with open("config/entities.json", mode="r", encoding="utf-8") as read_file:
	ENTITIES = json.load(read_file)

def check_sensorThings_connection():
	try: 
		request_result = requests.get(CONFIG["sensorThings_base_location"])
		if not request_result.ok:
			return 0
		return 1
	except:
		return 0

if __name__ == "__main__":

	if not check_sensorThings_connection():
		print("ERROR -> sync: not connected to sensorThingsAPI")
		exit()

	print("\n#######################################################")
	print("Initiate SensorThings API synchronization with Telraam")
	print("#######################################################\n")

	sensorThings_base_location = CONFIG["sensorThings_base_location"]

	# Get and/or add Sensors
	sensors = {}
	for sensor in ENTITIES["Sensors"].values():
		sensors[sensor["name"]] = Sensor(sensorThings_base_location, sensor)

	# Get and/or add ObservedProperties
	observed_properties = {}
	for observed_property in ENTITIES["ObservedProperties"].values():
		observed_properties[observed_property["name"]] = ObservedProperty(sensorThings_base_location, observed_property)

	telraam_api = TelraamAPI(CONFIG["telraam_key_header"], CONFIG["telraam_base_location"])

	while True:
		sync(telraam_api)
		time.sleep(CONFIG["sync_timer_in_seconds"])