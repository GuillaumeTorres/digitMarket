from flask import jsonify
from flask_jwt_extended import JWTManager, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

db = SQLAlchemy()
jwt = JWTManager()


def save():
    try:
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False


def is_admin():
    from models.utilisateur import Utilisateur

    user = db.session.get(Utilisateur, get_jwt_identity())
    if user is None or user.role != "admin":
        return jsonify({"erreur": "Accès réservé aux administrateurs."}), 403
    return None
