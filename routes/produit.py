from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import db
from models.produit import Produit


product_bp = Blueprint("product", __name__, url_prefix="/api")


@product_bp.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "API Product fonctionne correctement."}), 200


@product_bp.route("/produits", methods=["GET"])
@jwt_required()
def produits():
    products = Produit.query.all()
    return jsonify([product.to_dict() for product in products]), 200


@product_bp.route("/produits", methods=["POST"])
def create_product():
    body = request.get_json()

    name = body.get("nom")
    description = body.get("description")
    category = body.get("categorie")
    price = body.get("prix")
    stock_quantity = body.get("quantite_stock")

    if not all([name, category, price, stock_quantity]):
        return jsonify({
            "erreur": (
                "Nom, catégorie, prix et quantité en stock sont obligatoires."
            )
        }), 400

    values_have_valid_types = (
        isinstance(name, str)
        and isinstance(category, str)
        and isinstance(price, (int, float))
        and isinstance(stock_quantity, int)
    )
    if not values_have_valid_types:
        return jsonify({"erreur": "Format des données invalide."}), 400

    product = Produit(
        nom=name.strip(),
        description=description.strip() if description else None,
        categorie=category.strip(),
        prix=price,
        quantite_stock=stock_quantity,
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({
        "message": "Produit créé avec succès.",
        "produit": product.to_dict(),
    }), 201
