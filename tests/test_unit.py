from datetime import datetime

from models.produit import Produit


def test_show():
    created_at = datetime(2026, 10, 20, 9, 24, 6)
    product = Produit(
        id=1,
        nom="Clavier",
        description="Clavier mécanique",
        categorie="Informatique",
        prix=49.99,
        quantite_stock=10,
        date_creation=created_at,
    )

    result = product.show()

    assert result == {
        "id": 1,
        "nom": "Clavier",
        "description": "Clavier mécanique",
        "categorie": "Informatique",
        "prix": 49.99,
        "quantite_stock": 10,
        "date_creation": "2026-10-20T09:24:06",
    }
