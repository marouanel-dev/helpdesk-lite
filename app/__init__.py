"""HelpDesk Lite - application de gestion de tickets (Flask)."""
import os

from flask import Flask, redirect, url_for


def index():
    return redirect(url_for("tickets.list_tickets"))


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Les secrets sont lus dans l'environnement, jamais écrits dans le code.
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD"),
        DATABASE=os.path.join(app.instance_path, "helpdesk.db"),
    )
    if test_config:
        app.config.update(test_config)

    if not app.config["SECRET_KEY"]:
        raise RuntimeError("La variable d'environnement SECRET_KEY doit être définie.")

    os.makedirs(app.instance_path, exist_ok=True)

    from . import auth, db, tickets

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(tickets.bp)
    app.add_url_rule("/", "index", index)

    return app
