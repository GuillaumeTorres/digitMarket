from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models.commande import Commande, LigneCommande
from models.produit import Produit
from models.utilisateur import Utilisateur
from utils import db, is_admin, save

order_bp = Blueprint("order", __name__, url_prefix="/api")

@order_bp.route("/commandes", methods=["GET"])
@jwt_required()
def get_order():
    """Lister les commandes du client connecté ou toutes celles de l'admin.
    ---
    tags: [Commandes]
    security: [{Bearer: []}]
    responses:
      200: {description: Liste des commandes, éventuellement vide.}
      401: {description: Token absent ou invalide.}
    """
    admin_status = is_admin() is None
    if admin_status:
        commandes = Commande.query.all()
    else:
        utilisateur_id = get_jwt_identity()
        commandes = Commande.query.filter_by(utilisateur_id=utilisateur_id).all()

    return jsonify([commande.show(is_admin=admin_status) for commande in commandes]), 200

@order_bp.route("/commandes", methods=["POST"])
@jwt_required()
def create_order():
    """Créer une commande avec ses articles.
    ---
    tags: [Commandes]
    security: [{Bearer: []}]
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [adresse_livraison, produits]
          properties:
            adresse_livraison: {type: string}
            produits:
              type: array
              items: {type: object, required: [produit_id, quantite], properties: {produit_id: {type: integer}, quantite: {type: integer}}}
    responses:
      201: {description: Commande créée avec ses articles.}
      400: {description: Adresse ou produits manquants, ou erreur d'enregistrement.}
      404: {description: Produit ou utilisateur introuvable.}
      401: {description: Token absent ou invalide.}
    """
    body = request.get_json()

    adresse_livraison = body.get("adresse_livraison")
    produits = body.get("produits")

    if not all([adresse_livraison, produits]):
        return jsonify({"erreur": "Adresse de livraison et produits obligatoires."}), 400

    # Vérification de l'existence des produits et calcul du prix total
    total_prix = 0
    for produit in produits:
        produit_id = produit.get("produit_id")
        quantite = produit.get("quantite")

        produit = db.session.get(Produit, produit_id)
        if produit is None:
            return jsonify({"erreur": f"Produit avec id {produit_id} introuvable."}), 404

        total_prix += produit.prix * quantite

    utilisateur_id = get_jwt_identity()
    utilisateur = db.session.get(Utilisateur, utilisateur_id)

    if utilisateur is None:
        return jsonify({"erreur": "Utilisateur introuvable."}), 404

    order = Commande(
        utilisateur_id=utilisateur.id,
        adresse_livraison=adresse_livraison,
    )
    db.session.add(order)
    if not save():
        return jsonify({"erreur": "Erreur lors de la création de la commande."}), 400

    order_items = []
    for produit in produits:
        produit_id = produit["produit_id"]
        quantite = produit["quantite"]
        produit = db.session.get(Produit, produit_id)

        order_item = LigneCommande(
            commande_id=order.id,
            produit_id=produit.id,
            quantite=quantite,
            prix_unitaire=produit.prix
        )
        db.session.add(order_item)
        order_items.append(order_item)
        if not save():
            return jsonify({"erreur": "Erreur lors de l'enregisrement des articles de la commande."}), 400

    return jsonify({
        "message": "Commande créée avec succès.",
        "commande": {
            "id": order.id,
            "utilisateur_id": order.utilisateur_id,
            "date_commande": order.date_commande.isoformat(),
            "adresse_livraison": order.adresse_livraison,
            "statut": order.statut,
            "prix": total_prix,
            "produits": [
                {
                    "id": item.id,
                    "commande_id": item.commande_id,
                    "produit_id": item.produit_id,
                    "quantite": item.quantite,
                    "prix_unitaire": item.prix_unitaire
                } for item in order_items
            ]
        }
    }), 201
