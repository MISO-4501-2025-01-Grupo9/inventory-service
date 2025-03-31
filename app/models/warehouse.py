import time
from safrs import SAFRSBase
from app import db

# --------------------- MODELO: WAREHOUSES ---------------------
class Warehouse(SAFRSBase, db.Model):
    __tablename__ = "warehouses"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.BigInteger, nullable=False, default=lambda: int(time.time()))
    updated_at = db.Column(db.BigInteger, nullable=False, default=lambda: int(time.time()))

    # Relación uno a muchos con inventory_items
    inventory_items = db.relationship("InventoryItem", back_populates="warehouse", cascade="all, delete-orphan")
