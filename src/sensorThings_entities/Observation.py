import requests
import json
from .Entity import Entity

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
  CONFIG = json.load(read_file)

class Observation(Entity):
	def __init__(self, result, phenomenonTime, datastream):
		super().__init__(f"Datastream({datastream}):{phenomenonTime}")

		self.result = result 
		self.phenomenonTime = phenomenonTime 
		self.Datastream = {"@iot.id": datastream} 
		self.import_self()

	def import_json(self):
		import_json = {
		  "result": self.result,
		  "Datastream": self.Datastream
		}	

		if self.phenomenonTime:
			import_json["phenomenonTime"] = self.phenomenonTime

		return json.dumps(import_json)

	def iot_id():
		return None