# Berlin zählt Mobilität: Überführung der Telraam-Daten in SensorThings API

Dieses Projekt hat zum Ziel, die in Berlin erhobenen Telraam-Daten an eine SensorThings API zu überführen. SensorThings ist ein Standard des Open Geospacial Consortium (OGC) und ermöglicht die problemlose Anbindung anderer SensorThings Datenquellen. Durch die Erweiterung der Telraam-Daten mit anderen Quellen sollen in diesem Projekt mithilfe der Senosrthings API neue Erkenntnisse gewonnen werden. 

- Berlin zählt Mobilität: https://berlin.adfc.de/artikel/berlin-zaehlt-mobilitaet-adfc-berlin-dlr-rufen-zu-citizen-science-projekt-auf-1
- OGC SenosorThings API: https://www.ogc.org/publications/standard/sensorthings/
- Telraam: https://telraam.net
- Berliner Luftgütemessnetz (BLUME): https://luftdaten.berlin.de/lqi

## Quick Start Guide

- Teck-Stack: Docker, Python

Hinweis: Dieser Quick Start Guide wurde auf Debian getestet

Zum Ausführen des Service muss eine laufende SensorThings API vorhanden sein (siehe **FROST-Server** https://fraunhoferiosb.github.io/FROST-Server/deployment/docker.html). Die entprechende docker-compose Datei für den FROST-Server liegt auch in diesem Repository unter `src/config` und kann wie folgt verwendet werden: 

```bash
sudo docker compose up
```

1. Die URL der SensorThingsAPI (FROST-Server) muss in `src/config/config.json` im Feld `sensorThings_base_location` gesetzt werden (Default von FROST: `http://localhost:8080/FROST-Server/v1.1`)
2. Die Telraam API benötigt einen X-API-Key zur Autorisierung. Diesen ebenfalls in der Konfigurationsdatei im Feld `telraam_key_header.X-Api-Key` hinterlegen. Es kann zusätzlich ein fallback-key angegeben werden, für den Fall, dass die maximale Anzahl an Abfragen an die Telraam-API für den X-Api-Key erreicht wird.
3. Dann kann zum Starten des Service `python3 main.py` im Ordner `src` ausgeführt werden. Alternativ kann die Synchronisation mit `python3 -m Telraam.trigger_telraam_sync` im Ordner `src` einmalig ausgeführt werden.
4. Jeweils 10 Minuten vor einer vollen Stunde synchronisiert der Service die Telraam Daten.

- `Logs` werden unter `src/logs` erstellt.
- Alternativ können auch die BLUME-Daten synchronisiert werden. Hierzu muss in `src/config/config.json` nur das sync_module entprechend gesetzt werden:

```json
{ ...
	"sync_module": "BLUME.sync_blume",
	"sync_module.disabled": "Telraam.sync_telraam"
}
```