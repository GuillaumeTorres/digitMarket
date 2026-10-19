from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class Utilisateur(db.Model):
    __tablename__ = "utilisateurs"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(255), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="client")
    date_creation = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
    )

    def hash_mot_de_passe(self, password):
        self.mot_de_passe = generate_password_hash(password)

    def check_mot_de_passe(self, password):
        return check_password_hash(self.mot_de_passe, password)
