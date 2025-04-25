import time
from safrs import SAFRSBase
from app import db

# --------------------- MODELO: MANUFACTURERS ---------------------
class Manufacturer(SAFRSBase, db.Model):
    __tablename__ = "manufacturers"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    contact_person = db.Column(db.String(255))
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    country = db.Column(db.String(100), nullable=False)
    payment_terms = db.Column(db.Text)
    delivery_conditions = db.Column(db.Text)
    created_at = db.Column(db.BigInteger, nullable=False, default=lambda: int(time.time()))
    updated_at = db.Column(db.BigInteger, nullable=False, default=lambda: int(time.time()))

    # Relación 1 a N con productos
    products = db.relationship("Product", back_populates="manufacturer")

