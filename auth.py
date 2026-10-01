from functools import wraps

from flask import (
    Blueprint, flash, redirect, render_template,
    request, session, url_for,
)
from werkzeug.security import check_password_hash

import db as database

auth_bp = Blueprint("auth", __name__)


def admin():
    aid = session.get("admin_id")
    if not aid:
        return None
    c = database.conn()
    a = c.execute(
        """SELECT a.*, s.name subject_name FROM admins a
           LEFT JOIN subjects s ON s.id=a.subject_id WHERE a.id=?""",
        (aid,),
    ).fetchone()
    c.close()
    return a


def required(view):
    @wraps(view)
    def f(*args, **kwargs):
        if not admin():
            session.clear()
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return f


def super_required(view):
    @wraps(view)
    def f(*args, **kwargs):
        a = admin()
        if not a or a["role"] != "super_admin":
            return redirect(url_for("admin_routes.dashboard"))
        return view(*args, **kwargs)
    return f


@auth_bp.route("/admin/login", methods=["GET", "POST"])
def login():
    if admin():
        return redirect(url_for("admin_routes.dashboard"))

    if request.method == "POST":
        u = database.clean(request.form.get("username"))
        p = request.form.get("password", "")
        c = database.conn()
        a = c.execute("SELECT * FROM admins WHERE username=?", (u,)).fetchone()
        c.close()

        if a and check_password_hash(a["password_hash"], p):
            session.clear()
            session["admin_id"] = a["id"]
            return redirect(url_for("admin_routes.dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@auth_bp.route("/admin/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
