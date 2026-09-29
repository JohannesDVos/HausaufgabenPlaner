from __future__ import annotations

import json
import os
import sqlite3
from datetime import date, datetime
from functools import wraps
from datetime import timedelta
from pathlib import Path
from typing import Any, Iterable

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
DB_PATH = DATA_DIR / "hausaufgaben.db"
SUBJECTS_PATH = CONFIG_DIR / "subjects.json"
TIMETABLE_PATH = CONFIG_DIR / "timetable.json"
THEME_PATH = CONFIG_DIR / "theme.json"
ENV_PATH = BASE_DIR / ".env"
DEFAULT_PASSWORD = "hausaufgaben"
PASSWORD_ENV_KEY = "HAUSAUFGABEN_PASSWORD"


def load_dotenv_file(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_dotenv_file()

app = Flask(__name__)
app.secret_key = os.environ.get("HAUSAUFGABEN_SECRET_KEY", "change-me-in-production")


def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def default_subjects() -> list[dict[str, str]]:
    return [
        {"name": "Mathe", "color": "#2563eb"},
        {"name": "Deutsch", "color": "#dc2626"},
        {"name": "Englisch", "color": "#16a34a"},
        {"name": "Bio", "color": "#0891b2"},
        {"name": "Physik", "color": "#7c3aed"},
    ]


def default_timetable() -> dict[str, Any]:
    return {
        "periods": [
            {"slot": 1, "start": "08:00", "end": "08:45"},
            {"slot": 2, "start": "08:50", "end": "09:35"},
            {"slot": 3, "start": "09:50", "end": "10:35"},
            {"slot": 4, "start": "10:40", "end": "11:25"},
            {"slot": 5, "start": "11:30", "end": "12:15"},
            {"slot": 6, "start": "12:20", "end": "13:05"},
            {"slot": 7, "start": "13:10", "end": "13:55"},
        ],
        "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "lessons": [
            {"day": "Mon", "slot": 1, "subject": "Mathe", "room": "201"},
            {"day": "Mon", "slot": 2, "subject": "Deutsch", "room": "101"},
            {"day": "Tue", "slot": 3, "subject": "Englisch", "room": "304"},
        ],
    }


def default_theme() -> dict[str, str]:
    return {"active": "midnight"}


def theme_definitions() -> dict[str, dict[str, str]]:
    return {
        "midnight": {
            "bg": "#0b1220",
            "surface": "rgba(15, 23, 42, 0.92)",
            "surface_2": "rgba(30, 41, 59, 0.96)",
            "text": "#e5eefb",
            "muted": "#8ca0b8",
            "line": "rgba(148, 163, 184, 0.18)",
            "accent": "#38bdf8",
            "accent_soft": "rgba(56, 189, 248, 0.16)",
            "accent_text": "#082f49",
            "danger": "#fb7185",
            "shadow": "0 18px 48px rgba(0, 0, 0, 0.34)",
        },
        "paper": {
            "bg": "#f4f1ea",
            "surface": "rgba(255, 255, 255, 0.92)",
            "surface_2": "rgba(255, 255, 255, 0.98)",
            "text": "#111827",
            "muted": "#5b6472",
            "line": "rgba(17, 24, 39, 0.10)",
            "accent": "#0f766e",
            "accent_soft": "rgba(15, 118, 110, 0.12)",
            "accent_text": "#ffffff",
            "danger": "#b91c1c",
            "shadow": "0 18px 48px rgba(17, 24, 39, 0.12)",
        },
        "forest": {
            "bg": "#07130f",
            "surface": "rgba(8, 31, 24, 0.94)",
            "surface_2": "rgba(15, 45, 35, 0.98)",
            "text": "#eaf7ef",
            "muted": "#9bb6a7",
            "line": "rgba(167, 243, 208, 0.14)",
            "accent": "#86efac",
            "accent_soft": "rgba(134, 239, 172, 0.14)",
            "accent_text": "#052e16",
            "danger": "#f87171",
            "shadow": "0 18px 48px rgba(0, 0, 0, 0.32)",
        },
        "paper-dark": {
            "bg": "#181614",
            "surface": "rgba(38, 34, 30, 0.94)",
            "surface_2": "rgba(50, 45, 40, 0.98)",
            "text": "#f5eee5",
            "muted": "#b8aa9b",
            "line": "rgba(245, 238, 229, 0.16)",
            "accent": "#f0b56b",
            "accent_soft": "rgba(240, 181, 107, 0.16)",
            "accent_text": "#3b2410",
            "danger": "#f87171",
            "shadow": "0 18px 48px rgba(0, 0, 0, 0.34)",
        },
    }


def load_json_file(path: Path, fallback: Any) -> Any:
    if not path.exists():
        path.write_text(json.dumps(fallback, indent=2, ensure_ascii=False), encoding="utf-8")
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        path.write_text(json.dumps(fallback, indent=2, ensure_ascii=False), encoding="utf-8")
        return fallback


def save_json_file(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def init_config_files() -> None:
    load_json_file(SUBJECTS_PATH, default_subjects())
    load_json_file(TIMETABLE_PATH, default_timetable())
    load_json_file(THEME_PATH, default_theme())


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(_: BaseException | None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    ensure_directories()
    init_config_files()
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    try:
        db.executescript(
            """
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                priority INTEGER NOT NULL,
                created_on TEXT NOT NULL,
                due_on TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                event_date TEXT NOT NULL,
                event_type TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT ''
            );
            """
        )
    finally:
        db.close()


def get_setting(db: sqlite3.Connection, key: str) -> str | None:
    row = db.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return None if row is None else str(row["value"])


def set_setting(db: sqlite3.Connection, key: str, value: str) -> None:
    db.execute(
        "INSERT INTO settings(key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    db.commit()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def load_subjects() -> list[dict[str, str]]:
    data = load_json_file(SUBJECTS_PATH, default_subjects())
    return [subject for subject in data if subject.get("name")]


def load_timetable() -> dict[str, Any]:
    data = load_json_file(TIMETABLE_PATH, default_timetable())
    data.setdefault("periods", [])
    data.setdefault("weekdays", ["Mon", "Tue", "Wed", "Thu", "Fri"])
    data.setdefault("lessons", [])
    return data


def load_theme() -> dict[str, str]:
    data = load_json_file(THEME_PATH, default_theme())
    active = str(data.get("active", "midnight"))
    if active not in theme_definitions():
        active = "midnight"
    return {"active": active, **theme_definitions()[active]}


def next_subject_date(subject: str, start_from: date | None = None) -> date | None:
    timetable = load_timetable()
    lessons = timetable.get("lessons", [])
    weekdays = timetable.get("weekdays", ["Mon", "Tue", "Wed", "Thu", "Fri"])
    day_index_map = {day: idx for idx, day in enumerate(weekdays)}
    if subject not in {lesson.get("subject") for lesson in lessons}:
        return None
    start = start_from or date.today()
    for offset in range(0, 15):
        candidate = start + timedelta(days=offset)
        weekday_name = candidate.strftime("%a")
        if weekday_name not in day_index_map:
            continue
        for lesson in lessons:
            if lesson.get("subject") == subject and lesson.get("day") == weekday_name:
                return candidate
    return None


def subject_map() -> dict[str, str]:
    return {subject["name"]: subject.get("color", "#64748b") for subject in load_subjects()}


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


@app.before_request
def bootstrap() -> None:
    init_db()


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        password = request.form.get("password", "")
        expected_password = os.environ.get(PASSWORD_ENV_KEY, DEFAULT_PASSWORD)
        if password == expected_password:
            session["logged_in"] = True
            flash("Erfolgreich angemeldet.", "success")
            return redirect(url_for("dashboard"))
        flash("Ungültiges Passwort.", "error")
    return render_template("login.html", theme=load_theme())


@app.route("/logout")
def logout():
    session.clear()
    flash("Du wurdest abgemeldet.", "success")
    return redirect(url_for("login"))


@app.route("/")
@login_required
def dashboard():
    db = get_db()
    tasks = [row_to_dict(row) for row in db.execute("SELECT * FROM tasks WHERE completed = 0 ORDER BY priority DESC, due_on ASC, id DESC")]
    events = [row_to_dict(row) for row in db.execute("SELECT * FROM events ORDER BY event_date ASC, id DESC")]
    today = date.today()
    overdue = sum(1 for task in tasks if task["due_on"] < today.isoformat())
    due_soon = sum(1 for task in tasks if 0 <= (parse_date(task["due_on"]) - today).days <= 7)
    return render_template(
        "dashboard.html",
        tasks=tasks,
        events=events,
        overdue=overdue,
        due_soon=due_soon,
        today=today,
        subjects=load_subjects(),
        subject_colors=subject_map(),
        timetable=load_timetable(),
        theme=load_theme(),
    )


@app.route("/settings")
@login_required
def settings():
    return render_template(
        "settings.html",
        theme=load_theme(),
        themes=theme_definitions(),
        active_theme=load_theme()["active"],
    )


@app.route("/tasks", methods=["POST"])
@login_required
def add_task():
    title = request.form.get("title", "").strip()
    subject = request.form.get("subject", "").strip()
    due_on = request.form.get("due_on", "").strip()
    priority = int(request.form.get("priority", "2"))
    created_on = request.form.get("created_on", "").strip() or date.today().isoformat()
    suggested_due = request.form.get("suggested_due_on", "").strip()
    if not due_on and suggested_due:
        due_on = suggested_due
    if not title or not subject or not due_on:
        flash("Titel, Fach und Fälligkeitsdatum sind erforderlich.", "error")
        return redirect(url_for("dashboard"))
    get_db().execute(
        "INSERT INTO tasks(title, subject, priority, created_on, due_on, completed) VALUES (?, ?, ?, ?, ?, 0)",
        (title, subject, priority, created_on, due_on),
    )
    get_db().commit()
    flash("Aufgabe gespeichert.", "success")
    return redirect(url_for("dashboard"))


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id: int):
    get_db().execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    get_db().commit()
    flash("Aufgabe gelöscht.", "success")
    return redirect(url_for("dashboard"))


@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id: int):
    db = get_db()
    db.execute(
        "UPDATE tasks SET completed = CASE completed WHEN 1 THEN 0 ELSE 1 END WHERE id = ?",
        (task_id,),
    )
    db.commit()
    flash("Aufgabenstatus aktualisiert.", "success")
    return redirect(url_for("dashboard"))


@app.route("/events", methods=["POST"])
@login_required
def add_event():
    title = request.form.get("title", "").strip()
    subject = request.form.get("subject", "").strip()
    event_date = request.form.get("event_date", "").strip()
    event_type = request.form.get("event_type", "").strip() or "Klausur"
    notes = request.form.get("notes", "").strip()
    if not title or not subject or not event_date:
        flash("Titel, Fach und Datum sind erforderlich.", "error")
        return redirect(url_for("dashboard"))
    get_db().execute(
        "INSERT INTO events(title, subject, event_date, event_type, notes) VALUES (?, ?, ?, ?, ?)",
        (title, subject, event_date, event_type, notes),
    )
    get_db().commit()
    flash("Termin gespeichert.", "success")
    return redirect(url_for("dashboard"))


@app.route("/events/<int:event_id>/delete", methods=["POST"])
@login_required
def delete_event(event_id: int):
    get_db().execute("DELETE FROM events WHERE id = ?", (event_id,))
    get_db().commit()
    flash("Termin gelöscht.", "success")
    return redirect(url_for("dashboard"))


@app.route("/settings/theme", methods=["POST"])
@login_required
def update_theme():
    active = request.form.get("theme", "midnight").strip()
    if active not in theme_definitions():
        flash("Ungültiges Theme.", "error")
        return redirect(url_for("settings"))
    save_json_file(THEME_PATH, {"active": active})
    flash("Theme gespeichert.", "success")
    return redirect(url_for("settings"))


@app.route("/api/next-due-date")
@login_required
def api_next_due_date():
    subject = request.args.get("subject", "").strip()
    if not subject:
        return app.response_class(json.dumps({"due_on": None}), mimetype="application/json")
    due = next_subject_date(subject)
    return app.response_class(json.dumps({"due_on": due.isoformat() if due else None}), mimetype="application/json")


@app.route("/api/export")
@login_required
def export_data():
    db = get_db()
    payload = {
        "tasks": [row_to_dict(row) for row in db.execute("SELECT * FROM tasks ORDER BY id DESC")],
        "events": [row_to_dict(row) for row in db.execute("SELECT * FROM events ORDER BY event_date ASC, id DESC")],
        "subjects": load_subjects(),
        "timetable": load_timetable(),
    }
    return app.response_class(json.dumps(payload, indent=2, ensure_ascii=False), mimetype="application/json")


@app.errorhandler(404)
def not_found(_: Exception):
    return render_template("404.html", theme=load_theme()), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
