import requests
import json

class TelraamAPI:

	def __init__(self, api_key_header, base_url):
		self.api_key_header = api_key_header
		self.base_url = base_url

	def get_traffic_snapshot(self, settings):
		url = f"{self.base_url}/reports/traffic_snapshot"
		body = {
			"time": settings["time"],
			"contents": settings["contents"],
			"area": settings["berlin_area"]
		}	
		return self.telraam_post(url, body)

	def get_instances(self):
		return self.telraam_get(f"{self.base_url}/cameras")

	def get_instance_by_id(self, segment_id):
		url = f"{self.base_url}/cameras/segment/{segment_id}"
		return self.telraam_get(url)

	def get_traffic(self, settings):
		body = {
		  "level": settings["level"],
		  "format": settings["format"],
		  "id": settings["id"],
		  "time_start": settings["time_start"],
		  "time_end": settings["time_end"]
		}	
		return self.telraam_post(f"{self.base_url}/reports/traffic", body)

	def get_segments(self):
		return self.telraam_get(f"{self.base_url}/segments/all")

	def get_segment_by_id(self, segment_id):
		url = f"{self.base_url}/segments/id/{segment_id}"
		return self.telraam_get(url)

	def telraam_get(self, url):
		try:
			res = requests.get(url, headers = self.api_key_header)
			if res.status_code > 200:
				return {"ok": 0, "error_message": res.json()}
			return {"ok": 1, "result": res}
		except RuntimeError as err:
			print(f"ERROR -> telraam_get: {err}")
			return {"ok": 0, "error_message": err}

	def telraam_post(self, url, body):
		try:
			res = requests.post(url, data = json.dumps(body), headers = self.api_key_header)
			if res.status_code > 200:
				return {"ok": 0, "error_message": res.json()}
			return {"ok": 1, "result": res}
		except RuntimeError as err:
			print(f"ERROR -> telraam_post: {err}")
			return {"ok": 0, "error_message": err}