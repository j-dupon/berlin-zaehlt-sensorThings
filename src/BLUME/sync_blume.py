import requests
import json
import time
import sensorThings_entities
import logger

LOGGER = logger.log

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
	CONFIG = json.load(read_file)

def import_Thing(station):
	return sensorThings_entities.Thing(
		station["code"],
		name = station["name"],
		description = station["url"],
		properties = {
			"unique_allocator": station["code"],
			"Messbeginn": station["measuringStart"],
			"active": station["active"]
		}
	)

def import_Location(station):
	return sensorThings_entities.Location(
		station["name"], 
		name = station["address"],
		description = station["information"],
		encodingType = "application/geo+json",
		properties = {},
		location = {
			"type":  "Point",
			"coordinates":  [station["lng"], station["lat"]]
			},
		Things = []
		)

def import_ObservedProperty(data): 
	res = requests.get(f"https://luftdaten.berlin.de/api/cores/{data['core']}")
	core = res.json() if res.ok else {"name": data["core"], "description": f'{data["component"]}-{data["component"]}'}

	return sensorThings_entities.ObservedProperty({ 
		"name": data["core"],
		"description": core["name"],
		"properties": {
			"symbol": "",
			"component": data["component"],
    	"period": data["period"],
		},
		"definition": core["description"],
	})

def import_Sensor():
	return sensorThings_entities.Sensor({
		"name": "Messcontainer",
	  "description": "Messcontainer des Berliner Luftgüte-Messnetzes (BLUME)",
	  "encodingType": "text",
	  "metadata": "https://www.berlin.de/sen/uvk/umwelt/luft/luftqualitaet/berliner-luft/messnetz/"
	})

def import_Datastream(observed_property, thing, sensor):
	return sensorThings_entities.Datastream(
		observed_property, 
		sensor, 
		thing
		)

def sync(things, sensor):
	LOGGER.log.info(f"\n\n########## Start BLUME synchronization ##########\n")

	stations = requests.get(f"https://luftdaten.berlin.de/api/stations")
	res = requests.get(f"https://luftdaten.berlin.de/api/lqis/data")
	lqi_stations = [lqi_station["station"] for lqi_station in res.json()]
	lqi_data = [lqi_station["data"] for lqi_station in res.json()]
	
	update_count = 0

	for station in stations.json():
		LOGGER.log.info(f"### Start synchronization for >>{'active' if station['active'] else 'inactive'}<< station({station['name']}) ###")

		# Import BLUME instance and location if not exists
		if station["code"] not in things:
			things[station["code"]] = import_Thing(station)
			location = import_Location(station)
			location.link_to_things([{"@iot.id": things[station["code"]].iot_id()}])
			location.update_self()

		thing = things[station["code"]]
			
		# Import observation
		if station["active"]:
			update_count += 1
			res = requests.get(f"https://luftdaten.berlin.de/api/stations/{station['code']}/data")
			station_data = res.json()

			# Merge lqi data
			if station["code"] in lqi_stations:
				for data in lqi_data[lqi_stations.index(station["code"])]:
					data["core"] = "lqi_" + data["component"]
					station_data.append(data)

			datastreams = [datastream["unitOfMeasurement"]["name"] for datastream in thing.datastreams()]

			for data in station_data:
				timestamp = time.strptime(data["datetime"], "%Y-%m-%dT%H:%M:%S%z")
				current_time = time.localtime()

				if timestamp.tm_hour != current_time.tm_hour:
					continue

				# Make sure that the datastream and observed property exists
				if data["core"] not in datastreams:
					observed_property = import_ObservedProperty(data)
					datastream = import_Datastream(observed_property, thing, sensor)
					datastream_iot_id = datastream.iot_id()
				else:
					datastream_iot_id = [datastream["@iot.id"] for datastream in thing.datastreams() if datastream["unitOfMeasurement"]["name"] == data["core"]][0]

				# Import observation
				sensorThings_entities.Observation(
					data["value"], 
					data["datetime"], 
					datastream_iot_id
					)
			
		LOGGER.log.info(f"### Finished synchronization for >>{'active' if station['active'] else 'inactive'}<< station({station['name']}) ### \n")

	LOGGER.log.info(f"sync -> updated observations for {update_count} BLUME stations")

def init():
	sensor = import_Sensor()
	things = {}

	res = requests.get(f"{CONFIG['sensorThings_base_location']}/Things?$select=properties/unique_allocator")
	for allocator in res.json()["value"]:
		things[allocator["properties"]["unique_allocator"]] = sensorThings_entities.Thing(allocator["properties"]["unique_allocator"])

	return {"things": things, "sensor": sensor}