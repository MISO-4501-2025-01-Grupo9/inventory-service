import time
from safrs import SAFRSBase
from app import db

# --------------------- MODELO: PRODUCT_IMAGES --------------------------
class ProductImage(SAFRSBase, db.Model):
    __tablename__ = "product_images"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    is_primary = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.BigInteger, nullable=False, default=lambda: int(time.time()))

    product = db.relationship("Product", back_populates="images")
