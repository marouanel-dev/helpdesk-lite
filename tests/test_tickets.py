def create_ticket(client, title="Imprimante HS", description="Bourrage papier", priority="Haute"):
    return client.post(
        "/tickets/new",
        data={"title": title, "description": description, "priority": priority},
        follow_redirects=True,
    )


def test_empty_ticket_list(auth_client):
    response = auth_client.get("/tickets/")
    assert response.status_code == 200
    assert "Aucun ticket" in response.text


def test_create_ticket(auth_client):
    response = create_ticket(auth_client)
    assert response.status_code == 200
    assert "Ticket créé" in response.text
    assert "Imprimante HS" in response.text
    assert "Imprimante HS" in auth_client.get("/tickets/").text


def test_create_ticket_requires_title(auth_client):
    response = create_ticket(auth_client, title="")
    assert "obligatoires" in response.text


def test_create_ticket_rejects_unknown_priority(auth_client):
    response = create_ticket(auth_client, priority="Urgente")
    assert "Priorité invalide" in response.text


def test_update_status(auth_client):
    create_ticket(auth_client)
    response = auth_client.post(
        "/tickets/1/status", data={"status": "Résolu"}, follow_redirects=True
    )
    assert "Statut mis à jour" in response.text


def test_filter_by_status(auth_client):
    create_ticket(auth_client, title="Ticket A")
    create_ticket(auth_client, title="Ticket B")
    auth_client.post("/tickets/2/status", data={"status": "En cours"})

    response = auth_client.get("/tickets/?status=En cours")
    assert "Ticket B" in response.text
    assert "Ticket A" not in response.text


def test_unknown_ticket_returns_404(auth_client):
    assert auth_client.get("/tickets/999").status_code == 404
