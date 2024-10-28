import json
import requests
from . import Location

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
  CONFIG = json.load(read_file)

class Thing:
  def __init__(self, instance_id, **kwargs):
    self.name = "Telraam instance"
    self.description = "Telraam device for counting traffic on a street segment"
    self.instance_id = instance_id

    if kwargs.keys():
      self.segment_id = kwargs["segment_id"]
      self.status = kwargs["status"]
      self.iot_id = self.get_iot_id()
    else:
      self.iot_id = self.get_iot_id()
      thing = requests.get(f"{CONFIG['sensorThings_base_location']}/Things({self.iot_id})")
      self.segment_id = thing.json()["properties"]["segment_id"]
      self.status = thing.json()["properties"]["status"]
      self.set_datastreams()

  def set_datastreams(self):
    datastreams_query_result = requests.get(f"{CONFIG['sensorThings_base_location']}/Things({self.iot_id})/Datastreams?$select=@iot.id,unitOfMeasurement/name")
    self.datastreams = datastreams_query_result.json()["value"]
    return self.set_datastreams

  def get_import_json(self):
    import_json = {
      "name": self.name,
      "description": self.description,
      "properties": {
        "segment_id": self.segment_id,
        "instance_id": self.instance_id,
        "status": self.status
      }
    }
    return json.dumps(import_json)

  def import_self(self):
    import_result = requests.post(f"{CONFIG['sensorThings_base_location']}/Things", data = self.get_import_json())
    if import_result.ok:
      thing = requests.get(import_result.headers["Location"])
      print(f"Thing@iot.id({thing.json()['@iot.id']}) -> imported new Thing: {thing.json()}")
      return thing.json()["@iot.id"]
    else:
      print(f"ERROR -> Things({self.instance_id}): {import_result.headers}")
      return None

  def get_iot_id(self):
    things = requests.get(f"{CONFIG['sensorThings_base_location']}/Things?$filter=properties/instance_id eq '{self.instance_id}'&$select=@iot.id")
    if len(things.json()["value"]) == 1:
      return things.json()["value"][0]["@iot.id"]
    else:
      return self.import_self()
    