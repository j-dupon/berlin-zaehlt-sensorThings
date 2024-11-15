import requests
import json
from .Entity import Entity

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
  CONFIG = json.load(read_file)

class ObservedProperty(Entity):
	def __init__(self, observed_property):
		super().__init__(observed_property["name"])
		self.iot_id_request_url = f"ObservedProperties?$filter=name eq '{observed_property['name']}'&$select=@iot.id"

		self.name = observed_property["name"]
		self.description = observed_property["description"]
		self.properties = observed_property["properties"]
		self.definition = observed_property["definition"]
		self.iot_id()

	def import_json(self):
		import_json = {
			"name": self.name,
			"description": self.description,
			"properties": self.properties,
			"definition": self.definition
		}
		return json.dumps(import_json)