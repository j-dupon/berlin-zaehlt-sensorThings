import requests
import json

class ObservedProperty:
	def __init__(self, sensorThings_base_url, observed_property):
		self.name = observed_property["name"]
		self.description = observed_property["description"]
		self.properties = observed_property["properties"]
		self.definition = observed_property["definition"]
		self.iot_id = self.get_iot_id(sensorThings_base_url)

	def get_import_json(self):
		import_json = {
			"name": self.name,
			"description": self.description,
			"properties": self.properties,
			"definition": self.definition
		}
		return json.dumps(import_json)

	def import_self(self, sensorThings_base_url):
		import_result = requests.post(f"{sensorThings_base_url}/ObservedProperties", data = self.get_import_json())
		if import_result.ok:
			observed_property = requests.get(import_result.headers["Location"])
			print(f"ObservedProperty@iot.id({observed_property.json()['@iot.id']}) -> imported new ObservedProperty: {observed_property.json()}")
			return observed_property.json()["@iot.id"]
		else:
			print(f"ERROR -> ObservedProperty({self.name}): {import_result.headers}")
			return None

	def get_iot_id(self, sensorThings_base_url):
		observed_properties = requests.get(f"{sensorThings_base_url}/ObservedProperties?$filter=name eq '{self.name}'&$select=@iot.id")
		if len(observed_properties.json()["value"]) == 1:
			return observed_properties.json()["value"][0]["@iot.id"]
		else:
			return self.import_self(sensorThings_base_url)