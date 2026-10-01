import sqlite3
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

import db as database

public_bp = Blueprint("public", __name__)


@public_bp.route("/", methods=["GET", "POST"])
def home():
    c = database.conn()
    subjects = c.execute(
        "SELECT * FROM subjects ORDER BY name COLLATE NOCASE"
    ).fetchall()

    if request.method == "POST":
        name = database.clean(request.form.get("student_name"))
        school = database.clean(request.form.get("school"))
        try:
            sid = int(request.form.get("subject_id", ""))
        except ValueError:
            sid = 0

        subject = c.execute(
            "SELECT * FROM subjects WHERE id=?", (sid,)
        ).fetchone()

        if len(name) < 2 or len(school) < 2 or not subject:
            c.close()
            flash("Please enter your name, school and select a subject.", "error")
            return redirect(url_for("public.home"))

        now = datetime.now()
        try:
            c.execute(
                """INSERT INTO attendance
                   (student_name, school, subject_id, attendance_date, attendance_time)
                   VALUES(?,?,?,?,?)""",
                (
                    name, school, sid,
                    now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"),
                ),
            )
            c.commit()
            flash(f"Attendance recorded for {subject['name']}.", "success")
        except sqlite3.IntegrityError:
            flash(f"{name} is already recorded for {subject['name']} today.", "error")

        c.close()
        return redirect(url_for("public.home"))

    c.close()
    return render_template("home.html", subjects=subjects)
