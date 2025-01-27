import requests
import json
import time
import sensorThings_entities
from Telraam.TelraamAPI import TelraamAPI
from Telraam.day_night_cycle import berlin_daytime
import logger

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
	CONFIG = json.load(read_file)

with open("Telraam/telraam_entities.json", mode="r", encoding="utf-8") as read_file:
	TELRAAM_ENTITIES = json.load(read_file)

LOGGER = logger.log
TELRAAM_API = TelraamAPI(CONFIG["telraam_api_key"], CONFIG["telraam_api_key_fallback"], CONFIG["telraam_base_location"])

def get_sensorThings_entities(entity_name, id_filter):
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

def archive_outdated_entities(entites, entity_allocator, telraam_data):
	telraam_data = [instance["instance_id"] for instance in telraam_data] if entity_allocator == "instance_id" else telraam_data
	entity_name = "Things" if entity_allocator == "instance_id" else "Locations"

	for entity in entites:
		if entity not in telraam_data and not entites[entity].properties["deleted"]:
			LOGGER.log.info(f"sync@outdated: archived {entity_allocator}({entity})")
			requests.patch(
				f"{CONFIG['sensorThings_base_location']}/{entity_name}({entites[entity].iot_id()})", 
				data = json.dumps({
					"properties": {
						entity_allocator: f"_{entity}",
						"unique_allocator": f"_{entity}",
						"deleted": True
					}})
				)

def get_telraam_data():
	
	# Get a list of Telraam segments in Berlin
	telraam_snapshots = TELRAAM_API.get_traffic_snapshot(CONFIG["telraam_traffic_snapshot"])
	if not telraam_snapshots['ok']:
		LOGGER.err.error(f"sync: {telraam_snapshots['error_message']}")
		return 1

	telraam_segments_berlin = {}
	for snapshot in telraam_snapshots['result'].json()['features']:
		telraam_segments_berlin[snapshot['properties']['segment_id']] = snapshot	

	# Get a list of all Telraam instances
	time.sleep(2)
	telraam_instances = TELRAAM_API.get_instances()
	if not telraam_instances['ok']:
		LOGGER.err.error(f"sync: {telraam_snapshots['error_message']}")
		return 1

	telraam_instances = telraam_instances['result'].json()['cameras']
	telraam_instances_berlin = [instance for instance in telraam_instances if instance['segment_id'] in telraam_segments_berlin]

	return{
		"telraam_segments_berlin": telraam_segments_berlin,
		"telraam_instances_berlin": telraam_instances_berlin
	}

def import_telraam(instance, sensors, observed_properties, telraam_segments_berlin):
	instance_id = instance['instance_id']  
	segment_id = instance['segment_id']

	LOGGER.log.info(f"\nsync@instance_id({instance_id}) -> found new instance({instance_id}) with segment_id({segment_id}))")

	thing = sensorThings_entities.Thing(
		instance_id, 
		name = TELRAAM_ENTITIES["Things"]["name"],
		description = TELRAAM_ENTITIES["Things"]["description"],
		properties = {
			"instance_id": instance_id,
			"segment_id": segment_id,
			"status": instance["status"],
			"deleted": False
			}
		)

	# Select the sensor
	if instance["hardware_version"] == 1:
		sensor = sensors["Telraam_V1"]
	elif instance["hardware_version"] == 2:
		sensor = sensors["Telraam_S2"]
	else:
		sensor = sensors["Unknown"]

	# Import datastreams
	for observed_property in observed_properties:
		datastream = sensorThings_entities.Datastream(observed_properties[observed_property], sensor, thing)
	
	# Import new segment as location
	if segment_id not in get_sensorThings_entities("Locations", "segment_id"):
		location = sensorThings_entities.Location(
			segment_id, 
			name = TELRAAM_ENTITIES["Locations"]["name"],
			description = TELRAAM_ENTITIES["Locations"]["description"],
			encodingType = TELRAAM_ENTITIES["Locations"]["encodingType"],
			location = telraam_segments_berlin[segment_id]['geometry'],  
			Things = [{"@iot.id": thing.iot_id()}],
			properties = {"segment_id": segment_id, "deleted": False}
			)
		
	# Link existing location to new thing
	else:
		location = sensorThings_entities.Location(segment_id)
		location.link_to_things([{"@iot.id": thing.iot_id()}])
		location.update_self()

	return thing

def sync(sensors, observed_properties):
	LOGGER.log.info(f"########## Start Telraam synchronization ##########")
	
	time_start = time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime(time.time() - 60*60*2))
	time_end = time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime())

	things = get_sensorThings_entities("Things", "instance_id")
	locations = get_sensorThings_entities("Locations", "segment_id")

	telraam_data = get_telraam_data()
	telraam_segments_berlin = telraam_data["telraam_segments_berlin"]
	telraam_instances_berlin = telraam_data["telraam_instances_berlin"]

	number_new_instances = len([instance for instance in telraam_instances_berlin if instance['instance_id'] not in things])

	LOGGER.log.info(f"sync   -> found {len(telraam_segments_berlin)} segments, {len(telraam_instances_berlin)} instances")
	LOGGER.log.info(f"sync   -> found {len(locations)} Locations, {len(things)} Things\n")
	
	# Archive entities from sensorThings if not present in the Telraam data anymore
	archive_outdated_entities(things, "instance_id", telraam_instances_berlin)
	archive_outdated_entities(locations, "segment_id", telraam_segments_berlin)

	# Update the sensorThings API
	update_count = 0
	inactive_count = 0
	for instance in telraam_instances_berlin:
		try:
			instance_id = instance['instance_id']
			LOGGER.log.info(f"### Start synchronization for >>{instance['status']}<< instance({instance_id}) ###")

			if not instance_id in things:	
				things[instance_id] = import_telraam(instance, sensors, observed_properties, telraam_segments_berlin)

			if instance["status"] == "active":
				time.sleep(2)
				telraam_traffic_query_result = TELRAAM_API.get_traffic({ 
					"level": "instances",
					"format": "per-hour",
					"id": f"{instance_id}",
					"time_start": time_start,
					"time_end": time_end
				})

			# Update Observations
			for datastream in things[instance_id].datastreams():
				if instance["status"] == "active" and len(telraam_traffic_query_result["result"].json()["report"]) > 0:
					update_count += 1/len(things[instance_id].datastreams())
					telraam_traffic_data = telraam_traffic_query_result["result"].json()["report"][0]
					result = telraam_traffic_data[datastream["unitOfMeasurement"]["name"]]
					date = telraam_traffic_data["date"]
					sensorThings_entities.Observation(result, date, datastream["@iot.id"])
				else:
					if instance["status"] == "active" and len(telraam_traffic_query_result["result"].json()["report"]) == 0:
						LOGGER.err.warning(f"sync@instance_id({instance['instance_id']}): empty query result for active instance \n")
						break
					inactive_count += 1/len(things[instance_id].datastreams())
					sensorThings_entities.Observation(instance["status"], None, datastream["@iot.id"])

			LOGGER.log.info(f"### Finished synchronization for >>{instance['status']}<< instance({instance_id}) ### \n")

		except RuntimeError as err:
			LOGGER.err.error(f"sync@instance_id({instance['instance_id']}): {err}")
			LOGGER.err.error("sync -> exit \n")
			exit()

	LOGGER.log.info(f"sync -> executed {TELRAAM_API.request_counter} requests to the telraam API")
	LOGGER.log.info(f"sync -> imported {number_new_instances} new instances")
	LOGGER.log.info(f"sync -> updated observations for {round(update_count)} instances ({round(inactive_count)} not active)")
	LOGGER.log.info("sync -> done \n")

def init():

	# Get and/or add Sensors
	sensors = {}
	for sensor in TELRAAM_ENTITIES["Sensors"]:
		sensors[sensor] = sensorThings_entities.Sensor(TELRAAM_ENTITIES["Sensors"][sensor])

	# Get and/or add ObservedProperties
	observed_properties = {}
	for observed_property in TELRAAM_ENTITIES["ObservedProperties"].values():
		observed_properties[observed_property["name"]] = sensorThings_entities.ObservedProperty(observed_property)

	while True:
		if time.localtime().tm_min == 50:
			if time.localtime().tm_hour >= berlin_daytime("sunrise") and time.localtime().tm_hour <= berlin_daytime("sunset"):
				sync(sensors, observed_properties)
			else:
				LOGGER.log.info("main@telraam.sync -> waiting for the sun to rise") 
			time.sleep(10*60)
		time.sleep(abs(2999 - time.localtime().tm_min*60))