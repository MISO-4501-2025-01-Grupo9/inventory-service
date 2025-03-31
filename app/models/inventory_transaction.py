import time
from safrs import SAFRSBase
from app import db

# --------------------- MODELO: INVENTORY_TRANSACTIONS ---------------------
class InventoryTransaction(SAFRSBase, db.Model):
    __tablename__ = "inventory_transactions"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    from_warehouse_id = db.Column(db.Integer)  # opcional: referencia a warehouses.id si aplica
    to_warehouse_id = db.Column(db.Integer)  # opcional: referencia a warehouses.id si aplica
    transaction_date = db.Column(db.BigInteger, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)  # Se asume que referencia a la tabla users en otro servicio
    notes = db.Column(db.Text)

    inventory_item = db.relationship("InventoryItem", back_populates="transactions")
