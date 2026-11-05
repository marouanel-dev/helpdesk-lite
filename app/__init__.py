"""HelpDesk Lite - application de gestion de tickets (Flask)."""
import os

from flask import Flask, redirect, url_for


def index():
    return redirect(url_for("tickets.list_tickets"))


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="7c1e9b4a2f8d6035e4b7a9c2d1f0e83b5a6c4d2e9f1b7a3c8d0e5f2a4b6c9d1e",
        DATABASE=os.path.join(app.instance_path, "helpdesk.db"),
    )
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    from . import auth, db, tickets

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(tickets.bp)
    app.add_url_rule("/", "index", index)

    return app
