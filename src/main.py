import requests
import json
import time
from sync import sync
from sensorThings_entities.Sensor import Sensor
from sensorThings_entities.ObservedProperty import ObservedProperty
from sensorThings_entities.Thing import Thing


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
		print("ERROR -> main: not connected to sensorThingsAPI")
		exit()

	print("\n#######################################################")
	print("Initiate SensorThings API synchronization with Telraam")
	print("#######################################################\n")

	# Get things
	things = {}
	things_query_result = requests.get(f"{CONFIG['sensorThings_base_location']}/Things")
	for thing in things_query_result.json()["value"]:
		instance_id = thing["properties"]["instance_id"]
		things[instance_id] = Thing(instance_id)

	# Get and/or add Sensors
	sensors = {}
	for sensor in ENTITIES["Sensors"]:
		sensors[sensor] = Sensor(ENTITIES["Sensors"][sensor])

	# Get and/or add ObservedProperties
	observed_properties = {}
	for observed_property in ENTITIES["ObservedProperties"].values():
		observed_properties[observed_property["name"]] = ObservedProperty(observed_property)

	while True:
		if time.localtime().tm_min == 50:
			if time.localtime().tm_hour > 7 and time.localtime().tm_hour < 18:
				sync(things, sensors, observed_properties)
			else:
				print("main -> waiting for the sun to rise") 
			time.sleep(3000)
		else:
			time.sleep(55)
