from flask import Flask
from safrs import SAFRSAPI
from config import Config
from .database import db
from .controllers.api import api_bp
from .models import Manufacturer, ProductImage, ProductCountryRegulation
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(api_bp, url_prefix="/api")
    db.init_app(app)
    CORS(app)

    with app.app_context():
        from .models import Warehouse, InventoryItem, InventoryTransaction, Product
        db.create_all()

        api = SAFRSAPI(app,
                      host=Config.HOST_SWAGGER,
                      port=Config.PORT_SWAGGER,
                      prefix="/api")

        # Exponer modelos con métodos CRUD
        api.expose_object(Warehouse, methods=["GET", "POST", "PATCH", "DELETE"])
        api.expose_object(InventoryItem, methods=["GET", "POST", "PATCH", "DELETE"])
        api.expose_object(InventoryTransaction, methods=["GET", "POST", "PATCH", "DELETE"])
        api.expose_object(Product, methods=["GET", "POST", "PATCH", "DELETE"])
        api.expose_object(Manufacturer, methods=["GET", "POST", "PATCH", "DELETE"])
        api.expose_object(ProductImage, methods=["GET", "POST", "PATCH", "DELETE"])
        api.expose_object(ProductCountryRegulation, methods=["GET", "POST", "PATCH", "DELETE"])

    # Registrar blueprints
    from app.routes.pubsub import pubsub_bp
    from app.routes.inventory import inventory_bp
    app.register_blueprint(pubsub_bp, url_prefix='/api/pubsub')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')

    return app
