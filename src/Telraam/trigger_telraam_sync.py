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

def sensorThings_entities_from_api(entity_name, id_filter):
	count = requests.get(f"{CONFIG['sensorThings_base_location']}/{entity_name}?$count=true")
	query_top =  count.json()["@iot.count"]
	query_filter = f"$filter=properties/{id_filter} ne ''"
	query_result = requests.get(f"{CONFIG['sensorThings_base_location']}/{entity_name}?$top={query_top}&{query_filter}")

	entities = {}
	for entity in query_result.json()['value']:
		if id_filter in entity["properties"] and entity_name == "Things":
			entities[entity['properties'][id_filter]] = sensorThings_entities.Thing(entity["properties"]["unique_allocator"])
		if id_filter in entity["properties"] and entity_name == "Locations":
			entities[entity['properties'][id_filter]] = sensorThings_entities.Location(entity["properties"]["unique_allocator"])
	return entities

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
		LOGGER.err.error("sync: not connected to sensorThingsAPI")
		exit()

	# Get and/or add Sensors
	sensors = {}
	for sensor in TELRAAM_ENTITIES["Sensors"]:
		sensors[sensor] = sensorThings_entities.Sensor(TELRAAM_ENTITIES["Sensors"][sensor])

	# Get and/or add ObservedProperties
	observed_properties = {}
	for observed_property in TELRAAM_ENTITIES["ObservedProperties"].values():
		observed_properties[observed_property["name"]] = sensorThings_entities.ObservedProperty(observed_property)	

	things = sensorThings_entities_from_api("Things", "instance_id")
	locations = sensorThings_entities_from_api("Locations", "segment_id")

	telraam.sync(sensors, observed_properties, things, locations)