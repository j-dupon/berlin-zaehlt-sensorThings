import Telraam.sync_telraam as telraam
import logger
import requests
import json
import sensorThings_entities

LOGGER = logger.log

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
	CONFIG = json.load(read_file)

with open("Telraam/telraam_entities.json", mode="r", encoding="utf-8") as read_file:
	TELRAAM_ENTITIES = json.load(read_file)

def check_sensorThings_connection():
	try: 
		res = requests.get(CONFIG["sensorThings_base_location"])
		if not res.ok:
			return 0
		return 1
	except:
		return 0
	
if __name__ == "__main__":

	if not check_sensorThings_connection():
		LOGGER.err.error("ERROR -> sync: not connected to sensorThingsAPI")
		exit()

	# Get things
	things = {}
	things_query_result = requests.get(f"{CONFIG['sensorThings_base_location']}/Things")
	for thing in things_query_result.json()["value"]:
		if "instance_id" in thing["properties"]:			
			instance_id = thing["properties"]["instance_id"]
			things[instance_id] = sensorThings_entities.Thing(instance_id)

	# Get and/or add Sensors
	sensors = {}
	for sensor in TELRAAM_ENTITIES["Sensors"]:
		sensors[sensor] = sensorThings_entities.Sensor(TELRAAM_ENTITIES["Sensors"][sensor])

	# Get and/or add ObservedProperties
	observed_properties = {}
	for observed_property in TELRAAM_ENTITIES["ObservedProperties"].values():
		observed_properties[observed_property["name"]] = sensorThings_entities.ObservedProperty(observed_property)	

	telraam.sync(things, sensors, observed_properties)