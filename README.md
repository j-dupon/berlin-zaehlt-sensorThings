# Berlin zählt Mobilität: Überführung der Telraam-Daten in SensorThings API

**`! Aktuell kann die Synchronisierung aufgrund eines Fehlers mit einem der Endpunkte der Telraam-API nicht korrekt ausgeführt werden !`**

Dieses Projekt hat zum Ziel, die in Berlin erhobenen Telraam-Daten in eine SensorThings API zu überführen. SensorThings ist ein Standard des Open Geospacial Consortium (OGC).

- Berlin zählt Mobilität: https://berlin.adfc.de/artikel/berlin-zaehlt-mobilitaet-adfc-berlin-dlr-rufen-zu-citizen-science-projekt-auf-1
- OGC SenosorThings API: https://www.ogc.org/publications/standard/sensorthings/
- Telraam: https://telraam.net

## Quick Start Guide

- Teck-Stack: Python, SensorThings API (FROST-Server)
	- FROST-Server: https://fraunhoferiosb.github.io/FROST-Server/deployment/docker.html
	- Python: Es wird die Bibliothek 'requests' benötigt

Hinweis: Dieser Quick Start Guide wurde auf Debian GNU/Linux 11 (bullseye) getestet

Zum Ausführen des Service muss eine laufende Instanz von SensorThings API vorhanden sein (siehe FROST-Server). Die entprechende docker-compose Datei für den FROST-Server liegt auch in diesem Repository unter `src/config` und kann wie folgt verwendet werden: 

```bash
sudo docker compose up
```

1. Die URL der SensorThingsAPI (FROST-Server-Konfiguration) muss in `src/config/config.json` im Feld `sensorThings_base_location` gesetzt werden.
2. Die Telraam-API benötigt drei X-API-Keys zur Autorisierung (https://faq.telraam.net/article/27/you-wish-more-data-and-statistics-using-the-telraam-api). Diese ebenfalls in der Konfigurationsdatei in den Feldern `telraam_key_header.X-Api-Key` hinterlegen.
3. Zum Starten des Service wird `python3 main.py` im Ordner `src` ausgeführt. Alternativ kann die Synchronisation mit `python3 -m Telraam.trigger_telraam_sync` im Ordner `src` einmalig ausgeführt werden.
4. Jeweils 20 Minuten vor einer vollen Stunde synchronisiert der Service die Telraam-Daten.

`Logs` werden unter `src/logs` erstellt.
#

```json
# config.json

{
	"sensorThings_base_location": "http://localhost:8080/FROST-Server/v1.1",
	"telraam_base_location": "https://telraam-api.net/v1",
	"telraam_api_keys": [
		"X-API-Key 1",
		"X-API-Key 2",
		"X-API-Key 3"
		],
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