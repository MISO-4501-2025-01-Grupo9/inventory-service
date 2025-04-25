import time
from safrs import SAFRSBase
from app import db

# --------------------- MODELO: PRODUCT_COUNTRY_REGULATIONS --------------------------
class ProductCountryRegulation(SAFRSBase, db.Model):
    __tablename__ = "product_country_regulations"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    tax_rate = db.Column(db.Numeric(5, 2), nullable=False)
    legal_restrictions = db.Column(db.Text)
    created_at = db.Column(db.BigInteger, nullable=False, default=lambda: int(time.time()))
    updated_at = db.Column(db.BigInteger, nullable=False, default=lambda: int(time.time()))

    product = db.relationship("Product", back_populates="regulations")
