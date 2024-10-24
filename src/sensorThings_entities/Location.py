import json
import requests

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
  CONFIG = json.load(read_file)

class Location:
  def __init__(self, segment_id, **kwargs):
    self.name = "Segment"
    self.description = "Road segment of the Telraam Instance"
    self.segment_id = segment_id
    self.encodingType = "application/geo+json"

    if "things" in kwargs.keys():
      self.Things = kwargs["things"]
      self.location = kwargs["location"]   
      self.iot_id = self.get_iot_id()
    else:
      self.iot_id = self.get_iot_id()
      location = requests.get(f"{CONFIG['sensorThings_base_location']}/Locations({self.iot_id})?$select=location&$expand=Things($select=@iot.id)")
      self.Things = location.json()["Things"]
      self.location = location.json()["location"]


  def link_to_things(self, iotIDs):
    self.Things += [iot_id for iot_id in iotIDs]
    return self.Things

  def get_import_json(self):
    import_json = {
      "name": self.name,
      "description": self.description,
      "properties": {
          "segment_id": self.segment_id
        },
      "encodingType": self.encodingType,
      "location": self.location,
      "Things": self.Things
    }
    return json.dumps(import_json)

  def update_self(self):
    iot_id = self.get_iot_id()
    update_result = requests.patch(f"{CONFIG['sensorThings_base_location']}/Locations({iot_id})", data = self.get_import_json())

    if update_result.ok:
      location = requests.get(f"{CONFIG['sensorThings_base_location']}/Locations({iot_id})")
      print(f"Location@iot.id({iot_id}) -> success - updated Location({self.segment_id}) for Thing(s)({self.Things}), Location: {location.json()}")
      return iot_id
    else:
      print(f"ERROR -> Location@iot.id({iot_id}): {update_result.json()}")
      return None

  def import_self(self):
    import_result = requests.post(f"{CONFIG['sensorThings_base_location']}/Locations", data = self.get_import_json())
    if import_result.ok:
      location = requests.get(import_result.headers["Location"])
      print(f"Location@iot.id({location.json()['@iot.id']}) -> imported new Location: {location.json()}")
      return location.json()["@iot.id"]
    else:
      print(f"ERROR -> Location({self.segment_id}): {import_result.headers}")
      return None

  def get_iot_id(self):
    locations = requests.get(f"{CONFIG['sensorThings_base_location']}/Locations?$filter=properties/segment_id eq '{self.segment_id}'&$select=@iot.id")
    if len(locations.json()["value"]) == 1:
      return locations.json()["value"][0]["@iot.id"]
    else:
      return self.import_self()