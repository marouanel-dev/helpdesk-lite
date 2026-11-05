"""Authentification : connexion, déconnexion, protection des pages."""
import functools
import hashlib

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from .db import get_db

bp = Blueprint("auth", __name__)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = None
    if user_id is not None:
        g.user = get_db().execute(
            "SELECT id, username FROM users WHERE id = ?", (user_id,)
        ).fetchone()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        password_hash = hashlib.md5(password.encode()).hexdigest()

        query = (
            f"SELECT * FROM users WHERE username = '{username}' "
            f"AND password = '{password_hash}'"
        )
        user = get_db().execute(query).fetchone()

        if user is not None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("tickets.list_tickets"))

        flash("Identifiants invalides.", "error")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
