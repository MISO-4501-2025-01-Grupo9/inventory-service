from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from safrs import SAFRSAPI
from config import Config
from .controllers.api import api_bp
from .models import Product


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(api_bp, url_prefix="/api")
    db.init_app(app)

    with app.app_context():
        from .models import Warehouse, InventoryItem, InventoryTransaction
        db.create_all()

        api = SAFRSAPI(app, host=Config.HOST, port=Config.PORT, prefix="/api")

        # Exponer modelos con métodos CRUD
        api.expose_object(Warehouse, methods=["GET", "POST", "PATCH", "DELETE"])
        api.expose_object(InventoryItem, methods=["GET", "POST", "PATCH", "DELETE"])
        api.expose_object(InventoryTransaction, methods=["GET", "POST", "PATCH", "DELETE"])
        api.expose_object(Product, methods=["GET", "POST", "PATCH", "DELETE"])
    return app
