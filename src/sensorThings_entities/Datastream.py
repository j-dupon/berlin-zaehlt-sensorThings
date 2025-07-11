from .Entity import *

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
  CONFIG = json.load(read_file)

class Datastream(Entity):
	def __init__(self, observed_property, sensor, thing):
		super().__init__(f"Thing({thing.iot_id()}):{observed_property.name}/{sensor.name}")

		self.name = f"{sensor.name}: {observed_property.name}"
		self.description = observed_property.description
		self.observationType = observed_property.definition
		self.properties = {"unique_allocator": self.unique_allocator}
		self.unitOfMeasurement = {
	    "name": observed_property.name,
	    "symbol": observed_property.properties["symbol"],
	    "definition": self.description
	  	}
		self.ObservedProperty = {"@iot.id": observed_property.iot_id()}
		self.Sensor = {"@iot.id": sensor.iot_id()}
		self.Thing = {"@iot.id": thing.iot_id()}
		
		self.iot_id_request_url = f"Datastreams?$filter=properties/unique_allocator eq '{self.unique_allocator}'&$select=@iot.id"
		self.iot_id()

	def import_json(self):
		import_json = {
		  "name": self.name,
		  "description": self.description,
		  "observationType": self.observationType,
		  "unitOfMeasurement": self.unitOfMeasurement,
		  "Thing": self.Thing,
		  "Sensor": self.Sensor,
		  "ObservedProperty": self.ObservedProperty,
		  "properties": self.properties
		}	

		return json.dumps(import_json)