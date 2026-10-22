import os

from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask

from routes.auth import auth_bp
from routes.commande import order_bp
from routes.produit import product_bp
from utils import db, jwt


def create_app(test_config=None):
    load_dotenv()

    app = Flask(__name__)

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI="sqlite:///digimarket.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY"),
    )

    # Les tests peuvent fournir leurs propres réglages, dont une base séparée.
    if test_config is not None:
        app.config.update(test_config)

    if not app.config["JWT_SECRET_KEY"]:
        raise RuntimeError("La variable JWT_SECRET_KEY est manquante.")

    db.init_app(app)
    jwt.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(order_bp)

    # Flasgger lit les spécifications YAML écrites dans les docstrings
    # des routes et fournit l'interface interactive sur /apidocs/.
    swagger_template = {
        "info": {
            "title": "DigitMarket API",
            "description": "Documentation de l'API du catalogue DigitMarket.",
            "version": "1.0.0",
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Saisir le token sous la forme : Bearer <token>",
            }
        },
    }
    Swagger(app, template=swagger_template)

    return app

app = create_app()

if __name__ == "__main__":
    # La base est initialisée au démarrage normal de l'application.
    # Les tests créent leurs tables dans leur propre base temporaire.
    with app.app_context():
        db.create_all()
    app.run(debug=True)
