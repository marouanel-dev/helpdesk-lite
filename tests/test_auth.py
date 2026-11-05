from tests.conftest import ADMIN_PASSWORD


def test_login_page_is_displayed(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert "Se connecter" in response.text


def test_protected_page_redirects_to_login(client):
    response = client.get("/tickets/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_login_with_valid_credentials(client):
    response = client.post(
        "/login", data={"username": "admin", "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 302
    assert client.get("/tickets/").status_code == 200


def test_login_with_wrong_password(client):
    response = client.post(
        "/login", data={"username": "admin", "password": "mauvais"}
    )
    assert response.status_code == 200
    assert "Identifiants invalides" in response.text


def test_logout(auth_client):
    auth_client.get("/logout")
    response = auth_client.get("/tickets/")
    assert response.status_code == 302
