"""Tests de sécurité : ils échouent tant que les failles ne sont pas corrigées."""
import hashlib

import pytest

from app import create_app
from app.db import get_db


def test_app_refuses_to_start_without_secret_key(tmp_path, monkeypatch):
    """Secret : la clé de session doit venir de l'environnement, pas du code."""
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError):
        create_app({"TESTING": True, "DATABASE": str(tmp_path / "t.db")})


def test_sql_injection_cannot_bypass_login(client):
    """Injection SQL : « admin' -- » ne doit pas permettre de se connecter."""
    client.post("/login", data={"username": "admin' --", "password": "peu-importe"})
    response = client.get("/tickets/")
    assert response.status_code == 302, "Connexion obtenue par injection SQL"


def test_passwords_are_not_stored_with_md5(app):
    """Stockage des mots de passe : pas de MD5, un hachage lent et salé."""
    with app.app_context():
        stored = get_db().execute(
            "SELECT password FROM users WHERE username = 'admin'"
        ).fetchone()[0]
    assert stored != hashlib.md5(b"admin123").hexdigest()
    assert stored.startswith(("scrypt:", "pbkdf2:"))


def test_ticket_description_is_escaped(auth_client):
    """XSS stockée : le HTML saisi dans un ticket ne doit jamais être exécuté."""
    payload = "<script>alert('XSS')</script>"
    response = auth_client.post(
        "/tickets/new",
        data={"title": "Test XSS", "description": payload, "priority": "Basse"},
        follow_redirects=True,
    )
    assert payload not in response.text
    assert "&lt;script&gt;" in response.text


def test_forms_require_csrf_token(tmp_path, monkeypatch):
    """CSRF : un formulaire envoyé sans jeton anti-CSRF doit être refusé."""
    monkeypatch.setenv("SECRET_KEY", "cle-de-test-uniquement")
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "t.db")})
    response = app.test_client().post(
        "/login", data={"username": "admin", "password": "peu-importe"}
    )
    assert response.status_code == 400
