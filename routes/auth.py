from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from utils import db, save
from models.utilisateur import Utilisateur

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Créer un compte client.
    ---
    tags:
      - Authentification
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - nom
            - email
            - mot_de_passe
          properties:
            nom:
              type: string
            email:
              type: string
              format: email
            mot_de_passe:
              type: string
              format: password
    responses:
      201:
        description: JSON contenant un message et les informations du compte.
      400:
        description: Données manquantes ou invalides.
      409:
        description: L'email est déjà utilisé ou le compte n'a pas pu être créé.
    """
    body = request.get_json()

    email = body.get("email")
    password = body.get("mot_de_passe")
    name = body.get("nom")

    if not all([name, email, password]):
        return jsonify({
            "erreur": "Nom, email et mot de passe obligatoires."
        }), 400

    values_are_strings = all(
        isinstance(value, str) for value in [name, email, password]
    )
    if not values_are_strings:
        return jsonify({"erreur": "Format des données invalide."}), 400

    name = name.strip()
    email = email.strip().lower()

    if not name or not email or "@" not in email:
        return jsonify({"erreur": "Nom ou email invalide."}), 400

    if len(password) < 8:
        return jsonify({
            "erreur": "Le mot de passe doit contenir au moins 8 caractères."
        }), 400

    existing_user = db.session.scalar(
        db.select(Utilisateur).where(Utilisateur.email == email)
    )
    if existing_user:
        return jsonify({"erreur": "Cet email est déjà utilisé."}), 409

    user = Utilisateur(nom=name, email=email, role="client")
    user.hash_mot_de_passe(password)
    db.session.add(user)

    if not save():
        return jsonify({"erreur": "Le compte n'a pas pu être créé."}), 409

    return jsonify({
        "message": "Compte créé avec succès.",
        "utilisateur": {
            "id": user.id,
            "nom": user.nom,
            "email": user.email,
            "role": user.role,
            "date_creation": user.date_creation.isoformat(),
        },
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Se connecter et obtenir un token d'accès.
    ---
    tags:
      - Authentification
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - mot_de_passe
          properties:
            email:
              type: string
              format: email
            mot_de_passe:
              type: string
              format: password
    responses:
      200:
        description: JSON contenant un message, un token et l'utilisateur.
      400:
        description: Email ou mot de passe manquant ou invalide.
      401:
        description: Email ou mot de passe incorrect.
    """
    body = request.get_json()

    email = body.get("email")
    password = body.get("mot_de_passe")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({"erreur": "Email et mot de passe obligatoires."}), 400

    email = email.strip().lower()
    user = db.session.scalar(
        db.select(Utilisateur).where(Utilisateur.email == email)
    )

    if user is None or not user.check_mot_de_passe(password):
        return jsonify({"erreur": "Email ou mot de passe incorrect."}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role},
    )

    return jsonify({
        "message": "Connexion réussie.",
        "access_token": access_token,
        "utilisateur": {
            "id": user.id,
            "nom": user.nom,
            "email": user.email,
            "role": user.role,
        },
    }), 200
