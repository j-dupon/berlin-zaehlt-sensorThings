import requests
import json
from .Entity import Entity

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
  CONFIG = json.load(read_file)

class Sensor(Entity):
	def __init__(self, sensor):
		super().__init__(sensor["name"])
		self.iot_id_request_url = f"Sensors?$filter=name eq '{sensor['name']}'&$select=@iot.id"

		self.name = sensor["name"]
		self.description = sensor["description"]
		self.encodingType = sensor["encodingType"]
		self.metadata = sensor["metadata"]
		self.iot_id()

	def import_json(self):
		import_json = {
			"name": self.name,
			"description": self.description,
			"encodingType": self.encodingType,
			"metadata": self.metadata
		}
		return json.dumps(import_json)