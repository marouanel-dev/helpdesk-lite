"""HelpDesk Lite - application de gestion de tickets (Flask)."""
import os

from flask import Flask, redirect, url_for
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

# En-têtes de sécurité HTTP ajoutés à chaque réponse
SECURITY_HEADERS = {
    # Seules les ressources du site lui-même sont autorisées (bloque les scripts injectés)
    "Content-Security-Policy": (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
        "object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
    ),
    "X-Frame-Options": "DENY",                    # anti-clickjacking
    "X-Content-Type-Options": "nosniff",          # pas de devinette du type MIME
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Cross-Origin-Embedder-Policy": "require-corp",
    "Cache-Control": "no-store",                  # pas de données sensibles en cache
}


def add_security_headers(response):
    response.headers.update(SECURITY_HEADERS)
    return response


def index():
    return redirect(url_for("tickets.list_tickets"))


def inject_csrf_form():
    # Formulaire vide qui fournit le jeton anti-CSRF aux templates
    return {"csrf_form": FlaskForm()}


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Les secrets sont lus dans l'environnement, jamais écrits dans le code.
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD"),
        DATABASE=os.path.join(app.instance_path, "helpdesk.db"),
        # Cookie de session : inaccessible au JavaScript, non envoyé par les sites tiers,
        # HTTPS uniquement quand SESSION_COOKIE_SECURE=1 (production derrière TLS)
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE") == "1",
    )
    if test_config:
        app.config.update(test_config)

    if not app.config["SECRET_KEY"]:
        raise RuntimeError("La variable d'environnement SECRET_KEY doit être définie.")

    os.makedirs(app.instance_path, exist_ok=True)

    # Protection CSRF : tout formulaire POST doit contenir un jeton valide
    csrf.init_app(app)
    app.context_processor(inject_csrf_form)
    app.after_request(add_security_headers)

    from . import auth, db, tickets

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(tickets.bp)
    app.add_url_rule("/", "index", index)

    return app
