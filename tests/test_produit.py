import pytest
from flask_jwt_extended import create_access_token

from models.produit import Produit
from models.utilisateur import Utilisateur
from utils import db


@pytest.fixture
def create_products(app):
    db.session.add_all([
        Produit(
            nom="Clavier",
            description="Clavier de test",
            categorie="Informatique",
            prix=49.99,
            quantite_stock=10,
        ),
        Produit(
            nom="Souris",
            description="Souris de test",
            categorie="Informatique",
            prix=19.99,
            quantite_stock=5,
        ),
        Produit(
            nom="Ecouteurs",
            description="Ecouteurs de test",
            categorie="Son",
            prix=99,
            quantite_stock=20,
        ),
    ])
    db.session.commit()


@pytest.fixture
def token_client(app):
    client = Utilisateur(
        nom="Client",
        email="client@example.com",
        role="client",
    )
    client.hash_mot_de_passe("password")
    db.session.add(client)
    db.session.commit()

    return create_access_token(identity=str(client.id))


@pytest.fixture
def token_admin(app):
    admin = Utilisateur(
        nom="Admin",
        email="admin@example.com",
        role="admin",
    )
    admin.hash_mot_de_passe("password")
    db.session.add(admin)
    db.session.commit()

    return create_access_token(identity=str(admin.id))


def test_list_products(client, create_products):
    response = client.get("/api/produits")
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 3

    response = client.get("/api/produits?nom=clav")
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["nom"] == "Clavier"

    response = client.get(
        "/api/produits?categorie=informatique")
    assert response.status_code == 200
    assert len(response.json) == 2
    assert all(
        product["categorie"] == "Informatique"
        for product in response.json
    )

    response = client.get(
        "/api/produits?nom=clav&categorie=informatique")
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["nom"] == "Clavier"
    assert response.json[0]["categorie"] == "Informatique"


def test_get_product(client, create_products):
    response = client.get("/api/produits/1")
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert response.json["nom"] == "Clavier"
    assert response.json["description"] == "Clavier de test"
    assert response.json["categorie"] == "Informatique"
    assert response.json["prix"] == 49.99
    assert response.json["quantite_stock"] == 10


def test_create_product(client, token_admin, token_client):
    client_response = client.post(
        "/api/produits",
        headers={"Authorization": f"Bearer {token_client}"},
    )
    assert client_response.status_code == 403

    headers = {"Authorization": f"Bearer {token_admin}"}
    response = client.post(
        "/api/produits",
        headers=headers,
        json={
            "nom": "Casque",
            "description": "Casque de test",
            "categorie": "Son",
            "prix": 79.99,
            "quantite_stock": 15,
        }
    )
    assert response.status_code == 201
    assert isinstance(response.json, dict)
    assert response.json["produit"]["nom"] == "Casque"
    assert response.json["produit"]["description"] == "Casque de test"
    assert response.json["produit"]["categorie"] == "Son"
    assert response.json["produit"]["prix"] == 79.99
    assert response.json["produit"]["quantite_stock"] == 15


def test_update_product(client, create_products, token_admin, token_client):
    client_response = client.post(
        "/api/produits",
        headers={"Authorization": f"Bearer {token_client}"},
    )
    assert client_response.status_code == 403

    headers = {"Authorization": f"Bearer {token_admin}"}
    response = client.patch(
        "/api/produits/1",
        headers=headers,
        json={
            "prix": 30,
            "quantite_stock": 8,
        },
    )
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert response.json["produit"]["id"] == 1
    assert response.json["produit"]["prix"] == 30
    assert response.json["produit"]["quantite_stock"] == 8
    assert response.json["produit"]["nom"] == "Clavier"


def test_delete_product(client, create_products, token_admin, token_client):
    client_response = client.post(
        "/api/produits",
        headers={"Authorization": f"Bearer {token_client}"},
    )
    assert client_response.status_code == 403

    headers = {"Authorization": f"Bearer {token_admin}"}
    delete_response = client.delete("/api/produits/1", headers=headers)
    assert delete_response.status_code == 200

    get_response = client.get("/api/produits/1", headers=headers)
    assert get_response.status_code == 404
