import requests
import json
import time
import sensorThings_entities
from Telraam.TelraamAPI import TelraamAPI
import logger

LOGGER = logger.log

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
	CONFIG = json.load(read_file)

with open("Telraam/telraam_entities.json", mode="r", encoding="utf-8") as read_file:
	TELRAAM_ENTITIES = json.load(read_file)

def get_sensorThings_entitiy_IDs(entity, id_filter):
	count = requests.get(f"{CONFIG['sensorThings_base_location']}/{entity}?$count=true")
	query_top =  count.json()["@iot.count"]
	query_select = f"$select=properties/{id_filter}"
	query_filter = f"$filter=properties/{id_filter} ne ''"

	query_result = requests.get(f"{CONFIG['sensorThings_base_location']}/{entity}?$top={query_top}&{query_select}&{query_filter}")
	return [entities['properties'][id_filter] for entities in query_result.json()['value']]

def delete_outdated_entities(entity, telraamIDs, sensorThingsIDs):
	outdated_entityIDs = [entity_id for entity_id in sensorThingsIDs if entity_id not in telraamIDs]
	
	for entity_id in outdated_entityIDs:
		if entity == "Things":
			result_iot_id_query = requests.get(f"{CONFIG['sensorThings_base_location']}/Things?$filter=properties/instance_id eq {entity_id}&$select=@iot.id")
		if entity == "Locations":
			result_iot_id_query = requests.get(f"{CONFIG['sensorThings_base_location']}/Locations?$filter=properties/segment_id eq {entity_id}&$select=@iot.id")
		
		if len(result_iot_id_query.json()["value"]) == 1:
			iot_id = result_iot_id_query.json()["value"][0]["@iot.id"]
			result_delete_entity = requests.delete(f"{CONFIG['sensorThings_base_location']}/{entity}({iot_id})")
			if result_delete_entity.ok:
				LOGGER.log.info(f"sync -> deleted {entity}({iot_id})")
			else:
				LOGGER.err.error(f"sync: {result_delete_entity.json()}")
		else:
			LOGGER.err.error(f"sync: found {result_iot_id_query.json()['value']} for {entity_id} of {entity}")

def get_telraam_data(telraam_api):
	
	# Get a list of Telraam segments in Berlin
	telraam_snapshots = telraam_api.get_traffic_snapshot(CONFIG["telraam_traffic_snapshot"])
	if not telraam_snapshots['ok']:
		LOGGER.err.error(f"sync: {telraam_snapshots['error_message']}")
		return 1

	telraam_segments_berlin = {}
	for snapshot in telraam_snapshots['result'].json()['features']:
		telraam_segments_berlin[snapshot['properties']['segment_id']] = snapshot	

	telraam_segmentIDs_berlin = telraam_segments_berlin.keys()

	# Get a list of all Telraam instances
	time.sleep(2)
	telraam_instances = telraam_api.get_instances()
	if not telraam_instances['ok']:
		LOGGER.err.error(f"sync: {telraam_snapshots['error_message']}")
		return 1

	telraam_instances = telraam_instances['result'].json()['cameras']
	telraam_instances_berlin = [instance for instance in telraam_instances if instance['segment_id'] in telraam_segmentIDs_berlin]
	telraam_instanceIDs_berlin = [instance['instance_id'] for instance in telraam_instances_berlin]

	return{
		"telraam_segmentIDs_berlin": telraam_segmentIDs_berlin, 
		"telraam_segments_berlin": telraam_segments_berlin,
		"telraam_instanceIDs_berlin": telraam_instanceIDs_berlin, 
		"telraam_instances_berlin": telraam_instances_berlin
	}

def import_new_telraam_instance(instance, things, sensors, observed_properties, sensorThings_segmentIDs, telraam_segments_berlin):
	instance_id = instance['instance_id']  
	segment_id = instance['segment_id']

	LOGGER.log.info(f"\nsync@instance_id({instance_id}) -> found new instance({instance_id}) with segment_id({segment_id}))")

	things[instance_id] = sensorThings_entities.Thing(
		instance_id, 
		name = TELRAAM_ENTITIES["Things"]["name"],
		description = TELRAAM_ENTITIES["Things"]["description"],
		properties = {
			"instance_id": instance_id,
			"segment_id": segment_id,
			"status": instance["status"]
			}
		)

	thing = things[instance_id]

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

	thing.datastreams()
	
	# Import new segment as location
	if segment_id not in sensorThings_segmentIDs:
		location = sensorThings_entities.Location(
			segment_id, 
			name = TELRAAM_ENTITIES["Locations"]["name"],
			description = TELRAAM_ENTITIES["Locations"]["description"],
			encodingType = TELRAAM_ENTITIES["Locations"]["encodingType"],
			location = telraam_segments_berlin[segment_id]['geometry'],  
			Things = [{"@iot.id": thing.iot_id()}],
			properties = {"segment_id": segment_id}
			)
		sensorThings_segmentIDs.append(segment_id)
		
	# Link existing location to new thing
	else:
		location = sensorThings_entities.Location(segment_id)
		location.link_to_things([{"@iot.id": thing.iot_id()}])
		location.update_self()

	return things

def sync(things, sensors, observed_properties):
	LOGGER.log.info(f"########## Start Telraam synchronization ##########")
	
	time_start = time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime(time.time() - 60*60*2))
	time_end = time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime())
	time_now = time.strftime('%Y-%m-%d %H:%M:%SZ', time.localtime())

	sensorThings_segmentIDs = get_sensorThings_entitiy_IDs("Locations", "segment_id") 
	sensorThings_instanceIDs = get_sensorThings_entitiy_IDs("Things", "instance_id") 

	telraam_api = TelraamAPI(CONFIG["telraam_key_header"], CONFIG["telraam_base_location"])
	telraam_data = get_telraam_data(telraam_api)

	telraam_segmentIDs_berlin = telraam_data["telraam_segmentIDs_berlin"]
	telraam_segments_berlin = telraam_data["telraam_segments_berlin"]
	telraam_instanceIDs_berlin = telraam_data["telraam_instanceIDs_berlin"]
	telraam_instances_berlin = telraam_data["telraam_instances_berlin"]

	number_new_instances = len([instance for instance in telraam_instances_berlin if instance['instance_id'] not in sensorThings_instanceIDs])

	LOGGER.log.info(f"sync   -> found {len(telraam_segments_berlin)} segments, {len(telraam_instances_berlin)} instances")
	LOGGER.log.info(f"sync   -> found {len(sensorThings_segmentIDs)} Locations, {len(sensorThings_instanceIDs)} Things\n")
	
	# Delete entities from sensorThings if not present in the Telraam data anymore
	delete_outdated_entities("Locations", telraam_segmentIDs_berlin, sensorThings_segmentIDs)
	delete_outdated_entities("Things", telraam_instanceIDs_berlin, sensorThings_instanceIDs)

	# Update the sensorThings API
	update_count = 0
	inactive_count = 0
	for instance in telraam_instances_berlin:
		try:
			#instance['instance_id'] += 90000
			instance_id = instance['instance_id']

			LOGGER.log.info(f"### Start synchronization for >>{instance['status']}<< instance({instance_id}) ###")

			if not instance_id in sensorThings_instanceIDs:	
				things = import_new_telraam_instance(instance, things, sensors, observed_properties, sensorThings_segmentIDs, telraam_segments_berlin)

			if instance["status"] == "active":
				time.sleep(2)
				telraam_traffic_query_result = telraam_api.get_traffic({ 
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
					observation = sensorThings_entities.Observation(result, date, datastream["@iot.id"])
				else:
					if instance["status"] == "active" and len(telraam_traffic_query_result["result"].json()["report"]) == 0:
						LOGGER.err.warning(f"sync@instance_id({instance['instance_id']}): empty query result for active instance \n")
						break
					inactive_count += 1/len(things[instance_id].datastreams())
					observation = sensorThings_entities.Observation(instance["status"], None, datastream["@iot.id"])

			LOGGER.log.info(f"### Finished synchronization for >>{instance['status']}<< instance({instance_id}) ### \n")

		except RuntimeError as err:
			LOGGER.err.error(f"sync@instance_id({instance['instance_id']}): {err}")
			LOGGER.err.error("sync -> exit \n")
			exit()

	LOGGER.log.info(f"sync -> imported {number_new_instances} new instances")
	LOGGER.log.info(f"sync -> updated observations for {round(update_count)} instances ({round(inactive_count)} not active)")
	LOGGER.log.info("sync -> done \n")

def init():

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

	while True:
		if time.localtime().tm_min == 50:
			if time.localtime().tm_hour > 7 and time.localtime().tm_hour < 18:
				sync(things, sensors, observed_properties)
			else:
				LOGGER.log.info("main@telraam.sync -> waiting for the sun to rise") 
			time.sleep(10*60)
		time.sleep(abs(2999 - time.localtime().tm_min*60))