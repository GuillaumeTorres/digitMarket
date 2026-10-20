from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from extensions import db, save
from models.produit import Produit
from models.utilisateur import Utilisateur

product_bp = Blueprint("product", __name__, url_prefix="/api")

def is_admin():
    user = db.session.get(Utilisateur, get_jwt_identity())
    if user is None or user.role != "admin":
        return jsonify({"erreur": "Accès réservé aux administrateurs."}), 403
    return None


@product_bp.route("/produits", methods=["GET"])
@jwt_required()
def list_products():
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
@jwt_required()
def get_product(product_id):
    product = db.session.get(Produit, product_id)
    if product is None:
        return jsonify({"erreur": "Produit introuvable."}), 404
    return jsonify(product.show()), 200


@product_bp.route("/produits", methods=["POST"])
@jwt_required()
def create_product():
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
