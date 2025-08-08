import requests
import json
import importlib
import logger

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
	CONFIG = json.load(read_file)

LOGGER = logger.log
SYNC = importlib.import_module(f"{CONFIG['sync_module']}")

def check_sensorThings_connection():
	try: 
		request_result = requests.get(CONFIG["sensorThings_base_location"])
		if not request_result.ok:
			return 0
		return 1
	except:
		return 0

if __name__ == "__main__":

	if not check_sensorThings_connection():
		LOGGER.err.error("not connected to sensorThingsAPI")
		print("ERROR: not connected to sensorThingsAPI")
		exit()

	LOGGER.log.info("##########################################")
	LOGGER.log.info("Initiate SensorThings API synchronization")
	LOGGER.log.info("##########################################\n")

	SYNC.init()