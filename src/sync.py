import requests
import json
from sensorThings_entities import Location
from sensorThings_entities import Thing

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
	CONFIG = json.load(read_file)

def number_of_sensorThings_entities(entity):
	top = 100
	if len(requests.get(f"{CONFIG['sensorThings_base_location']}/{entity}?$top={200}").json()['value']) > 100:
		while len(requests.get(f"{CONFIG['sensorThings_base_location']}/{entity}?$top={top}").json()['value']) % 100 == 0:
			top += 100
	return len(requests.get(f"{CONFIG['sensorThings_base_location']}/{entity}?$top={top}").json()['value'])

def get_sensorThings_entitiy_IDs(entity, id_filter):
	query_top =  number_of_sensorThings_entities(entity)
	query_select = f"$select=properties/{id_filter}"
	query_filter = f"$filter=properties/{id_filter} ne ''"

	query_result = requests.get(f"{CONFIG['sensorThings_base_location']}/{entity}?$top={query_top}&{query_select}&{query_filter}")
	return [entities['properties'][id_filter] for entities in query_result.json()['value']]

def sync(telraam_api):
	sensorThings_segmentIDs = get_sensorThings_entitiy_IDs("Locations", "segment_id") 
	sensorThings_instanceIDs = get_sensorThings_entitiy_IDs("Things", "instance_id") 

	# Get a list of Telraam segments in Berlin
	telraam_snapshots = telraam_api.get_traffic_snapshot('13.398872, 52.511014, 30')
	if not telraam_snapshots['ok']:
		print(f"ERROR -> sync: {telraam_snapshots['error_message']}")
		print("sync -> stop")
		return 1

	telraam_segments_berlin = {}
	for snapshot in telraam_snapshots['result'].json()['features']:
		telraam_segments_berlin[snapshot['properties']['segment_id']] = snapshot	

	# Get a list of all Telraam instances
	time.sleep(2)
	telraam_instances = telraam_api.get_instances()
	if not telraam_instances['ok']:
		print(f"ERROR -> sync: {telraam_instances['error_message']}")
		print("sync -> stop")
		return 1

	telraam_instances = telraam_instances['result'].json()['cameras']
	telraam_instances_berlin = [instance for instance in telraam_instances if instance['segment_id'] in telraam_segments_berlin.keys()]
	
	print(f"sync -> start synchronization now - found {len(telraam_segments_berlin)} segments, {len(telraam_instances_berlin)} instances")
	
	new_instances = [new_instance for new_instance in telraam_instances_berlin if new_instance['instance_id'] not in sensorThings_instanceIDs]
	if new_instances == []:
		print("sync -> no new instances - stop")
		return 0

	# Filter instances for Berlin segments
	telraam_berlin_instances = {}
	for instance in telraam_instances_berlin:
		try:
			instance_id = instance['instance_id']
			segment_id = instance['segment_id']

			if not instance_id in sensorThings_instanceIDs:	
				print(f"\nsync@instance_id({instance_id}) -> found new instance({instance_id}) with segment_id({segment_id}))")
				thing = Thing(instance['user_id'], instance_id, segment_id)
				iot_id = thing.import_self(CONFIG['sensorThings_base_location'])
				sensorThings_instanceIDs.append(instance_id)
				location = Location(segment_id, telraam_segments_berlin[segment_id]['geometry'])
				location.link_to_things([{"@iot.id": iot_id}])

				# Import new segment as location
				if segment_id not in sensorThings_segmentIDs:
					location.import_self(CONFIG['sensorThings_base_location'])
					sensorThings_segmentIDs.append(segment_id)

				# Link existing location to new thing
				else:
					iotIDs_filter_url = f"{CONFIG['sensorThings_base_location']}/Things?$filter=properties/segment_id eq {segment_id}&$select=@iot.id"
					iotIDs_query_result = requests.get(iotIDs_filter_url)
					location.link_to_things(iotIDs_query_result.json()['value'])
					location.update_self(CONFIG['sensorThings_base_location'])

		except RuntimeError as err:
			print(f"ERROR -> sync@segment_id({segment_id}): {err}")
			print("sync -> exit")
			exit()

	print("sync -> done")