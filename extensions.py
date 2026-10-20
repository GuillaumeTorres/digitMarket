from flask_jwt_extended import JWTManager
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
