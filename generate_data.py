"""Créer quelques données de démonstration dans la base digiMarket."""

from app import app
from models.commande import Commande, LigneCommande
from models.produit import Produit
from models.utilisateur import Utilisateur
from utils import db


def generate_data():
    with app.app_context():
        db.create_all()

        # Ne pas ajouter de doublons ni modifier une base déjà utilisée.
        existing_user = db.session.scalar(db.select(Utilisateur.id).limit(1))
        existing_product = db.session.scalar(db.select(Produit.id).limit(1))

        if existing_user is not None or existing_product is not None:
            print("La base contient déjà des données. Aucune donnée ajoutée.")
            return

        admin = Utilisateur(
            nom="Admin",
            email="admin@digimarket.test",
            role="admin",
        )
        admin.hash_mot_de_passe("admin_password")

        customer = Utilisateur(
            nom="Jean",
            email="jean@digimarket.test",
        )
        customer.hash_mot_de_passe("client_password")

        second_customer = Utilisateur(
            nom="Marie",
            email="marie@digimarket.test",
        )
        second_customer.hash_mot_de_passe("client2_password")

        headphones = Produit(
            nom="Casque de démonstration",
            description="Un casque audio pour tester le catalogue.",
            categorie="Son",
            prix=49.99,
            quantite_stock=10,
        )
        keyboard = Produit(
            nom="Clavier de démonstration",
            description="Un clavier pour tester les commandes.",
            categorie="Informatique",
            prix=79.99,
            quantite_stock=5,
        )
        mouse = Produit(
            nom="Souris de démonstration",
            description="Une souris pour tester les filtres.",
            categorie="Informatique",
            prix=24.99,
            quantite_stock=12,
        )

        first_order = Commande(
            utilisateur=customer,
            adresse_livraison="1 rue de Démonstration, Paris",
        )
        second_order = Commande(
            utilisateur=customer,
            adresse_livraison="1 rue de Démonstration, Paris",
        )
        third_order = Commande(
            utilisateur=second_customer,
            adresse_livraison="23 rue de Démonstration, Lyon",
        )

        order_items = [
            LigneCommande(
                commande=first_order,
                produit=headphones,
                quantite=1,
                prix_unitaire=headphones.prix,
            ),
            LigneCommande(
                commande=first_order,
                produit=keyboard,
                quantite=1,
                prix_unitaire=keyboard.prix,
            ),
            LigneCommande(
                commande=second_order,
                produit=mouse,
                quantite=2,
                prix_unitaire=mouse.prix,
            ),
            LigneCommande(
                commande=third_order,
                produit=headphones,
                quantite=1,
                prix_unitaire=headphones.prix,
            ),
        ]

        db.session.add_all([
            admin,
            customer,
            second_customer,
            headphones,
            keyboard,
            mouse,
            first_order,
            second_order,
            third_order,
            *order_items,
        ])
        db.session.commit()

        print("Données de démonstration ajoutées.")
        print("Admin : admin@digimarket.test / admin_password")
        print("Client Jean : jean@digimarket.test / client_password")
        print("Client Marie : marie@digimarket.test / client2_password")


if __name__ == "__main__":
    generate_data()
