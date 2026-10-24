from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from models.produit import Produit
from utils import db, is_admin, save

product_bp = Blueprint("product", __name__, url_prefix="/api")


@product_bp.route("/produits", methods=["GET"])
def list_products():
    """Lister les produits avec ou sans filtres.
    ---
    tags:
      - Produits
    parameters:
      - name: nom
        in: query
        type: string
        description: Recherche partielle dans le nom.
      - name: categorie
        in: query
        type: string
        description: Correspondance exacte sans distinction de casse.
    responses:
      200:
        description: Liste JSON des produits correspondants.
    """
    name = request.args.get("nom")
    category = request.args.get("categorie")

    query = Produit.query

    if name:
        query = query.filter(Produit.nom.ilike(f"%{name}%"))

    if category:
        query = query.filter(Produit.categorie.ilike(category))

    products = query.all()
    return jsonify([product.show() for product in products]), 200


@product_bp.route("/produits/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Afficher un produit par son identifiant.
    ---
    tags:
      - Produits
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Objet JSON du produit trouvé.
      404:
        description: Produit introuvable.
    """
    product = db.session.get(Produit, product_id)
    if product is None:
        return jsonify({"erreur": "Produit introuvable."}), 404
    return jsonify(product.show()), 200


@product_bp.route("/produits", methods=["POST"])
@jwt_required()
def create_product():
    """Créer un produit (administrateurs uniquement).
    ---
    tags:
      - Produits
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - nom
            - categorie
            - prix
            - quantite_stock
          properties:
            nom:
              type: string
            description:
              type: string
            categorie:
              type: string
            prix:
              type: number
            quantite_stock:
              type: integer
    responses:
      201:
        description: JSON contenant un message et le produit créé.
      400:
        description: Données invalides ou échec de création.
      401:
        description: Token absent ou invalide.
      403:
        description: Accès réservé aux administrateurs.
    """
    access_error = is_admin()
    if access_error:
        return access_error

    body = request.get_json()

    name = body.get("nom")
    description = body.get("description")
    category = body.get("categorie")
    price = body.get("prix")
    stock_quantity = body.get("quantite_stock")

    if not name or not category or price is None or stock_quantity is None:
        return jsonify({
            "erreur": (
                "Nom, catégorie, prix et quantité en stock sont obligatoires."
            )
        }), 400

    product = Produit(
        nom=name,
        description=description,
        categorie=category,
        prix=price,
        quantite_stock=stock_quantity,
    )

    db.session.add(product)
    if not save():
        return jsonify({"erreur": "Le produit n'a pas pu être créé."}), 400

    return jsonify({
        "message": "Produit créé avec succès.",
        "produit": product.show(),
    }), 201


@product_bp.route("/produits/<int:product_id>", methods=["PATCH"])
@jwt_required()
def update_product(product_id):
    """Modifier un produit (administrateurs uniquement).
    ---
    tags:
      - Produits
    security:
      - Bearer: []
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            nom:
              type: string
            description:
              type: string
            categorie:
              type: string
            prix:
              type: number
            quantite_stock:
              type: integer
    responses:
      200:
        description: JSON contenant un message et le produit modifié.
      400:
        description: Produit non modifié.
      401:
        description: Token absent ou invalide.
      403:
        description: Accès réservé aux administrateurs.
      404:
        description: Produit introuvable.
    """
    access_error = is_admin()
    if access_error:
        return access_error

    product = db.session.get(Produit, product_id)
    if product is None:
        return jsonify({"erreur": "Produit introuvable."}), 404

    body = request.get_json()

    fields = ["nom", "description", "categorie", "prix", "quantite_stock"]

    for field in fields:
        if field in body:
            setattr(product, field, body.get(field))

    if not save():
        return jsonify({"erreur": "Le produit n'a pas pu être modifié."}), 400

    return jsonify({
        "message": "Produit modifié avec succès.",
        "produit": product.show(),
    }), 200


@product_bp.route("/produits/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    """Supprimer un produit (administrateurs uniquement).
    ---
    tags:
      - Produits
    security:
      - Bearer: []
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: JSON contenant un message de confirmation.
      401:
        description: Token absent ou invalide.
      403:
        description: Accès réservé aux administrateurs.
      404:
        description: Produit introuvable.
    """
    access_error = is_admin()
    if access_error:
        return access_error

    product = db.session.get(Produit, product_id)
    if product is None:
        return jsonify({"erreur": "Produit introuvable."}), 404

    db.session.delete(product)
    if not save():
        return jsonify({"erreur": "Le produit n'a pas pu être supprimé."}), 400

    return jsonify({"message": "Produit supprimé avec succès."}), 200
