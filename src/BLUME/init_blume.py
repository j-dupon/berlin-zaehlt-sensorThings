import requests
import json
import csv
import time
from sensorThings_entities.Sensor import Sensor
from sensorThings_entities.ObservedProperty import ObservedProperty
from sensorThings_entities.Thing_V2 import Thing 
from sensorThings_entities.Datastream import Datastream
from sensorThings_entities.Observation import Observation

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
	CONFIG = json.load(read_file)

def sync(things, stations):
	print(f"\n ########## Start BLUME synchronization ##########\n")
	
	end_time = time.strftime('%H', time.localtime())
	date = time.strftime('%d.%m.%Y', time.localtime())

	update_count = 0

	for station in stations:

		blume_data_query_result = requests.get(f'https://luftdaten.berlin.de/station/{station}.csv?group=pollution&period=1h&timespan=custom&start%5Bdate%5D={date}&start%5Bhour%5D={int(end_time)-1}&end%5Bdate%5D={date}&end%5Bhour%5D={end_time}')
		print(f'https://luftdaten.berlin.de/station/{station}.csv?group=pollution&period=1h&timespan=custom&start%5Bdate%5D={date}&start%5Bhour%5D={int(end_time)-1}&end%5Bdate%5D={date}&end%5Bhour%5D={end_time}')
		print(blume_data_query_result)
		blume_data = list(csv.reader(blume_data_query_result.text.splitlines(), delimiter=';'))
		print(blume_data)

		blume_measurements = {}
		for index, blume_measurement in enumerate(blume_data[1]):
			blume_measurements[blume_measurement] = blume_data[5][index]

		for datastream in things[station].datastreams():
			update_count += 1/len(things[station].datastreams())
			time_now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.strptime(blume_data[5][0], '%d.%m.%Y %H:%M'))
			result = blume_measurements[datastream["unitOfMeasurement"]["name"]]
			observation = Observation(result, time_now, datastream["@iot.id"])			

	print(f"sync -> updated observations for {round(update_count)} BLUME stations")

def init():
	with open("config/blume_entities.json", mode="r", encoding="utf-8") as read_file:
		blume_entities = json.load(read_file)
		stations = blume_entities["stations"]
		lqi = blume_entities["ObservedProperties"]["Luftqualitätsindex"]
		messcontainer = blume_entities["Sensors"]

# Init Things and Locations (Messcontainer)
	things = {}

	for station in stations:
		station_name = stations[station]['name']
		get_thing_query_result = requests.get(f"{CONFIG['sensorThings_base_location']}/Things?$filter=name eq '{station_name}'")
		if get_thing_query_result.json()["value"] == []:
			import_thing_query_result = requests.post(
				f"{CONFIG['sensorThings_base_location']}/Things",
				json.dumps(stations[station])
				)
		things[station] = Thing(stations[station]["properties"]["unique_allocator"])

# Init Sensors
	sensor = Sensor(messcontainer)

# Init ObservedProperties and Datastreams
	ObservedProperty(lqi)

	start_time = time.strftime('%H', time.localtime())
	date = time.strftime('%d.%m.%Y', time.localtime())

	update_count = 0

	for station in stations:

		blume_data_query_result = requests.get(f"https://luftdaten.berlin.de/station/{station}.csv?group=pollution&period=1h&timespan=custom&start%5Bdate%5D={date}&start%5Bhour%5D={start_time}&end%5Bdate%5D={date}&end%5Bhour%5D={int(start_time)+1}")
		blume_data = list(csv.reader(blume_data_query_result.text.splitlines(), delimiter=';'))

		properties = blume_data[1]
		properties.pop(0)
		for index, blume_property in enumerate(properties):
			symbol = blume_data[2][index+1]
			observed_property = blume_entities["ObservedProperties"]["default"]
			observed_property["name"] = blume_property
			observed_property["description"] = f"{blume_property} in {symbol}"
			observed_property["properties"]["symbol"] = symbol
			observed_property = ObservedProperty(observed_property)
			datastream = Datastream(observed_property, sensor, things[station])

	return {"things": things, "stations": stations}