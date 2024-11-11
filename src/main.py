import requests
import json
import time
from sync import sync
from sensorThings_entities.Sensor import Sensor
from sensorThings_entities.ObservedProperty import ObservedProperty
from sensorThings_entities.Thing_V2 import Thing


with open("config/config.json", mode="r", encoding="utf-8") as read_file:
	CONFIG = json.load(read_file)

with open("config/telraam_entities.json", mode="r", encoding="utf-8") as read_file:
	TELRAAM_ENTITIES = json.load(read_file)

def check_sensorThings_connection():
	try: 
		request_result = requests.get(CONFIG["sensorThings_base_location"])
		if not request_result.ok:
			return 0
		return 1
	except:
		return 0

def init_telraam():

	# Get things
	things = {}
	things_query_result = requests.get(f"{CONFIG['sensorThings_base_location']}/Things")
	for thing in things_query_result.json()["value"]:
		if "instance_id" in thing["properties"]:			
			instance_id = thing["properties"]["instance_id"]
			things[instance_id] = Thing(instance_id)

	# Get and/or add Sensors
	sensors = {}
	for sensor in TELRAAM_ENTITIES["Sensors"]:
		sensors[sensor] = Sensor(TELRAAM_ENTITIES["Sensors"][sensor])

	# Get and/or add ObservedProperties
	observed_properties = {}
	for observed_property in TELRAAM_ENTITIES["ObservedProperties"].values():
		observed_properties[observed_property["name"]] = ObservedProperty(observed_property)

	return {"things": things, "sensors": sensors, "observed_properties": observed_properties}

if __name__ == "__main__":

	if not check_sensorThings_connection():
		print("ERROR -> main: not connected to sensorThingsAPI")
		exit()

	print("\n##########################################")
	print("Initiate SensorThings API synchronization")
	print("##########################################\n")

	telraam_initialization = init_telraam()

	while True:
		if time.localtime().tm_min == 50:
			if time.localtime().tm_hour > 7 and time.localtime().tm_hour < 18:
				sync(telraam_initialization["things"], telraam_initialization["sensors"], telraam_initialization["observed_properties"])
			else:
				print("main -> waiting for the sun to rise") 
			time.sleep(3000)
		else:
			time.sleep(55)
