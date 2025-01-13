from .Entity import *

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
  CONFIG = json.load(read_file)

class Thing(Entity):
  def __init__(self, unique_allocator, **kwargs):
    super().__init__(unique_allocator)
    self.iot_id_request_url = f"Things?$filter=properties/unique_allocator eq '{unique_allocator}'&$select=@iot.id"

    if not kwargs.keys():
      thing = requests.get(f"{CONFIG['sensorThings_base_location']}/Things({self.iot_id()})")
      kwargs = thing.json()

    self.name = kwargs["name"]
    self.description = kwargs["description"]
    self.properties = kwargs["properties"]

    if kwargs.keys():
      self.properties["unique_allocator"] = unique_allocator
      self.iot_id()

  def import_json(self):
    import_json = {
      "name": self.name,
      "description": self.description,
      "properties": self.properties
    }
    return json.dumps(import_json)

  def datastreams(self):
    datastreams_query_result = requests.get(
      f"{CONFIG['sensorThings_base_location']}/Things({self.iot_id()})/Datastreams?$select=@iot.id,unitOfMeasurement/name"
      )
    return datastreams_query_result.json()["value"]