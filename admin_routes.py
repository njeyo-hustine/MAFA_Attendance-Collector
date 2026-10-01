import csv
import io
import sqlite3
from datetime import datetime

from flask import Blueprint, Response, flash, render_template, request
from werkzeug.security import generate_password_hash

import db as database
from auth import admin, required, super_required

admin_bp = Blueprint("admin_routes", __name__)


@admin_bp.route("/admin")
@required
def dashboard():
    a = admin()
    c = database.conn()
    subjects = c.execute(
        "SELECT * FROM subjects ORDER BY name COLLATE NOCASE"
    ).fetchall()

    sub = database.clean(request.args.get("subject"))
    school = database.clean(request.args.get("school"))
    date = database.clean(request.args.get("date"))
    search = database.clean(request.args.get("search"))
    sort = request.args.get("sort", "newest")

    q = """SELECT x.*, s.name subject_name FROM attendance x
           JOIN subjects s ON s.id=x.subject_id WHERE 1=1"""
    p = []

    if a["role"] == "subject_admin":
        q += " AND x.subject_id=?"
        p.append(a["subject_id"])
        sub = str(a["subject_id"])
    elif sub:
        try:
            q += " AND x.subject_id=?"
            p.append(int(sub))
        except ValueError:
            sub = ""

    if school:
        q += " AND x.school=?"
        p.append(school)
    if date:
        q += " AND x.attendance_date=?"
        p.append(date)
    if search:
        q += " AND x.student_name LIKE ?"
        p.append("%" + search + "%")

    order = {
        "name": "x.student_name COLLATE NOCASE ASC",
        "school": "x.school COLLATE NOCASE ASC,x.student_name COLLATE NOCASE ASC",
        "subject": "s.name COLLATE NOCASE ASC,x.student_name COLLATE NOCASE ASC",
        "oldest": "x.attendance_date ASC,x.attendance_time ASC",
    }.get(sort, "x.attendance_date DESC,x.attendance_time DESC")

    q += " ORDER BY " + order
    rows = c.execute(q, p).fetchall()

    sq = "SELECT DISTINCT x.school FROM attendance x"
    sp = []
    if a["role"] == "subject_admin":
        sq += " WHERE x.subject_id=?"
        sp = [a["subject_id"]]
    sq += " ORDER BY x.school COLLATE NOCASE"
    schools = c.execute(sq, sp).fetchall()

    if a["role"] == "subject_admin":
        total = c.execute(
            "SELECT COUNT(*) n FROM attendance WHERE subject_id=?",
            (a["subject_id"],),
        ).fetchone()["n"]
        today = c.execute(
            "SELECT COUNT(*) n FROM attendance WHERE subject_id=? AND attendance_date=?",
            (a["subject_id"], datetime.now().strftime("%Y-%m-%d")),
        ).fetchone()["n"]
    else:
        total = c.execute("SELECT COUNT(*) n FROM attendance").fetchone()["n"]
        today = c.execute(
            "SELECT COUNT(*) n FROM attendance WHERE attendance_date=?",
            (datetime.now().strftime("%Y-%m-%d"),),
        ).fetchone()["n"]

    c.close()
    return render_template(
        "dashboard.html", rows=rows, subjects=subjects, schools=schools,
        total=total, today=today, sub=sub, school=school, date=date,
        search=search, sort=sort,
    )


@admin_bp.route("/admin/export")
@required
def export():
    a = admin()
    c = database.conn()
    sub = database.clean(request.args.get("subject"))
    school = database.clean(request.args.get("school"))
    date = database.clean(request.args.get("date"))
    search = database.clean(request.args.get("search"))

    q = """SELECT x.student_name, x.school, s.name subject_name,
                  x.attendance_date, x.attendance_time
           FROM attendance x JOIN subjects s ON s.id=x.subject_id WHERE 1=1"""
    p = []

    if a["role"] == "subject_admin":
        q += " AND x.subject_id=?"
        p.append(a["subject_id"])
    elif sub:
        try:
            q += " AND x.subject_id=?"
            p.append(int(sub))
        except ValueError:
            pass

    if school:
        q += " AND x.school=?"
        p.append(school)
    if date:
        q += " AND x.attendance_date=?"
        p.append(date)
    if search:
        q += " AND x.student_name LIKE ?"
        p.append("%" + search + "%")

    q += " ORDER BY x.attendance_date DESC,x.attendance_time DESC"
    rows = c.execute(q, p).fetchall()
    c.close()

    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["Student Name", "School", "Subject", "Date", "Time"])
    for r in rows:
        w.writerow([
            r["student_name"], r["school"], r["subject_name"],
            r["attendance_date"], r["attendance_time"],
        ])

    return Response(
        out.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=mafa_attendance.csv"},
    )


@admin_bp.route("/admin/subjects", methods=["GET", "POST"])
@super_required
def subjects_page():
    c = database.conn()

    if request.method == "POST":
        name = database.clean(request.form.get("name"))
        try:
            c.execute("INSERT INTO subjects(name) VALUES(?)", (name,))
            c.commit()
            flash("Subject added.", "success")
        except sqlite3.IntegrityError:
            flash("Subject already exists.", "error")

    rows = c.execute(
        """SELECT s.*, COUNT(a.id) count FROM subjects s
           LEFT JOIN attendance a ON a.subject_id=s.id GROUP BY s.id
           ORDER BY s.name COLLATE NOCASE"""
    ).fetchall()

    c.close()
    return render_template("subjects.html", subjects=rows)


@admin_bp.route("/admin/users", methods=["GET", "POST"])
@super_required
def users_page():
    c = database.conn()
    subjects = c.execute("SELECT * FROM subjects ORDER BY name").fetchall()

    if request.method == "POST":
        u = database.clean(request.form.get("username"))
        p = request.form.get("password", "")
        role = request.form.get("role", "subject_admin")
        sid = request.form.get("subject_id")

        if len(p) < 8 or not u:
            flash("Username and password (8+ characters) are required.", "error")
        elif role == "subject_admin" and not sid:
            flash("Choose a subject.", "error")
        else:
            try:
                c.execute(
                    "INSERT INTO admins(username,password_hash,role,subject_id) VALUES(?,?,?,?)",
                    (
                        u, generate_password_hash(p), role,
                        int(sid) if role == "subject_admin" else None,
                    ),
                )
                c.commit()
                flash("Administrator created.", "success")
            except sqlite3.IntegrityError:
                flash("Username already exists.", "error")

    users = c.execute(
        """SELECT a.*, s.name subject_name FROM admins a
           LEFT JOIN subjects s ON s.id=a.subject_id
           ORDER BY a.username COLLATE NOCASE"""
    ).fetchall()

    c.close()
    return render_template("users.html", users=users, subjects=subjects)
