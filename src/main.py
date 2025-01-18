import requests
import json
import time
import BLUME.sync_blume as blume
import Telraam.init_telraam as telraam
import logger

LOGGER = logger.log

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
	CONFIG = json.load(read_file)

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
		LOGGER.err.error("main: not connected to sensorThingsAPI")
		exit()

	LOGGER.log.info("##########################################")
	LOGGER.log.info("Initiate SensorThings API synchronization")
	LOGGER.log.info("##########################################\n")

	if CONFIG["sync_telraam"]:
		telraam_initialization = telraam.init()

	if CONFIG["sync_blume"]:
		blume_initialization = blume.init()

	while True:
		if time.localtime().tm_min == 50:
			if CONFIG["sync_telraam"]:
				if time.localtime().tm_hour > 7 and time.localtime().tm_hour < 18:
					telraam.sync(
						telraam_initialization["things"], 
						telraam_initialization["sensors"], 
						telraam_initialization["observed_properties"]
						)
				else:
					LOGGER.log.info("main@telraam.sync -> waiting for the sun to rise") 
			if CONFIG["sync_blume"]:
				blume.sync(
					blume_initialization["things"], 
					blume_initialization["sensor"]
					)
			time.sleep(3000)
		else:
			time.sleep(55)
