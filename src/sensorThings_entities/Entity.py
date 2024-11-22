import json
import requests
import logging

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
  CONFIG = json.load(read_file)

class Entity():
  def __init__(self, unique_allocator):
    self.unique_allocator = unique_allocator

  def import_self(self):
    entity_name = self.__class__.__name__
    import_result = requests.post(f"{CONFIG['sensorThings_base_location']}/{entity_name.replace('y', 'ie')}s", data = self.import_json())
    if import_result.ok:
      entity = requests.get(import_result.headers["Location"])
      print(f"{entity_name}@iot.id({entity.json()['@iot.id']}) -> imported new {entity_name}: {entity.json()}")
      return entity.json()["@iot.id"]
    else:
      logging.error(f"ERROR -> {entity_name.replace('y', 'ie')}s({self.unique_allocator}) - headers: {import_result.headers} message: {import_result.json()['message']}")
      return None

  def iot_id(self):
    entites_from_result = requests.get(f"{CONFIG['sensorThings_base_location']}/{self.iot_id_request_url}")
    if len(entites_from_result.json()["value"]) == 1:
      return entites_from_result.json()["value"][0]["@iot.id"]
    else:
      return self.import_self()