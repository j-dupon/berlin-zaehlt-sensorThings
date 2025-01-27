import requests
import json
import logger

LOGGER = logger.log

class TelraamAPI:

	def __init__(self, api_key, api_key_fallback, base_url):
		self.api_key = api_key
		self.api_key_fallback = api_key_fallback
		self.api_key_header = {
			"X-Api-Key": self.api_key,
			"Content-Type": "application/json"
			}
		self.base_url = base_url
		self.request_counter = 0

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
	
	def swap_api_key(self):
		self.request_counter = 0
		LOGGER.err.warning(f"swapped the X-Api-Key after {self.request_counter} requests")
		if self.api_key_header["X-Api-Key"] == self.api_key:
			self.api_key_header["X-Api-Key"] = self.api_key_fallback
		else:
			self.api_key_header["X-Api-Key"] = self.api_key


	def telraam_get(self, url):
		try:
			res = requests.get(url, headers = self.api_key_header)
			if res.status_code > 200:
				self.swap_api_key(self)
				return {"ok": 0, "error_message": res.json()}
			self.request_counter += 1
			return {"ok": 1, "result": res}
		except RuntimeError as err:
			self.swap_api_key(self)
			LOGGER.err.error(f"ERROR -> telraam_get: {err}")
			return {"ok": 0, "error_message": err}

	def telraam_post(self, url, body):
		self.request_counter += 1
		try:
			res = requests.post(url, data = json.dumps(body), headers = self.api_key_header)
			if res.status_code > 200:
				self.swap_api_key(self)
				return {"ok": 0, "error_message": res.json()}
			self.request_counter += 1
			return {"ok": 1, "result": res}
		except RuntimeError as err:
			self.swap_api_key(self)
			LOGGER.err.error(f"ERROR -> telraam_post: {err}")
			return {"ok": 0, "error_message": err}