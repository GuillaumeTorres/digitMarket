from utils import db


class Commande(db.Model):
    __tablename__ = "commandes"

    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey("utilisateurs.id"), nullable=False)
    date_commande = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
    )
    adresse_livraison = db.Column(db.String(255), nullable=False)
    statut = db.Column(db.String(255), nullable=False, default="en_attente")

    utilisateur = db.relationship("Utilisateur")
    lignes = db.relationship("LigneCommande", backref="commande")

    def show(self, is_admin=False):
        total = sum(
            ligne.quantite * ligne.prix_unitaire
            for ligne in self.lignes
        )

        data = {
            "id": self.id,
            "date_commande": self.date_commande.isoformat(),
            "adresse_livraison": self.adresse_livraison,
            "statut": self.statut,
            "prix": total,
            "lignes": [ligne.show() for ligne in self.lignes],
        }

        if is_admin:
            data["utilisateur"] = {
                "id": self.utilisateur.id,
                "nom": self.utilisateur.nom,
                "email": self.utilisateur.email,
            }

        return data


class LigneCommande(db.Model):
    __tablename__ = "lignes_commandes"

    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(db.Integer, db.ForeignKey("commandes.id"), nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey("produits.id"), nullable=False)
    quantite = db.Column(
        db.Integer,
        db.CheckConstraint("quantite > 0", name="positive"),
        nullable=False,
    )
    prix_unitaire = db.Column(db.Float, nullable=False)

    produit = db.relationship("Produit")

    def show(self):
        return {
            "id": self.id,
            "produit_id": self.produit_id,
            "nom_produit": self.produit.nom,
            "quantite": self.quantite,
            "prix_unitaire": self.prix_unitaire,
        }
