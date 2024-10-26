import requests
import json

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
  CONFIG = json.load(read_file)

class Datastream:
	def __init__(self, observed_property, sensor, thing):
		self.name = f"{sensor.name}: {observed_property.name}"
		self.description = observed_property.description
		self.observationType = observed_property.definition
		self.unitOfMeasurement = {
	    "name": observed_property.name,
	    "symbol": "",
	    "definition": self.description
	  }
		self.ObservedProperty = {"@iot.id": observed_property.iot_id}
		self.Sensor = {"@iot.id": sensor.iot_id}
		self.Thing = {"@iot.id": thing.iot_id}
		self.iot_id = self.get_iot_id()

	def get_import_json(self):
		import_json = {
		  "name": self.name,
		  "description": self.description,
		  "observationType": self.observationType,
		  "unitOfMeasurement": self.unitOfMeasurement,
		  "Thing": self.Thing,
		  "Sensor": self.Sensor,
		  "ObservedProperty": self.ObservedProperty
		}	

		return json.dumps(import_json)

	def import_self(self):
		import_result = requests.post(f"{CONFIG['sensorThings_base_location']}/Datastreams", data = self.get_import_json())
		if import_result.ok:
			datastream = requests.get(import_result.headers["Location"])
			print(f"Datastream@iot.id({datastream.json()['@iot.id']}) -> imported new Datastream: {datastream.json()}")
			return datastream.json()["@iot.id"]
		else:
			print(f"ERROR -> Datastream({self.name}): {import_result.headers}")
			return None

	def get_iot_id(self):
		datastreams = requests.get(f"{CONFIG['sensorThings_base_location']}/Things({self.Thing['@iot.id']})?$expand=Datastreams($filter=name eq '{self.name}';$select=@iot.id)")
		if len(datastreams.json()["Datastreams"]) == 1:
			return datastreams.json()["value"][0]["@iot.id"]
		else:
			return self.import_self()