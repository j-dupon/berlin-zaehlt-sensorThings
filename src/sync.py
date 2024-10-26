import requests
import json
import time
from TelraamAPI import TelraamAPI
from sensorThings_entities.Location import Location 
from sensorThings_entities.Thing import Thing 
from sensorThings_entities.Datastream import Datastream 
from sensorThings_entities.Observation import Observation 

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
	CONFIG = json.load(read_file)

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
				print(f"sync -> deleted {entity}({iot_id})")
			else:
				print(f"ERROR -> sync: {result_delete_entity.json()}")
		else:
			print(f"ERROR -> sync: found {result_iot_id_query.json()['value']} for {entity_id} of {entity}")



def sync(sensors, observed_properties):

	"""
	Get ID-lists for Things and Locations from the sensorThings API
	"""

	sensorThings_segmentIDs = get_sensorThings_entitiy_IDs("Locations", "segment_id") 
	sensorThings_instanceIDs = get_sensorThings_entitiy_IDs("Things", "instance_id") 

	"""
	Get Telraam data
	"""

	telraam_api = TelraamAPI(CONFIG["telraam_key_header"], CONFIG["telraam_base_location"])

	# Get a list of Telraam segments in Berlin
	telraam_snapshots = telraam_api.get_traffic_snapshot(CONFIG["telraam_traffic_snapshot"])
	if not telraam_snapshots['ok']:
		print(f"ERROR -> sync: {telraam_snapshots['error_message']}")
		print("sync -> stop")
		return 1

	telraam_segments_berlin = {}
	for snapshot in telraam_snapshots['result'].json()['features']:
		telraam_segments_berlin[snapshot['properties']['segment_id']] = snapshot	

	telraam_segmentIDs_berlin = telraam_segments_berlin.keys()

	# Get a list of all Telraam instances
	time.sleep(2)
	telraam_instances = telraam_api.get_instances()
	if not telraam_instances['ok']:
		print(f"ERROR -> sync: {telraam_instances['error_message']}")
		print("sync -> stop")
		return 1

	telraam_instances = telraam_instances['result'].json()['cameras']
	telraam_instances_berlin = [instance for instance in telraam_instances if instance['segment_id'] in telraam_segmentIDs_berlin]
	telraam_instanceIDs = [instance['instance_id'] for instance in telraam_instances_berlin]

	print(f"sync -> start synchronization now")
	print(f"sync   -> found {len(telraam_segments_berlin)} segments, {len(telraam_instances_berlin)} instances")
	print(f"sync   -> found {len(sensorThings_segmentIDs)} Locations, {len(sensorThings_instanceIDs)} Things")
	
	"""
	Delete entities from sensorThings if not present in the Telraam data anymore
	"""

	delete_outdated_entities("Locations", telraam_segmentIDs_berlin, sensorThings_segmentIDs)
	delete_outdated_entities("Things", telraam_instanceIDs, sensorThings_instanceIDs)

	"""
	Import new Telraam data as sensorThings entities
	"""

	new_instances = [instance for instance in telraam_instances_berlin if instance['instance_id'] not in sensorThings_instanceIDs]

	time_start = time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime(time.time() - 60*60*2))
	time_end = time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime())
	time_now = time.strftime('%Y-%m-%d %H:%M:%SZ', time.localtime())

	# Filter instances for Berlin segments
	for instance in telraam_instances_berlin:
		try:
			instance_id = instance['instance_id']
			segment_id = instance['segment_id']

			print(f"\n### Start synchronization for >>{instance['status']}<< instance({instance_id}) ###")

			# Import new instance
			if not instance_id in sensorThings_instanceIDs:	
				print(f"\nsync@instance_id({instance_id}) -> found new instance({instance_id}) with segment_id({segment_id}))")
				thing = Thing(instance_id, segment_id = segment_id) #, user_id = instance["user_id"])

				# Select the sensor
				if instance["hardware_version"] == 1:
					sensor = sensors["Telraam_V1"]
				elif instance["hardware_version"] == 2:
					sensor = sensors["Telraam_S2"]
				else:
					sensor = sensors["Unknown"]

				# Import datastreams
				datastreams = {}
				for observed_property in observed_properties:
					datastream = Datastream(observed_properties[observed_property], sensor, thing)
					datastreams[observed_property] = datastream.iot_id
				
				# Import new segment as location
				if segment_id not in sensorThings_segmentIDs:
					location = Location(segment_id, location = telraam_segments_berlin[segment_id]['geometry'], things = [{"@iot.id": thing.iot_id}])
					sensorThings_segmentIDs.append(segment_id)
					
				# Link existing location to new thing
				else:
					location = Location(segment_id)
					location.link_to_things([{"@iot.id": thing.iot_id}])
					location.update_self()

			# Get datastreams for instance
			else:
				thing = Thing(instance_id)
				datastreams = {}
				for observed_property in observed_properties:
					datastream = requests.get(f"{CONFIG['sensorThings_base_location']}/Things({thing.iot_id})/Datastreams?$select=@iot.id&$filter=unitOfMeasurement/name eq '{observed_property}'")
					datastreams[observed_property] = datastream.json()["value"][0]["@iot.id"]

			"""
			Get Observations
			"""

			if instance["status"] == "active":
				time.sleep(2)
				telraam_traffic_query_result = telraam_api.get_traffic({ 
					"level": "instances",
					"format": "per-hour",
					"id": f"{instance_id}",
					"time_start": time_start,
					"time_end": time_end
				})

			for datastream in datastreams:
				if instance["status"] == "active" and len(telraam_traffic_query_result["result"].json()["report"]) > 0:
					telraam_traffic_data_by_instance_id = telraam_traffic_query_result["result"].json()["report"][0]
					result = telraam_traffic_data_by_instance_id[datastream]
					date = telraam_traffic_data_by_instance_id["date"]
					observation = Observation(result, date, datastreams[datastream])
				else:
					observation = Observation(instance["status"], None, datastreams[datastream])

		except RuntimeError as err:
			print(f"ERROR -> sync@segment_id({segment_id}): {err}")
			print("sync -> exit")
			exit()

	print(f"sync -> imported {len(new_instances)} new instances")
	print("sync -> done")