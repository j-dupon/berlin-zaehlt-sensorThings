import requests
import json
import time
from sync import sync
from TelraamAPI import TelraamAPI

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
	CONFIG = json.load(read_file)

def check_sensorThings_connection():
	try: 
		res = requests.get(CONFIG["sensorThings_base_location"])
		if not res.ok:
			return 0
		return 1
	except:
		return 0

if __name__ == "__main__":

	if not check_sensorThings_connection():
		print("ERROR -> sync: not connected to sensorThingsAPI")
		exit()

	telraam_api = TelraamAPI(CONFIG["telraam_key_header"], CONFIG["telraam_base_location"])

	while True:
		sync(telraam_api)
		time.sleep(CONFIG["sync_timer_in_seconds"])