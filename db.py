import os
import sqlite3

from werkzeug.security import generate_password_hash

import config

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "mafa_attendance.db")


def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c


def init_db():
    c = conn()
    c.execute("""CREATE TABLE IF NOT EXISTS subjects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE COLLATE NOCASE NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS admins(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE COLLATE NOCASE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        subject_id INTEGER,
        FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE SET NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS attendance(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT NOT NULL,
        school TEXT NOT NULL,
        subject_id INTEGER NOT NULL,
        attendance_date TEXT NOT NULL,
        attendance_time TEXT NOT NULL,
        FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE RESTRICT,
        UNIQUE(student_name COLLATE NOCASE, school COLLATE NOCASE,
               subject_id, attendance_date))""")

    for s in config.SUBJECTS:
        c.execute("INSERT OR IGNORE INTO subjects(name) VALUES(?)", (s,))

    if not c.execute(
        "SELECT id FROM admins WHERE username=?",
        (config.SUPER_ADMIN_USERNAME,)
    ).fetchone():
        c.execute(
            "INSERT INTO admins(username,password_hash,role) VALUES(?,?,?)",
            (
                config.SUPER_ADMIN_USERNAME,
                generate_password_hash(config.SUPER_ADMIN_PASSWORD),
                "super_admin",
            ),
        )

    c.commit()
    c.close()


def clean(v):
    return " ".join((v or "").strip().split())
