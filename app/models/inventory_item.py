import time
from safrs import SAFRSBase
from app import db

# --------------------- MODELO: INVENTORY_ITEMS ---------------------
class InventoryItem(SAFRSBase, db.Model):
    __tablename__ = "inventory_items"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouses.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100))
    expiry_date = db.Column(db.BigInteger)
    created_at = db.Column(db.BigInteger, nullable=False, default=lambda: int(time.time()))
    updated_at = db.Column(db.BigInteger, nullable=False, default=lambda: int(time.time()))

    warehouse = db.relationship("Warehouse", back_populates="inventory_items", lazy="joined")
    # Relación uno a muchos con transactions
    transactions = db.relationship("InventoryTransaction", back_populates="inventory_item",
                                   cascade="all, delete-orphan", lazy="joined")
    user = db.relationship("Product", back_populates="items")
