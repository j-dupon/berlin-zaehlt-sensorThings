import requests
import json

class Sensor:
	def __init__(self, sensorThings_base_url, sensor):
		self.name = sensor["name"]
		self.description = sensor["description"]
		self.properties = sensor["properties"]
		self.encodingType = sensor["encodingType"]
		self.metadata = sensor["metadata"]
		self.iot_id = self.get_iot_id(sensorThings_base_url)

	def get_import_json(self):
		import_json = {
			"name": self.name,
			"description": self.description,
			"properties": self.properties,
			"encodingType": self.encodingType,
			"metadata": self.metadata
		}
		return json.dumps(import_json)

	def import_self(self, sensorThings_base_url):
		import_result = requests.post(f"{sensorThings_base_url}/Sensors", data = self.get_import_json())
		if import_result.ok:
			sensor = requests.get(import_result.headers["Location"])
			print(f"Sensor@iot.id({sensor.json()['@iot.id']}) -> imported new Sensor: {sensor.json()}")
			return sensor.json()["@iot.id"]
		else:
			print(f"ERROR -> Sensor({self.name}): {import_result.headers}")
			return None

	def get_iot_id(self, sensorThings_base_url):
		sensors = requests.get(f"{sensorThings_base_url}/Sensors?$filter=name eq '{self.name}'&$select=@iot.id")
		if len(sensors.json()["value"]) == 1:
			return sensors.json()["value"][0]["@iot.id"]
		else:
			return self.import_self(sensorThings_base_url)