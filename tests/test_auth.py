
def test_register(client):
    response = client.post(
        "/api/auth/register",
        json={
            "nom": "Test",
            "email": "test@example.com",
            "mot_de_passe": "motdepasse123",
        },
    )

    assert response.status_code == 201
    assert response.json["utilisateur"]["nom"] == "Test"
    assert response.json["utilisateur"]["role"] == "client"

def test_login(client):
    client.post(
        "/api/auth/register",
        json={
            "nom": "Test",
            "email": "test@example.com",
            "mot_de_passe": "motdepasse123",
        },
    )

    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "mot_de_passe": "motdepasse123",
        },
    )

    assert response.status_code == 200
    assert response.json["access_token"]
    assert response.json["utilisateur"]["nom"] == "Test"
