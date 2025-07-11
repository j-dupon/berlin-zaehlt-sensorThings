import json
import requests
import logger

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
  CONFIG = json.load(read_file)

class Entity():
  def __init__(self, unique_allocator):
    self.unique_allocator = unique_allocator
    self.logger = logger.log
    self.entity_name = self.__class__.__name__

  def import_self(self):
    import_result = requests.post(f"{CONFIG['sensorThings_base_location']}/{self.entity_name.replace('y', 'ie')}s", data = self.import_json())
    if import_result.ok:
      entity = requests.get(import_result.headers["Location"])
      self.logger.debug.debug(f"{self.entity_name}@iot.id({entity.json()['@iot.id']}) -> imported new {self.entity_name}: {entity.json()}")
      return entity.json()["@iot.id"]
    else:
      self.logger.err.error(f"{self.entity_name.replace('y', 'ie')}s({self.unique_allocator}) - headers: {import_result.headers} message: {import_result.json()['message']}")
      return None

  def iot_id(self):
    entites_from_result = requests.get(f"{CONFIG['sensorThings_base_location']}/{self.iot_id_request_url}")
    if len(entites_from_result.json()["value"]) == 0:
      return self.import_self()
    if len(entites_from_result.json()["value"]) == 1:
      return entites_from_result.json()["value"][0]["@iot.id"]
    self.logger.err.error(f"{self.entity_name}@unique_allocator({self.unique_allocator}): {entites_from_result.json()}")
    return -1
    
  def update_self(self):
    iot_id = self.iot_id()
    update_result = requests.patch(f"{CONFIG['sensorThings_base_location']}/{self.entity_name.replace('y', 'ie')}s({iot_id})", data = self.import_json())

    if update_result.ok:
      location = requests.get(f"{CONFIG['sensorThings_base_location']}/{self.entity_name.replace('y', 'ie')}s({iot_id})")
      self.logger.debug.debug(f"{self.entity_name}@iot.id({iot_id}) -> success - updated {self.entity_name}({self.unique_allocator}), {self.entity_name}: {location.json()}")
      return iot_id
    else:
      self.logger.err.error(f"{self.entity_name}@iot.id({iot_id}): {update_result.json()}")
      return None
    