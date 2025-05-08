import time
from safrs import SAFRSBase
from app import db

# --------------------- MODELO: PRODUCTS --------------------------
class Product(SAFRSBase, db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey("manufacturers.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    sku = db.Column(db.String(100), unique=True, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    storage_conditions = db.Column(db.Text)
    delivery_time = db.Column(db.Integer)
    created_at = db.Column(db.BigInteger, nullable=False, default=lambda: int(time.time()))
    updated_at = db.Column(db.BigInteger, nullable=False, default=lambda: int(time.time()))

    manufacturer = db.relationship("Manufacturer", back_populates="products")
    images = db.relationship("ProductImage", back_populates="product")
    regulations = db.relationship("ProductCountryRegulation", back_populates="product")


