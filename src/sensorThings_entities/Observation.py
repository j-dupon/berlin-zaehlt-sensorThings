import requests
import json

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
  CONFIG = json.load(read_file)

class Observation:
	def __init__(self, result, phenomenonTime, datastream):
		self.result = result 
		self.phenomenonTime = phenomenonTime 
		self.Datastream = {"@iot.id": datastream} 
		self.iot_id = self.import_self()

	def get_import_json(self):
		import_json = {
		  "result": self.result,
		  "Datastream": self.Datastream
		}	

		if self.phenomenonTime:
			import_json["phenomenonTime"] = self.phenomenonTime

		return json.dumps(import_json)

	def import_self(self):
		import_result = requests.post(f"{CONFIG['sensorThings_base_location']}/Observations", data = self.get_import_json())
		if import_result.ok:
			observation = requests.get(import_result.headers["Location"])
			#print(f"Observation@iot.id({observation.json()['@iot.id']}) -> imported new Observation: {observation.json()}")
			return observation.json()["@iot.id"]
		else:
			print(f"ERROR -> Observation@Datastream({self.Datastream['@iot.id']}): {import_result.headers}")
			return None

	def get_iot_id(self):
		observations = requests.get(f"{CONFIG['sensorThings_base_location']}/Datastreams({self.Datastream['@iot.id']})/Observations?$filter=phenomenonTime eq '{self.phenomenonTime}'&$select=@iot.id")
		if len(observations.json()["value"]) == 1:
			return observations.json()["value"][0]["@iot.id"]
		else:
			return self.import_self()