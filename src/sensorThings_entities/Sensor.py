import requests
import json

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
  CONFIG = json.load(read_file)

class Sensor:
	def __init__(self, sensor):
		self.name = sensor["name"]
		self.description = sensor["description"]
		self.properties = sensor["properties"]
		self.encodingType = sensor["encodingType"]
		self.metadata = sensor["metadata"]
		self.iot_id = self.get_iot_id()

	def get_import_json(self):
		import_json = {
			"name": self.name,
			"description": self.description,
			"properties": self.properties,
			"encodingType": self.encodingType,
			"metadata": self.metadata
		}
		return json.dumps(import_json)

	def import_self(self):
		import_result = requests.post(f"{CONFIG["sensorThings_base_location"]}/Sensors", data = self.get_import_json())
		if import_result.ok:
			sensor = requests.get(import_result.headers["Location"])
			print(f"Sensor@iot.id({sensor.json()['@iot.id']}) -> imported new Sensor: {sensor.json()}")
			return sensor.json()["@iot.id"]
		else:
			print(f"ERROR -> Sensor({self.name}): {import_result.headers}")
			return None

	def get_iot_id(self):
		sensors = requests.get(f"{CONFIG["sensorThings_base_location"]}/Sensors?$filter=name eq '{self.name}'&$select=@iot.id")
		if len(sensors.json()["value"]) == 1:
			return sensors.json()["value"][0]["@iot.id"]
		else:
			return self.import_self()