# Berlin zählt Mobilität: Überführung der Telraam-Daten in SensorThings API

Dieses Projekt hat zum Ziel, die in Berlin erhobenen Telraam-Daten in eine SensorThings API zu überführen. SensorThings ist ein Standard des Open Geospacial Consortium (OGC).

- Berlin zählt Mobilität: https://berlin.adfc.de/artikel/berlin-zaehlt-mobilitaet-adfc-berlin-dlr-rufen-zu-citizen-science-projekt-auf-1
- OGC SenosorThings API: https://www.ogc.org/publications/standard/sensorthings/
- Telraam: https://telraam.net

## Quick Start Guide

- Teck-Stack: Python, SensorThings API (FROST-Server)
	- FROST-Server: https://fraunhoferiosb.github.io/FROST-Server/deployment/docker.html

Hinweis: Dieser Quick Start Guide wurde auf Debian GNU/Linux 11 (bullseye) getestet

Zum Ausführen des Service muss eine laufende Instanz von SensorThings API vorhanden sein (siehe FROST-Server). Die entprechende docker-compose Datei für den FROST-Server liegt auch in diesem Repository unter `src/config` und kann wie folgt verwendet werden: 

```bash
sudo docker compose up
```

1. Die URL der SensorThingsAPI (FROST-Server-Konfiguration) muss in `src/config/config.json` im Feld `sensorThings_base_location` gesetzt werden.
2. Die Telraam-API benötigt einen X-API-Key zur Autorisierung. Diesen ebenfalls in der Konfigurationsdatei im Feld `telraam_key_header.X-Api-Key` hinterlegen. Es kann zusätzlich ein fallback-key angegeben werden, für den Fall, dass die maximale tägliche Anzahl an Abfragen an die Telraam-API für den X-Api-Key erreicht wird. Das ist in der Regel der Fall.
3. Zum Starten des Service wird `python3 main.py` im Ordner `src` ausgeführt. Alternativ kann die Synchronisation mit `python3 -m Telraam.trigger_telraam_sync` im Ordner `src` einmalig ausgeführt werden.
4. Jeweils 20 Minuten vor einer vollen Stunde zwischen Sonnenaufgang und Sonnenuntergang synchronisiert der Service die Telraam-Daten.

- `Logs` werden unter `src/logs` erstellt.
#

```json
# config.json

{
	"sensorThings_base_location": "http://localhost:8080/FROST-Server/v1.1",
	"telraam_base_location": "https://telraam-api.net/v1",
	"telraam_api_key": "<X-API-Key>",
	"telraam_api_key_fallback": "<X-API-Key Fallback>",
	"telraam_traffic_snapshot": {
		"time": "live",
		"contents": "minimal",
		"berlin_area":"13.398872, 52.511014, 23"
	},
	"logging": {
  		"format": "{asctime} - {levelname}: {message}",
  		"style": "{",
  		"datefmt": "%Y-%m-%d %H:%M:%S",
  		"path": "logs/"
	},
	"sync_module": "Telraam.sync_telraam"
}
```