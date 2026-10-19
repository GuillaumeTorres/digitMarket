from extensions import db


class Produit(db.Model):
    __tablename__ = "produits"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text)
    categorie = db.Column(db.String(255), nullable=False)
    prix = db.Column(db.Float, nullable=False)
    quantite_stock = db.Column(db.Integer, nullable=False)
    date_creation = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
    )
