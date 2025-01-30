from .Entity import *

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
  CONFIG = json.load(read_file)

class Location(Entity):
  def __init__(self, unique_allocator, **kwargs):
    super().__init__(unique_allocator)
    self.iot_id_request_url = f"Locations?$filter=properties/unique_allocator eq '{unique_allocator}'&$select=@iot.id"

    if not kwargs.keys():
      location = requests.get(
        f"{CONFIG['sensorThings_base_location']}/Locations({self.iot_id()})?$expand=Things($select=@iot.id)"
        )
      kwargs = location.json()

    self.name = kwargs["name"]
    self.description = kwargs["description"]
    self.encodingType = kwargs["encodingType"]
    self.Things = kwargs["Things"]
    self.location = kwargs["location"]   
    self.properties = kwargs["properties"]

    if kwargs.keys():
      self.properties["unique_allocator"] = unique_allocator
      self.iot_id()

  def link_to_things(self, iotIDs):
    self.Things += [iot_id for iot_id in iotIDs]
    return self.Things

  def import_json(self):
    import_json = {
      "name": self.name,
      "description": self.description,
      "properties": self.properties,
      "encodingType": self.encodingType,
      "location": self.location,
      "Things": self.Things
    }
    return json.dumps(import_json)

  def update_self(self):
    iot_id = super().iot_id()
    update_result = requests.patch(f"{CONFIG['sensorThings_base_location']}/Locations({iot_id})", data = self.import_json())

    if update_result.ok:
      location = requests.get(f"{CONFIG['sensorThings_base_location']}/Locations({iot_id})")
      self.logger.debug.debug(f"Location@iot.id({iot_id}) -> success - updated Location({self.unique_allocator}) for Thing(s)({self.Things}), Location: {location.json()}")
      return iot_id
    else:
      self.logger.err.error(f"Location@iot.id({iot_id}): {update_result.json()}")
      return None