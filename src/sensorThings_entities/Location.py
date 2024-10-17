import json
import requests

class Location:
  def __init__(self, segment_id, geometry):
    self.name = "Segment"
    self.description = "Road segment of the Telraam Instance"
    self.segment_id = segment_id
    self.encodingType = "application/geo+json"
    self.location = geometry
    self.Things = []

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

  def import_self(self, sensorThings_base_url):
    exists_iot_id = self.get_iot_id(sensorThings_base_url)
    if exists_iot_id["ok"]:
      print(f"ERROR -> Location@segment_id({self.segment_id}): Location with segment_id already exists!")
      return None

    import_result = requests.post(f"{sensorThings_base_url}/Locations", data = self.get_import_json())
    
    if import_result.ok:
      location = requests.get(import_result.headers["Location"])
      print(f"Location@iot.id({location.json()['@iot.id']}) -> success - imported new Location({self.segment_id}) for Thing(s)({self.Things}), Location: {location.json()}")
      return location.json()["@iot.id"]
    else:
      print(f"ERROR -> Location@segment_id({self.segment_id}): {import_result.headers}")
      return None

  def update_self(self, sensorThings_base_url):
    exists_iot_id = self.get_iot_id(sensorThings_base_url)
    if not exists_iot_id["ok"]:
      print(f"ERROR -> Location@segment_id({self.segment_id}): error finding unique iot_id - {exists_iot_id['result']}")
      return None

    iot_id = exists_iot_id["result"]
    update_result = requests.patch(f"{sensorThings_base_url}/Locations({iot_id})", data = self.get_import_json())

    if update_result.ok:
      location = requests.get(f"{sensorThings_base_url}/Locations({iot_id})")
      print(f"Location@iot.id({iot_id}) -> success - updated Location({self.segment_id}) for Thing(s)({self.Things}), Location: {location.json()}")
      return iot_id
    else:
      print(f"ERROR -> Location@iot.id({iot_id}): {update_result.json()}")
      return None


  def get_iot_id(self, sensorThings_base_url):
    location_query_url = f"{sensorThings_base_url}/Locations?$filter=properties/segment_id eq {self.segment_id}"
    res = requests.get(location_query_url)
    if len(res.json()["value"]) == 1:
      return {"ok": 1, "result": res.json()["value"][0]["@iot.id"]}
    else:
      return {"ok": 0 , "result": res.json()}