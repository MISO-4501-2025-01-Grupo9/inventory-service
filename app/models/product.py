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
    def lookup(cls, **kwargs):
        """
        Custom lookup method for SAFRS
        """
        query = cls.query
        if 'name' in kwargs:
            query = query.filter(cls.name.ilike(f'%{kwargs["name"]}%'))
        if 'description' in kwargs:
            query = query.filter(cls.description.ilike(f'%{kwargs["description"]}%'))
        return query.all()

    @classmethod
    def _s_filter(cls, args, query):
        """
        Custom filter method for SAFRS
        """
        if args:
            filters = []
            try:
                # Try to parse as JSON first
                if isinstance(args, str):
                    filter_list = json.loads(args)
                    for filter_item in filter_list:
                        name = filter_item.get('name')
                        op = filter_item.get('op')
                        val = filter_item.get('val')

                        if name == 'name' and op == 'like':
                            filters.append(cls.name.ilike(f'%{val}%'))
                        elif name == 'description' and op == 'like':
                            filters.append(cls.description.ilike(f'%{val}%'))
                        elif op == 'gt':
                            filters.append(getattr(cls, name) > val)
                        elif op == 'lt':
                            filters.append(getattr(cls, name) < val)
                        elif op == 'gte':
                            filters.append(getattr(cls, name) >= val)
                        elif op == 'lte':
                            filters.append(getattr(cls, name) <= val)
                        else:
                            filters.append(getattr(cls, name) == val)
            except (json.JSONDecodeError, TypeError):
                # If not JSON, handle as direct key-value pairs
                for key, value in args.items():
                    if isinstance(value, dict):
                        # Handle operators in direct format
                        for op, val in value.items():
                            if key == 'name' and op == 'like':
                                filters.append(cls.name.ilike(f'%{val}%'))
                            elif key == 'description' and op == 'like':
                                filters.append(cls.description.ilike(f'%{val}%'))
                            elif op == 'gt':
                                filters.append(getattr(cls, key) > val)
                            elif op == 'lt':
                                filters.append(getattr(cls, key) < val)
                            elif op == 'gte':
                                filters.append(getattr(cls, key) >= val)
                            elif op == 'lte':
                                filters.append(getattr(cls, key) <= val)
                    else:
                        # Direct value comparison
                        if key == 'name':
                            filters.append(cls.name.ilike(f'%{value}%'))
                        elif key == 'description':
                            filters.append(cls.description.ilike(f'%{value}%'))
                        else:
                            filters.append(getattr(cls, key) == value)

            if filters:
                query = query.filter(and_(*filters))
        return query

    @classmethod
    def _s_get_list(cls, **kwargs):
        """
        Override the default get_list method to handle filters
        """
        query = cls.query
        if 'filter' in kwargs:
            query = cls._s_filter(kwargs['filter'], query)
        return query

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

