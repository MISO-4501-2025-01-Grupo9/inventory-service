from flask import Blueprint, jsonify, request
from app.models.inventory_item import InventoryItem
from app.models.product import Product
from sqlalchemy import or_
from app import db
from safrs import jsonapi_format_response

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/search_by_product_name', methods=['GET'])
def search_by_product_name():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Name parameter is required"}), 400
    
    # Obtener parámetros de paginación
    page = request.args.get('page[offset]', 0, type=int)
    limit = request.args.get('page[limit]', 250, type=int)
    
    # Realizar la búsqueda con paginación
    query = InventoryItem.query.join(Product).filter(Product.name == name)
    total = query.count()
    items = query.offset(page).limit(limit).all()
    
    # Usar el formato nativo de SAFRS
    return jsonapi_format_response(items, page=page, limit=limit, total=total)

@inventory_bp.route('/search_by_product_name_partial', methods=['GET'])
def search_by_product_name_partial():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Name parameter is required"}), 400
    
    # Obtener parámetros de paginación
    page = request.args.get('page[offset]', 0, type=int)
    limit = request.args.get('page[limit]', 250, type=int)
    
    # Realizar la búsqueda con paginación y eager loading de productos
    query = InventoryItem.query.join(Product).filter(Product.name.ilike(f'%{name}%'))
    total = query.count()
    items = query.offset(page).limit(limit).all()
    
    # Preparar la respuesta en formato JSON:API
    data = []
    included = []
    
    for item in items:
        item_dict = {
            "type": "InventoryItem",
            "id": str(item.id),
            "attributes": {
                "product_id": item.product_id,
                "warehouse_id": item.warehouse_id,
                "quantity": item.quantity,
                "location": item.location,
                "expiry_date": item.expiry_date,
                "created_at": item.created_at,
                "updated_at": item.updated_at
            },
            "relationships": {
                "product": {
                    "data": {
                        "type": "Product",
                        "id": str(item.product_id)
                    }
                }
            }
        }
        
        if item.product:
            item_dict["attributes"]["product_name"] = item.product.name
            item_dict["attributes"]["product_sku"] = item.product.sku
            
            # Agregar el producto a included
            product_dict = {
                "type": "Product",
                "id": str(item.product.id),
                "attributes": {
                    "name": item.product.name,
                    "sku": item.product.sku,
                    "description": item.product.description,
                    "unit_price": float(item.product.unit_price),
                    "storage_conditions": item.product.storage_conditions,
                    "delivery_time": item.product.delivery_time,
                    "manufacturer_id": item.product.manufacturer_id,
                    "created_at": item.product.created_at,
                    "updated_at": item.product.updated_at
                }
            }
            included.append(product_dict)
        
        data.append(item_dict)
    
    response = {
        "data": data,
        "included": included,
        "jsonapi": {"version": "1.0"},
        "links": {
            "self": f"/api/inventory/search_by_product_name_partial?name={name}&page[offset]={page}&page[limit]={limit}"
        },
        "meta": {
            "count": len(items),
            "limit": limit,
            "total": total
        }
    }
    
    return jsonify(response)

@inventory_bp.route('/all_items', methods=['GET'])
def get_all_items():
    """Endpoint para ver todos los items de inventario con sus productos"""
    # Obtener parámetros de paginación
    page = request.args.get('page[offset]', 0, type=int)
    limit = request.args.get('page[limit]', 250, type=int)
    
    # Realizar la consulta con paginación
    query = InventoryItem.query
    total = query.count()
    items = query.offset(page).limit(limit).all()
    
    # Usar el formato nativo de SAFRS
    return jsonapi_format_response(items, page=page, limit=limit, total=total) 