import Telraam.init_telraam as telraam
import logger
import requests
import json

LOGGER = logger.log

with open("config/config.json", mode="r", encoding="utf-8") as read_file:
	CONFIG = json.load(read_file)

with open("config/telraam_entities.json", mode="r", encoding="utf-8") as read_file:
	TELRAAM_ENTITIES = json.load(read_file)

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
		LOGGER.err.error("ERROR -> sync: not connected to sensorThingsAPI")
		exit()

	telraam_initialization = telraam.init()

	telraam.sync(
		telraam_initialization["things"], 
		telraam_initialization["sensors"], 
		telraam_initialization["observed_properties"]
		)