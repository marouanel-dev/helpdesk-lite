"""Gestion des tickets : liste, création, consultation, changement de statut."""
from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from .auth import login_required
from .db import get_db

bp = Blueprint("tickets", __name__, url_prefix="/tickets")

STATUSES = ["Ouvert", "En cours", "Résolu"]
PRIORITIES = ["Basse", "Moyenne", "Haute"]
CSS_CLASSES = {
    "Ouvert": "open", "En cours": "progress", "Résolu": "done",
    "Basse": "low", "Moyenne": "medium", "Haute": "high",
}


@bp.app_template_filter("css")
def css_class(value):
    return CSS_CLASSES.get(value, "default")


def get_ticket(ticket_id):
    ticket = get_db().execute(
        "SELECT t.*, u.username AS author FROM tickets t "
        "JOIN users u ON u.id = t.author_id WHERE t.id = ?",
        (ticket_id,),
    ).fetchone()
    if ticket is None:
        abort(404)
    return ticket


@bp.route("/")
@login_required
def list_tickets():
    db = get_db()
    status = request.args.get("status")
    if status in STATUSES:
        tickets = db.execute(
            "SELECT t.*, u.username AS author FROM tickets t "
            "JOIN users u ON u.id = t.author_id WHERE t.status = ? ORDER BY t.id DESC",
            (status,),
        ).fetchall()
    else:
        status = None
        tickets = db.execute(
            "SELECT t.*, u.username AS author FROM tickets t "
            "JOIN users u ON u.id = t.author_id ORDER BY t.id DESC"
        ).fetchall()

    counts = dict.fromkeys(STATUSES, 0)
    for row in db.execute("SELECT status, COUNT(*) AS n FROM tickets GROUP BY status"):
        counts[row["status"]] = row["n"]

    return render_template(
        "tickets.html", tickets=tickets, statuses=STATUSES, current=status, counts=counts
    )


@bp.route("/new", methods=("GET", "POST"))
@login_required
def create():
    form = {"title": "", "description": "", "priority": "Moyenne"}
    if request.method == "POST":
        form = {
            "title": request.form.get("title", "").strip(),
            "description": request.form.get("description", "").strip(),
            "priority": request.form.get("priority", ""),
        }
        if not form["title"] or not form["description"]:
            flash("Le titre et la description sont obligatoires.", "error")
        elif form["priority"] not in PRIORITIES:
            flash("Priorité invalide.", "error")
        else:
            db = get_db()
            cursor = db.execute(
                "INSERT INTO tickets (title, description, priority, author_id) "
                "VALUES (?, ?, ?, ?)",
                (form["title"], form["description"], form["priority"], g.user["id"]),
            )
            db.commit()
            flash("Ticket créé.", "success")
            return redirect(url_for("tickets.detail", ticket_id=cursor.lastrowid))

    return render_template("ticket_new.html", form=form, priorities=PRIORITIES)


@bp.route("/<int:ticket_id>")
@login_required
def detail(ticket_id):
    return render_template(
        "ticket_detail.html", ticket=get_ticket(ticket_id), statuses=STATUSES
    )


@bp.route("/<int:ticket_id>/status", methods=("POST",))
@login_required
def update_status(ticket_id):
    get_ticket(ticket_id)
    status = request.form.get("status")
    if status not in STATUSES:
        flash("Statut invalide.", "error")
    else:
        db = get_db()
        db.execute("UPDATE tickets SET status = ? WHERE id = ?", (status, ticket_id))
        db.commit()
        flash(f"Statut mis à jour : {status}.", "success")
    return redirect(url_for("tickets.detail", ticket_id=ticket_id))
