import json
import requests

class Thing:
  def __init__(self, user_id, instance_id, segment_id):
    self.name = "Telraam instance"
    self.description = "Telraam device for counting traffic on a street segment"
    self.user_id = user_id
    self.segment_id = segment_id
    self.instance_id = instance_id

  def get_import_json(self):
    import_json = {
      "name": self.name,
      "description": self.description,
      "properties": {
        "user_id": self.user_id,
        "segment_id": self.segment_id,
        "instance_id": self.instance_id  # unique
      }
    }
    return json.dumps(import_json)

  def import_self(self, sensorThings_base_url):
    exists_iot_id = self.get_iot_id(sensorThings_base_url)
    if exists_iot_id["ok"]:
      print(f"ERROR -> Thing@instance_id({self.instance_id}): Thing with instance_id already exists!")
      return None

    import_result = requests.post(f"{sensorThings_base_url}/Things", data = self.get_import_json())

    if import_result.ok:
      thing = requests.get(import_result.headers["Location"])
      print(f"Thing@iot.id({thing.json()['@iot.id']}) -> success - imported new Thing: instance_id({self.instance_id}), user_id({self.user_id}), segment_id({self.segment_id}), Thing: {thing.json()}")
      return thing.json()["@iot.id"]
    else:
      print(f"ERROR -> Thing@instance_id({self.instance_id}): {import_result.headers}")
      return None
    
  def get_iot_id(self, sensorThings_base_url):
    thing_query_url = f"{sensorThings_base_url}/Things?$filter=properties/instance_id eq {self.instance_id}"
    things = requests.get(thing_query_url)
    if len(things.json()["value"]) == 1:
      return {"ok": 1, "result": things.json()["value"][0]["@iot.id"]}
    else:
      return {"ok": 0 , "result": things.json()}
    