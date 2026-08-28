# HausaufgabenPlaner

Eine selbst gehostete, passwortgeschützte Webanwendung zur Verwaltung von Hausaufgaben, Terminen, Kalender und Stundenplan – konzipiert für den Dauerbetrieb auf einem lokalen Rechner oder Raspberry Pi.

> Inspiriert von [davidmvos/planerapp](https://github.com/davidmvos/planerapp) – Danke an David Vos.

---

## Inhaltsverzeichnis

- [Überblick](#überblick)
- [Funktionen](#funktionen)
- [Projektstruktur](#projektstruktur)
- [Voraussetzungen](#voraussetzungen)
- [Installation](#installation)
- [Konfiguration](#konfiguration)
- [Deployment](#deployment)
- [Mobile Nutzung](#mobile-nutzung)
- [Datensicherung](#datensicherung)

---

## Überblick

HausaufgabenPlaner ist eine lokale Single-User-Webanwendung auf Basis von Flask und SQLite. Alle Daten werden ausschließlich lokal gespeichert – ohne Cloud-Abhängigkeit, ohne externe Datenbank.

**Kernfunktionen auf einen Blick:**

- Aufgaben anlegen, bearbeiten und nach Priorität organisieren
- Aufgaben Fächern zuordnen, mit automatischer Fristvorschlag anhand des nächsten Fachtermins
- Klassenarbeiten und Prüfungen im Kalender erfassen
- Stundenplan hinterlegen und farblich visualisieren
- Mehrere visuelle Themes auswählen
- Passwortgeschützter Zugriff mit Session-Schutz

---

## Funktionen

### Aufgaben

- Erfassung mit Titel, Fach, Priorität, Erstell- und Fälligkeitsdatum
- Übersicht offener Aufgaben, sortiert nach Dringlichkeit
- Löschen einzelner Einträge

### Kalender

- Eintragen von Klassenarbeiten, Prüfungen und sonstigen Terminen
- Kompakte Übersicht anstehender Ereignisse

### Stundenplan

- Konfiguration über `config/timetable.json`
- Wochenübersicht mit Fächern und Räumen
- Fachfarben werden direkt in der Darstellung übernommen

### Themes

- Mehrere visuelle Themes verfügbar
- Auswahl über die Einstellungsseite
- Persistente Speicherung der Theme-Wahl in `config/theme.json`

### Sicherheit

- Passwortbasierter Login
- Session-Schutz über `SECRET_KEY`
- Kein Zugriff ohne erfolgreiche Anmeldung

---

## Projektstruktur

```
HausaufgabenPlaner/
├── app.py                    # Hauptanwendung (Flask, Datenbanklogik)
├── requirements.txt          # Python-Abhängigkeiten
├── .env                      # Passwort und Secret Key (nicht einchecken)
├── .env.example              # Vorlage für die .env
├── templates/                # HTML-Templates (Jinja2)
├── static/                   # CSS und statische Dateien
├── config/
│   ├── subjects.json         # Fächer und Farben
│   ├── timetable.json        # Stundenplan, Zeitraster, Unterrichtszuteilung
│   └── theme.json            # Aktuell gewähltes Theme
└── data/
    └── hausaufgaben.db       # Lokale SQLite-Datenbank
```

---

## Voraussetzungen

- Python 3.11 oder neuer
- `pip`

**Abhängigkeiten** (`requirements.txt`):

```
Flask==3.0.3
Werkzeug==3.0.3
```

---

## Installation

```bash
# 1. Repository klonen
git clone https://github.com/JohannesDVos/HausaufgabenPlaner.git
cd HausaufgabenPlaner

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Umgebungsdatei anlegen
cp .env.example .env
```

Anschließend `.env` mit eigenen Werten befüllen (siehe [Konfiguration](#konfiguration)).

```bash
# 4. Anwendung starten
python app.py
```

Die App ist danach unter `http://127.0.0.1:5000` erreichbar.

---

## Konfiguration

### Umgebungsvariablen (`.env`)

```env
HAUSAUFGABEN_PASSWORD=dein-sicheres-passwort
HAUSAUFGABEN_SECRET_KEY=ein-langer-zufaelliger-schluessel
```

> **Hinweis:** Der `SECRET_KEY` schützt die Login-Session. Eine Änderung macht alle bestehenden Anmeldungen ungültig.

### Fächer (`config/subjects.json`)

Fächer und ihre Anzeigefarben werden hier zentral gepflegt und in der gesamten App konsistent verwendet.

### Stundenplan (`config/timetable.json`)

Definiert das Stundenraster, die Wochentage sowie die Zuordnung von Fach, Stunde, Tag und Raum.

### Theme (`config/theme.json`)

Wird automatisch über die Einstellungsseite der App geschrieben. Kein manueller Eingriff erforderlich.

---

## Deployment Beispiele

### Lokaler Rechner

Geeignet für Tests und den privaten Einsatz im Heimnetz.

```bash
git clone https://github.com/JohannesDVos/HausaufgabenPlaner.git
cd HausaufgabenPlaner
pip install -r requirements.txt
cp .env.example .env
# .env anpassen
python app.py
```

### Raspberry Pi (Dauerbetrieb)

Der Raspberry Pi eignet sich besonders für den kontinuierlichen Betrieb: geringer Stromverbrauch, keine Cloud-Abhängigkeit, alle Daten bleiben im Heimnetz.

**Voraussetzungen:**
- Raspberry Pi OS
- Python 3.11+, `pip`

**Installation:**

```bash
# Projekt auf den Raspberry Pi kopieren
git clone https://github.com/JohannesDVos/HausaufgabenPlaner.git /home/pi/HausaufgabenPlaner
cd /home/pi/HausaufgabenPlaner

# Virtuelle Umgebung anlegen und Abhängigkeiten installieren
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Konfiguration anlegen
cp .env.example .env
# .env anpassen
```

**Autostart mit systemd: NICHT GETESTET**

Service-Datei unter `/etc/systemd/system/hausaufgabenplaner.service` ablegen:

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

Dienst aktivieren und starten:

```bash
sudo systemctl daemon-reload
sudo systemctl enable hausaufgabenplaner
sudo systemctl start hausaufgabenplaner
sudo systemctl status hausaufgabenplaner
```

---

## Mobile Nutzung

Die Oberfläche ist für die Nutzung auf iPhone und iPad optimiert:

- Responsives Layout für Hoch- und Querformat
- Große Schaltflächen und klare Abstände
- Kompakte Darstellung von Kalender und Stundenplan

---

## Datensicherung

Es wird empfohlen, folgende Dateien regelmäßig zu sichern:

| Datei / Verzeichnis | Inhalt |
|---|---|
| `data/hausaufgaben.db` | Alle Aufgaben und Termine (SQLite) |
| `config/` | Fächer, Stundenplan, Theme |
| `.env` | Passwort und Secret Key – **separat und sicher aufbewahren** |

---

## Hinweis

HausaufgabenPlaner ist bewusst als Single-User-Lösung ausgelegt und auf einfache Bedienung, lokale Datenhaltung und den privaten Einsatz optimiert. Es ist keine Mehrbenutzerverwaltung vorgesehen.