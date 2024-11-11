import json
import requests
from .Entity import Entity

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
  CONFIG = json.load(read_file)

class Thing(Entity):
  def __init__(self, unique_allocator, **kwargs):
    super().__init__(unique_allocator)

    if kwargs.keys():
      self.name = kwargs["name"]
      self.description = kwargs["description"]
      self.properties = kwargs["properties"]
      self.properties["unique_allocator"] = unique_allocator
      self.iot_id = self.iot_id()
    else:
      self.iot_id = self.iot_id()
      thing = requests.get(f"{CONFIG['sensorThings_base_location']}/Things({self.iot_id})")
      self.name = thing.json()["name"]
      self.description = thing.json()["description"]
      self.properties = thing.json()["properties"]
      self.datastreams()

  def import_json(self):
    import_json = {
      "name": self.name,
      "description": self.description,
      "properties": self.properties
    }
    return json.dumps(import_json)

  def datastreams(self):
    datastreams_query_result = requests.get(
      f"{CONFIG['sensorThings_base_location']}/{self.__class__.__name__}s({self.iot_id})/Datastreams?$select=@iot.id,unitOfMeasurement/name"
      )
    self.datastreams = datastreams_query_result.json()["value"]
    return self.datastreams