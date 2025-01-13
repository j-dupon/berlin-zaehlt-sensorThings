# Berlin zählt Mobilität: Überführung der Telraam-Daten in SensorThings API

Dieses Projekt hat zum Ziel, die in Berlin erhobenen Telraam-Daten an eine SensorThings API zu überführen. SensorThings ist ein Standard des Open Geospacial Consortium (OGC) und ermöglicht die problemlose Anbindung anderer SensorThings Datenquellen. Durch die Erweiterung der Telraam-Daten mit anderen Quellen sollen in diesem Projekt mithilfe der Senosrthings API neue Erkenntnisse gewonnen werden. 

- Berlin zählt Mobilität: https://berlin.adfc.de/artikel/berlin-zaehlt-mobilitaet-adfc-berlin-dlr-rufen-zu-citizen-science-projekt-auf-1
- OGC SenosorThings API: https://www.ogc.org/publications/standard/sensorthings/
- Telraam: https://telraam.net

## Quick Start Guide

- Teck-Stack: Docker, Python

Hinweis: Dieser Quick Start Guide wurde auf Debian getestet

Zum Ausführen des Service muss eine laufende SensorThings API vorhanden sein (siehe **FROST-Server** https://fraunhoferiosb.github.io/FROST-Server/deployment/docker.html). Die entprechende docker-compose Datei für den FROST-Server liegt auch in diesem Repository unter `src/config` und kann wie folgt verwendet werden: 

```bash
sudo docker compose up
```

1. Die URL der SensorThingsAPI (FROST-Server) muss in `src/config/config.json` im Feld `sensorThings_base_location` gesetzt werden (Default von FROST: `http://localhost:8080/FROST-Server/v1.1`)
2. Die Telraam API benötigt einen X-API-Key zur Autorisierung. Diesen ebenfalls in der Konfigurationsdatei im Feld `telraam_key_header.X-Api-Key` hinterlegen.
3. Dann kann zum Starten des Service `src/main.py` ausgeführt werden. Alternativ kann die Synchronisation mit `src/trigger_telraam_sync.py` einmalig ausgeführt werden.
4. Jeweils 10 Minuten vor einer vollen Stunde synchronisiert der Service die Telraam Daten.

`Logs` werden unter `src/logs` erstellt.

## Implementierung

- Tech-Stack: Python

Zur Überführung der Telraam-Daten an SensorThings wird ein Skript in Python
geschrieben, das stündlich die aktuellen SensorThings Entitäten mit
Telraam abgleicht und anpasst. Die Herausforderung liegt in den
unterschiedlichen Datenmodellen und den damit einhergehenden abweichenden
Verfahren. Zum Beispiel benötigt jede Telraam-Instanz ein zugehöriges
Segment, Segmente können aber zu unterschiedlichen Instanzen gehören. In
SensorThings wiederum kann eine Location (gemappt auf ein Telraam-Segment)
nicht ohne ein Thing (gemappt auf eine Telraam-Instanz) initiiert werden.