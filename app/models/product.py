import time
import json
from safrs import SAFRSBase, jsonapi_rpc
from app import db
from sqlalchemy import func
from app.models.inventory_item import InventoryItem
from sqlalchemy import or_, and_

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
    items = db.relationship("InventoryItem", back_populates="user", lazy="dynamic")

    def to_dict(self):
        result = super().to_dict()
        # Calculate total quantity of items
        total_quantity = db.session.query(func.sum(InventoryItem.quantity)).filter(
            InventoryItem.product_id == self.id
        ).scalar() or 0
        result['total_quantity'] = total_quantity
        return result

    @classmethod
    @jsonapi_rpc(http_methods=['GET'])
    def search_by_name(cls, name):
        """
        description: Search products by partial name match
        args:
            name:
                type: string
                description: The name or part of the name to search for
                example: "Kit"
                required: true
        """
        return cls.query.filter(cls.name.ilike(f'%{name}%')).all()

    @classmethod
    @jsonapi_rpc(http_methods=['GET'])
    def search_by_name_with_stock(cls, name, min_stock=0):
        """
        description: Search products by partial name match and minimum stock level
        """
        # Subquery to get total quantity for each product
        total_quantity = db.session.query(
            InventoryItem.product_id,
            func.sum(InventoryItem.quantity).label('total')
        ).group_by(InventoryItem.product_id).subquery()

        # Join with the subquery and filter by name and stock
        query = cls.query.outerjoin(
            total_quantity,
            cls.id == total_quantity.c.product_id
        ).filter(
            cls.name.ilike(f'%{name}%'),
            or_(
                total_quantity.c.total >= min_stock,
                total_quantity.c.total == None  # Include products with no stock if min_stock is 0
            )
        )

        return query.all()

