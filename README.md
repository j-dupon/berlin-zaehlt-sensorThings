# Berlin zählt Mobilität: Überführung der Telraam-Daten in SensorThings API

Dieses Projekt hat zum Ziel, die in Berlin erhobenen Telraam-Daten an eine SensorThings API zu überführen. SensorThings ist ein Standard des Open Geospacial Consortium (OGC) und ermöglicht die problemlose Anbindung anderer SensorThings Datenquellen. Durch die Erweiterung der Telraam-Daten mit anderen Quellen sollen in diesem Projekt mithilfe der Senosrthings API neue Erkenntnisse gewonnen werden. 

- Berlin zählt Mobilität: https://berlin.adfc.de/artikel/berlin-zaehlt-mobilitaet-adfc-berlin-dlr-rufen-zu-citizen-science-projekt-auf-1
- OGC SenosorThings API: https://www.ogc.org/publications/standard/sensorthings/
- Telraam: https://telraam.net

## Quick Start Guide

Zum Ausführen des Synchronisations-Service muss eine laufende SensorThings API vorhanden sein (siehe https://fraunhoferiosb.github.io/FROST-Server/deployment/docker.html) und die URL für den Server in `src/config/config.json` im Feld `sensorThings_base_location` gesetzt werden. Zusätzlich benötigt die Telraam API einen X-API-Key zur Autorisierung. Diesen ebenfalls in der Konfigurationsdatei im Feld `telraam_key_header.X-Api-Key` hinterlegen. Dann kann zum Starten des Skripts `src/main.py` ausgeführt werden.

## Implementierung

- Tech-Stack: Python

Zur Überführung der Telraam-Daten an SensorThings wird ein Skript in Python
geschrieben, das alle n Minuten die aktuellen SensorThings Entitäten mit
Telraam abgleicht und anpasst. Die Herausforderung liegt in den
unterschiedlichen Datenmodellen und den damit einhergehenden abweichenden
Verfahren. Zum Beispiel benötigt jede Telraam-Instanz ein zugehöriges
Segment, Segmente können aber zu unterschiedlichen Instanzen gehören. In
SensorThings wiederum kann eine Location (gemappt auf ein Telraam-Segment)
nicht ohne ein Thing (gemappt auf eine Telraam-Instanz) initiiert werden.

## TODO

- Verbesserung des Quick Start Guide durch ein install/start-Skript mit Einbindung einer FROST Initialisierung
- Visualisierung der Daten
- ...
