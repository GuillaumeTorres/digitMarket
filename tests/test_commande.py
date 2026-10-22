import pytest
from flask_jwt_extended import create_access_token

from models.commande import Commande, LigneCommande
from models.produit import Produit
from models.utilisateur import Utilisateur
from utils import db


@pytest.fixture
def create_order(app):
    customer_one = Utilisateur(
        nom="Client 1",
        email="client1@example.com"
    )
    customer_one.hash_mot_de_passe("password")

    customer_two = Utilisateur(
        nom="Client 2",
        email="client2@example.com"
    )
    customer_two.hash_mot_de_passe("password")

    admin = Utilisateur(
        nom="Admin",
        email="admin@example.com",
        role="admin",
    )
    admin.hash_mot_de_passe("password")

    headphones = Produit(
        nom="Casque de test",
        categorie="Son",
        prix=5,
        quantite_stock=10,
    )

    keyboard = Produit(
        nom="Clavier de test",
        categorie="Informatique",
        prix=20,
        quantite_stock=10,
    )

    order_one = Commande(
        utilisateur=customer_one,
        adresse_livraison="Adresse du client 1",
    )
    order_two = Commande(
        utilisateur=customer_one,
        adresse_livraison="Autre adresse du client 1",
    )
    order_three = Commande(
        utilisateur=customer_two,
        adresse_livraison="Adresse du client 2",
    )

    item_one = LigneCommande(
        commande=order_one,
        produit=headphones,
        quantite=2,
        prix_unitaire=5,
    )
    item_two = LigneCommande(
        commande=order_one,
        produit=keyboard,
        quantite=1,
        prix_unitaire=20,
    )
    item_three = LigneCommande(
        commande=order_two,
        produit=headphones,
        quantite=3,
        prix_unitaire=5,
    )

    db.session.add_all([
        customer_one,
        customer_two,
        admin,
        headphones,
        keyboard,
        order_one,
        order_two,
        order_three,
        item_one,
        item_two,
        item_three,
    ])
    db.session.commit()
    return customer_one, headphones, keyboard

def test_create_order(client, create_order):
    customer, headphones, keyboard = create_order
    token = create_access_token(identity=str(customer.id))

    response = client.post(
        "/api/commandes",
        json={
            "adresse_livraison": "123 Rue de Test",
            "produits": [
                {"produit_id": headphones.id, "quantite": 2},
                {"produit_id": keyboard.id, "quantite": 1},
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201

    order = response.json["commande"]
    assert order["utilisateur_id"] == customer.id
    assert order["adresse_livraison"] == "123 Rue de Test"
    assert order["prix"] == 30
    assert len(order["produits"]) == 2


def test_get_orders(client, create_order):
    customer, _, _ = create_order
    admin = Utilisateur.query.filter_by(role="admin").first()

    customer_token = create_access_token(identity=str(customer.id))
    customer_response = client.get(
        "/api/commandes",
        headers={"Authorization": f"Bearer {customer_token}"},
    )

    assert customer_response.status_code == 200
    assert len(customer_response.json) == 2

    admin_token = create_access_token(identity=str(admin.id))
    admin_response = client.get(
        "/api/commandes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert admin_response.status_code == 200
    assert len(admin_response.json) == 3


def test_get_order(client, create_order):
    customer, _, _ = create_order
    order = Commande.query.filter_by(utilisateur_id=customer.id).first()

    token = create_access_token(identity=str(customer.id))
    response = client.get(
        f"/api/commandes/{order.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403

    admin = Utilisateur.query.filter_by(role="admin").first()
    admin_token = create_access_token(identity=str(admin.id))
    response = client.get(
        f"/api/commandes/{order.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert response.json["id"] == order.id
    assert response.json["utilisateur"]["id"] == customer.id


def test_update_order(client, create_order):
    customer, headphones, keyboard = create_order
    admin = Utilisateur.query.filter_by(role="admin").first()
    admin_token = create_access_token(identity=str(admin.id))
    headers = {"Authorization": f"Bearer {admin_token}"}
    customer_token = create_access_token(identity=str(customer.id))
    customer_headers = {"Authorization": f"Bearer {customer_token}"}

    customer_orders = Commande.query.filter_by(
        utilisateur_id=customer.id
    ).order_by(Commande.id).all()
    order_to_ship = customer_orders[0]
    order_to_cancel = customer_orders[1]

    # Un client ne peut pas modifier le statut d'une commande.
    response = client.patch(
        f"/api/commandes/{order_to_ship.id}",
        json={"statut": "validee"},
        headers=customer_headers,
    )
    assert response.status_code == 403

    # La validation échoue sans changer le stock si la quantité manque.
    headphones.quantite_stock = 1
    db.session.commit()
    response = client.patch(
        f"/api/commandes/{order_to_ship.id}",
        json={"statut": "validee"},
        headers=headers,
    )
    assert response.status_code == 409
    db.session.refresh(headphones)
    db.session.refresh(order_to_ship)
    assert headphones.quantite_stock == 1
    assert order_to_ship.statut == "en_attente"

    # On remet le stock initial pour tester une validation réussie.
    headphones.quantite_stock = 10
    db.session.commit()

    # Valider la première commande retire ses articles du stock.
    response = client.patch(
        f"/api/commandes/{order_to_ship.id}",
        json={"statut": "validee"},
        headers=headers,
    )
    assert response.status_code == 200
    db.session.refresh(headphones)
    db.session.refresh(keyboard)
    assert headphones.quantite_stock == 8
    assert keyboard.quantite_stock == 9

    # L'expédition ne doit pas retirer le stock une deuxième fois.
    response = client.patch(
        f"/api/commandes/{order_to_ship.id}",
        json={"statut": "expediee"},
        headers=headers,
    )
    assert response.status_code == 200
    db.session.refresh(headphones)
    db.session.refresh(keyboard)
    assert headphones.quantite_stock == 8
    assert keyboard.quantite_stock == 9

    # Valider puis annuler la deuxième commande remet ses articles en stock.
    response = client.patch(
        f"/api/commandes/{order_to_cancel.id}",
        json={"statut": "validee"},
        headers=headers,
    )
    assert response.status_code == 200
    db.session.refresh(headphones)
    assert headphones.quantite_stock == 5

    response = client.patch(
        f"/api/commandes/{order_to_cancel.id}",
        json={"statut": "annulee"},
        headers=headers,
    )
    assert response.status_code == 200
    db.session.refresh(headphones)
    assert headphones.quantite_stock == 8
