import pytest

from app import create_app

ADMIN_PASSWORD = "admin123"


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "cle-de-test-uniquement")
    monkeypatch.setenv("ADMIN_PASSWORD", ADMIN_PASSWORD)
    app = create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "test.db"),
            "WTF_CSRF_ENABLED": False,
        }
    )
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    response = client.post(
        "/login", data={"username": "admin", "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 302
    return client
