# HausaufgabenPlaner

Eine selbst gehostete, passwortgeschützte Webanwendung zur Verwaltung von **Hausaufgaben, Terminen, Kalender und Stundenplan**.

Die Anwendung ist für den privaten Einsatz und den Dauerbetrieb auf einem lokalen Rechner oder Raspberry Pi ausgelegt. Alle Daten werden lokal gespeichert.

> Inspiriert von [davidmvos/planerapp](https://github.com/davidmvos/planerapp) – Danke an David Vos.

---

## Funktionen

### Aufgaben
- Aufgaben erstellen, bearbeiten und löschen
- Zuordnung zu Fächern
- Prioritäten und Fälligkeitsdaten
- Automatischer Fristvorschlag anhand des Stundenplans
- Übersicht der offenen Aufgaben

### Kalender
- Klassenarbeiten und Prüfungen
- Sonstige Termine
- Übersicht anstehender Ereignisse

### Stundenplan
- Individuell konfigurierbarer Stundenplan
- Fächer, Räume und Wochentage
- Individuelle Fachfarben
- Konfiguration über `config/timetable.json`

### Themes
- Mehrere visuelle Themes
- Auswahl direkt über die Einstellungen
- Speicherung der Auswahl in `config/theme.json`

### Sicherheit
- Passwortgeschützter Zugriff
- Session-Schutz über einen geheimen `SECRET_KEY`
- Keine Nutzung einer externen Cloud oder Datenbank

### Mobile Nutzung
- Responsive Oberfläche
- Optimiert für Smartphone und Tablet
- Funktioniert im Hoch- und Querformat

---

## Voraussetzungen

- **Python 3.11 oder neuer**
- `pip`

Abhängigkeiten:

```txt
Flask==3.0.3
Werkzeug==3.0.3
```

---

## Installation

### 1. Repository klonen

```bash
git clone https://github.com/JohannesDVos/HausaufgabenPlaner.git
cd HausaufgabenPlaner
```

### 2. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 3. `.env` erstellen

```bash
cp .env.example .env
```

Anschließend `.env` bearbeiten:

```env
HAUSAUFGABEN_PASSWORD=dein-sicheres-passwort
HAUSAUFGABEN_SECRET_KEY=ein-langer-zufaelliger-schluessel
```

> Die `.env` sollte **nicht in Git eingecheckt** werden.

### 4. Anwendung starten

```bash
python app.py
```

Anschließend ist die Anwendung normalerweise unter

```text
http://127.0.0.1:5000
```

erreichbar.

---

## Konfiguration

### Fächer

Die Fächer und ihre Farben werden in

```text
config/subjects.json
```

definiert.

### Stundenplan

Der Stundenplan wird in

```text
config/timetable.json
```

konfiguriert.

Dort werden unter anderem Unterrichtszeiten, Wochentage, Fächer und Räume festgelegt.

### Theme

Das aktuell ausgewählte Theme wird in

```text
config/theme.json
```

gespeichert.

Normalerweise muss diese Datei nicht manuell bearbeitet werden.

---

## Datensicherung

Für ein Backup sollten mindestens folgende Dateien gesichert werden:

| Datei / Verzeichnis | Inhalt |
|---|---|
| `data/hausaufgaben.db` | Aufgaben und Termine |
| `config/` | Fächer, Stundenplan und Theme |
| `.env` | Passwort und Secret Key |

Die `.env` sollte **separat und sicher** aufbewahrt werden und niemals öffentlich in ein Repository gelangen.

---

## Projektstruktur

```text
HausaufgabenPlaner/
├── app.py
├── requirements.txt
├── .env
├── .env.example
│
├── templates/
├── static/
│
├── config/
│   ├── subjects.json
│   ├── timetable.json
│   └── theme.json
│
└── data/
    └── hausaufgaben.db
```

---

## Hinweis

HausaufgabenPlaner ist als **private Single-User-Anwendung** konzipiert. Es gibt keine Mehrbenutzerverwaltung und keine Cloud-Anbindung.

Alle Daten bleiben standardmäßig auf dem Rechner bzw. Raspberry Pi, auf dem die Anwendung betrieben wird.