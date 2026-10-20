import os

from dotenv import load_dotenv
from flask import Flask

from extensions import db, jwt
from models.produit import Produit
from models.utilisateur import Utilisateur
from routes.auth import auth_bp
from routes.produit import product_bp


def create_app(test_config=None):
    """Crée l'application Flask et permet de remplacer sa configuration."""
    load_dotenv()

    app = Flask(__name__)

    # Ces valeurs sont utilisées par l'application quand on la lance normalement.
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

    return app


# Cette variable conserve la façon habituelle de démarrer l'application
# avec « python app.py » et reste disponible aux outils qui importent app.
app = create_app()


if __name__ == "__main__":
    # La base est initialisée au démarrage normal de l'application.
    # Les tests, eux, créent leurs tables dans leur propre base temporaire.
    with app.app_context():
        db.create_all()
    app.run(debug=True)
