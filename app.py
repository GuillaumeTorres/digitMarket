import os

from dotenv import load_dotenv
from flask import Flask

from extensions import db, jwt
from models.utilisateur import Utilisateur
from routes.auth import auth_bp


load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///digimarket.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")

if not app.config["JWT_SECRET_KEY"]:
    raise RuntimeError("La variable JWT_SECRET_KEY est manquante.")

db.init_app(app)
jwt.init_app(app)
app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
