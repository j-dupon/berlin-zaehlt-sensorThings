import requests
import json
import logger

LOGGER = logger.log

class TelraamAPI:

	def __init__(self, api_keys, base_url):
		self.api_keys = api_keys
		self.api_key_header = {
			"X-Api-Key": self.api_keys[0],
			"Content-Type": "application/json"
			}
		self.base_url = base_url
		self.request_counter = 0
		self.swap_key_counter = 0
		self.traffic_snapshot_fallback_data = {"ok": 0, "error_message": "no data available"}
		self.instances_fallback_data = {"ok": 0, "error_message": "no data available"}

	def traffic_snapshot(self, settings):
		url = f"{self.base_url}/reports/traffic_snapshot"
		body = {
			"time": settings["time"],
			"contents": settings["contents"],
			"area": settings["berlin_area"]
		}	

		res = self.telraam_post(url, body)
		
		if not res["ok"]:
			LOGGER.log.info(f"TelraamAPI@traffic_snapshot: fallback to snpashot backup - {res["error_message"]}")
			return self.traffic_snapshot_fallback_data

		self.traffic_snapshot_fallback_data = res
		return res

	def instances(self):
		res = self.telraam_get(f"{self.base_url}/cameras")

		if not res["ok"]:
			LOGGER.log.info(f"TelraamAPI@instances: fallback to instances backup - {res["error_message"]}")
			return self.instances_fallback_data

		self.instances_fallback_data = res
		return res

	def traffic(self, settings):
		body = {
		  "level": settings["level"],
		  "format": settings["format"],
		  "id": settings["id"],
		  "time_start": settings["time_start"],
		  "time_end": settings["time_end"]
		}	

		return self.telraam_post(f"{self.base_url}/reports/traffic", body)
		
	def swap_api_key(self, request_method, url, body):
		LOGGER.log.info(f"TelraamAPI@swap_api_key({self.api_keys[self.swap_key_counter%3]}): swapping X-Api-Key after {self.request_counter} requests")
		self.request_counter = 0
		self.swap_key_counter += 1
		self.api_key_header["X-Api-Key"] = self.api_keys[self.swap_key_counter%3]

		# Repeat a failed GET request
		if request_method == "get":
			return requests.get(url, headers = self.api_key_header)

		# Repeat a failed POST request
		if request_method == "post":
			return requests.post(url, data = body, headers = self.api_key_header)

		LOGGER.err.error(f"TelraamAPI@telraam_post: Unknown error - attempting to swap API-Keys failed")
		exit()

	def telraam_get(self, url):
		try:
			res = requests.get(url, headers = self.api_key_header)
			if res.status_code == 429:
				res = self.swap_api_key("get", url, None)
			if res.status_code > 201:
				LOGGER.err.error(f"TelraamAPI@telraam_get: request returned {res.status_code} - {res.json()}")
				return {"ok": 0, "error_message": res.json()}
			if res.json()["status_code"] == 201 and "download_url" in res.json():
				res = self.telraam_get(res.json()["download_url"])["result"]
				LOGGER.debug.debug(f"TelraamAPI@telraam_get: fallback to download url - result: {res.json()}")
				LOGGER.log.info(f"TelraamAPI@telraam_get: fallback to download url - status_code: {res.json()['status_code']}")
			if res.json()["status_code"] > 201 or "errorMessage" in res.json():
				LOGGER.err.error(f"TelraamAPI@telraam_get: request returned {res.json()['status_code']} - {res.json()}")
				return {"ok": 0, "error_message": res.json()}
			self.request_counter += 1
			return {"ok": 1, "result": res}
		
		except RuntimeError as err:
			LOGGER.err.error(f"ERROR -> telraam_get: {err}")
			exit()

	def telraam_post(self, url, body):
		try:
			res = requests.post(url, data = json.dumps(body), headers = self.api_key_header)
			if res.status_code == 429:
				res = self.swap_api_key("post", url, json.dumps(body))
			if res.status_code > 201:
				LOGGER.err.error(f"TelraamAPI@telraam_post: request returned {res.status_code} - {res.json()}")
				return {"ok": 0, "error_message": res.json()}
			if res.json()["status_code"] == 201 and "download_url" in res.json():
				res = self.telraam_get(res.json()["download_url"])["result"]
				LOGGER.debug.debug(f"TelraamAPI@telraam_post: fallback to download url - result: {res.json()}")
				LOGGER.log.info(f"TelraamAPI@telraam_post: fallback to download url - status_code: {res.json()['status_code']}")
			if res.json()["status_code"] > 201 or "errorMessage" in res.json():
				LOGGER.err.error(f"TelraamAPI@telraam_post: request returned {res.json()['status_code']} - {res.json()}")
				return {"ok": 0, "error_message": res.json()}
			self.request_counter += 1
			return {"ok": 1, "result": res}
		
		except RuntimeError as err:
			LOGGER.err.error(f"ERROR -> telraam_post: {err}")
			exit()