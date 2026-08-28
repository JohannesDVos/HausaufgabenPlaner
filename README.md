# HausaufgabenPlaner

HausaufgabenPlaner ist eine lokale, geschützte Single-User-WebApp für Aufgaben, Termine, Kalender und Stundenplan. Die App ist für den dauerhaften Einsatz auf einem eigenen Rechner oder Raspberry Pi gedacht und speichert alle Daten lokal.

## Überblick

Mit der App kannst du:

- Aufgaben anlegen, bearbeiten, löschen und nach Priorität organisieren
- Aufgaben einem Fach zuordnen
- Erstelldatum und Fälligkeitsdatum pflegen
- eine automatische Frist-Vorbelegung anhand des nächsten Fachtermins nutzen
- Klassenarbeiten und andere Termine im Kalender erfassen
- einen Stundenplan hinterlegen und anzeigen
- Fächer zentral mit Farben verwalten
- zwischen mehreren Themes wechseln
- die App mit Passwort schützen

## Dank

Danke an David M. Vos für die Idee und Inspiration zu diesem Projekt:
[github.com/davidmvos/planerapp](https://github.com/davidmvos/planerapp)

## Funktionen im Detail

### Aufgaben

- Titel, Fach, Priorität, Erstelldatum und Fälligkeitsdatum
- offene Aufgabenübersicht
- klare Darstellung nach Dringlichkeit
- Löschen einzelner Aufgaben

### Kalender

- Klassenarbeiten, Prüfungen und sonstige Termine
- kompakte Übersicht der anstehenden Ereignisse

### Stundenplan

- Konfiguration direkt über Projektdateien
- Wochenübersicht mit Fächern und Räumen
- Fachfarben werden in der Darstellung verwendet

### Themes

- mehrere visuelle Themes
- Auswahl über die Einstellungsseite
- Theme bleibt für den nächsten Aufruf gespeichert

### Sicherheit

- Login per Passwort
- Zugriff auf die App nur nach erfolgreicher Anmeldung
- Session-Schutz über `SECRET_KEY`

## Projektstruktur

- `app.py` - Hauptanwendung mit Flask, Datenbankzugriff und Logik
- `templates/` - HTML-Templates
- `static/` - CSS und statische Dateien
- `config/subjects.json` - Fächer und Farben
- `config/timetable.json` - Stundenplan, Zeitraster und Unterrichtszuteilung
- `config/theme.json` - aktuell gewähltes Theme
- `data/hausaufgaben.db` - lokale SQLite-Datenbank
- `.env` - Passwort und Secret-Key für den Betrieb

## Voraussetzungen

- Python 3.11 oder neuer
- `pip`

## Installation

1. Repository lokal öffnen.
2. Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

3. `.env` prüfen oder anlegen:

```env
HAUSAUFGABEN_PASSWORD=hausaufgaben
HAUSAUFGABEN_SECRET_KEY=change-me-in-production
```

## Lokaler Start

```bash
python app.py
```

Danach ist die App normalerweise unter `http://127.0.0.1:5000` erreichbar.

## Erste Einrichtung

### 1. Passwort setzen

Passe in der `.env` das Passwort an:

```env
HAUSAUFGABEN_PASSWORD=dein-sicheres-passwort
```

### 2. Secret Key setzen

Nutze für den produktiven Betrieb einen langen, zufälligen `SECRET_KEY`:

```env
HAUSAUFGABEN_SECRET_KEY=ein-langer-zufaelliger-zufaelliger-schluessel
```

Der Key schützt die Login-Session. Wenn du ihn änderst, werden bestehende Anmeldungen ungültig.

### 3. Fächer anpassen

In `config/subjects.json` kannst du deine Fächer und Farben pflegen.

### 4. Stundenplan pflegen

In `config/timetable.json` definierst du:

- das Stundenraster
- die Wochentage
- Fach, Stunde, Tag und Raum

### 5. Theme auswählen

Die verfügbaren Themes werden in der App über die Einstellungsseite gewählt und in `config/theme.json` gespeichert.

## Datenhaltung

Die App verwendet lokal eine SQLite-Datenbank. Dadurch bleiben Aufgaben, Termine und weitere Daten auch nach einem Neustart erhalten.

Empfohlene Sicherung:

- regelmäßig die Datei `data/hausaufgaben.db` sichern
- zusätzlich die Dateien in `config/` sichern
- `.env` separat aufbewahren

## Deployment

### Variante 1: Direkt auf einem lokalen Rechner

1. Projektverzeichnis auf den Rechner kopieren.
2. Python installieren.
3. Abhängigkeiten mit `pip install -r requirements.txt` installieren.
4. `.env` anlegen oder anpassen.
5. `python app.py` starten.

Diese Variante eignet sich für Tests und den privaten Einsatz im Heimnetz.

### Variante 2: Raspberry Pi

Der Raspberry Pi ist ein passender Zielrechner für den Dauerbetrieb, weil die App keine externe Datenbank und keine Cloud benötigt.

#### Voraussetzungen auf dem Raspberry Pi

- Raspberry Pi OS
- Python 3.11 oder kompatible Version
- `pip`
- ein Ordner für das Projekt, zum Beispiel `/home/pi/HausaufgabenPlaner`

#### Installation auf dem Raspberry Pi

1. Projekt auf den Raspberry Pi kopieren, zum Beispiel per `git clone` oder per Dateiübertragung.
2. In das Projektverzeichnis wechseln.
3. Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

4. `.env` anlegen:

```env
HAUSAUFGABEN_PASSWORD=dein-passwort
HAUSAUFGABEN_SECRET_KEY=ein-zufaelliger-produktions-schluessel
```

5. App testweise starten:

```bash
python app.py
```

6. Im Browser des Raspberry Pi oder von einem anderen Gerät im selben Netzwerk öffnen.

#### Beispiel für einen Autostart mit systemd

Wenn die App beim Start des Raspberry Pi automatisch laufen soll, kannst du einen systemd-Dienst anlegen.

Beispiel für eine Service-Datei:

```ini
[Unit]
Description=HausaufgabenPlaner
After=network.target

[Service]
WorkingDirectory=/home/pi/HausaufgabenPlaner
ExecStart=/home/pi/HausaufgabenPlaner/.venv/bin/python /home/pi/HausaufgabenPlaner/app.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Typischer Ablauf:

1. Virtuelle Umgebung im Projektordner anlegen.
2. Abhängigkeiten in diese Umgebung installieren.
3. Die Service-Datei unter `/etc/systemd/system/hausaufgabenplaner.service` ablegen.
4. Dienst aktivieren und starten.

Beispiel:

```bash
sudo systemctl daemon-reload
sudo systemctl enable hausaufgabenplaner
sudo systemctl start hausaufgabenplaner
sudo systemctl status hausaufgabenplaner
```

#### Warum Raspberry Pi geeignet ist

- geringer Stromverbrauch
- dauerhafter lokaler Betrieb
- keine externe Abhängigkeit von Cloud-Diensten
- Daten bleiben im Heimnetz

## Mobile Nutzung

Die Oberfläche ist für iPhone und iPad optimiert:

- gute Bedienbarkeit auf kleinen Displays
- geeignet für Hoch- und Querformat
- große Schaltflächen und klare Abstände
- kompakte Darstellung von Kalender und Stundenplan

## Wartung

Empfohlen wird:

- regelmäßig `data/hausaufgaben.db` sichern
- `config/subjects.json`, `config/timetable.json` und `config/theme.json` mit sichern
- Passwort und Secret Key getrennt verwalten

## Hinweis

Diese App ist bewusst als Single-User-Lösung ausgelegt. Sie ist auf einfache Bedienung, lokale Speicherung und den privaten Einsatz optimiert.
