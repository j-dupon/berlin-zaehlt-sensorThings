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

with open("config/blume_entities.json", mode="r", encoding="utf-8") as read_file:
	BLUME_ENTITIES = json.load(read_file)

def lqi_classification(metric, result):
	if not metric in BLUME_ENTITIES["lqi_classifications"].keys():
		return 0	

	for index, classification in enumerate(BLUME_ENTITIES["lqi_classifications"][metric]):
		if float(result) < classification:
			return index+1

	return 6

def sync(things):
	print(f"\n ########## Start BLUME synchronization ##########\n")
	
	end_time = time.strftime('%H', time.localtime())
	date = time.strftime('%d.%m.%Y', time.localtime())

	update_count = 0

	for station in BLUME_ENTITIES["stations"]:

		blume_data_query_result = requests.get(f'https://luftdaten.berlin.de/station/{station}.csv?group=pollution&period=1h&timespan=custom&start%5Bdate%5D={date}&start%5Bhour%5D={int(end_time)-1}&end%5Bdate%5D={date}&end%5Bhour%5D={end_time}')
		#print(f'https://luftdaten.berlin.de/station/{station}.csv?group=pollution&period=1h&timespan=custom&start%5Bdate%5D={date}&start%5Bhour%5D={int(end_time)-1}&end%5Bdate%5D={date}&end%5Bhour%5D={end_time}')
		blume_data = list(csv.reader(blume_data_query_result.text.splitlines(), delimiter=';'))
		result_time = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.strptime(blume_data[5][0], '%d.%m.%Y %H:%M'))

		blume_metrics = {}
		for index, blume_metric in enumerate(blume_data[1]):
			blume_metrics[blume_metric] = blume_data[5][index]


		lqi_grade_station = 0
		for datastream in things[station].datastreams():
			update_count += 1/len(things[station].datastreams())
			unit_of_measurement = datastream["unitOfMeasurement"]["name"]


			if unit_of_measurement == "LQI":
				lqi_iot_id = datastream["@iot.id"]
				continue
			
			result = blume_metrics[unit_of_measurement]

			lqi_grade_metric = lqi_classification(unit_of_measurement, result)
			if lqi_grade_metric > lqi_grade_station:
				lqi_grade_station = lqi_grade_metric
			
			#Observation(result, result_time, datastream["@iot.id"])			
			# TODO: observation for lqi of metric

		Observation(lqi_grade_station, result_time, lqi_iot_id)			

	print(f"sync -> updated observations for {round(update_count)} BLUME stations")

def init():
	stations = BLUME_ENTITIES["stations"]
	lqi = BLUME_ENTITIES["ObservedProperties"]["Luftqualitätsindex"]
	messcontainer = BLUME_ENTITIES["Sensors"]

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
	observed_property_lqi = ObservedProperty(lqi)

	start_time = time.strftime('%H', time.localtime())
	date = time.strftime('%d.%m.%Y', time.localtime())

	update_count = 0

	for station in stations:
		Datastream(observed_property_lqi, sensor, things[station])

		#blume_data_query_result = requests.get(f"https://luftdaten.berlin.de/station/{station}.csv?group=pollution&period=1h&timespan=custom&start%5Bdate%5D={date}&start%5Bhour%5D={start_time}&end%5Bdate%5D={date}&end%5Bhour%5D={int(start_time)+1}")
		blume_data_query_result = requests.get(f"https://luftdaten.berlin.de/station/{station}.csv?group=pollution&period=1h&timespan=custom&start%5Bdate%5D={date}&start%5Bhour%5D=15&end%5Bdate%5D={date}&end%5Bhour%5D=15")
		blume_data = list(csv.reader(blume_data_query_result.text.splitlines(), delimiter=';'))

		blume_metrics = blume_data[1]
		blume_metrics.pop(0)
		for index, blume_metric in enumerate(blume_metrics):
			symbol = blume_data[2][index+1]

			try:
				observed_property = BLUME_ENTITIES["ObservedProperties"][blume_metric]
			except:
				observed_property = BLUME_ENTITIES["ObservedProperties"]["default"]
				observed_property["name"] = blume_metric
				observed_property["description"] = f"{blume_metric} in {symbol}"

			observed_property["properties"]["symbol"] = symbol
			observed_property = ObservedProperty(observed_property)
			datastream = Datastream(observed_property, sensor, things[station])

	return things