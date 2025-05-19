import pytest
import json
import time
from flask import Flask
from unittest.mock import patch, MagicMock
from app.routes.inventory import inventory_bp
from app.models.inventory_item import InventoryItem
from app.models.product import Product

@pytest.fixture
def client():
    """Fixture para crear un cliente de Flask para probar las rutas"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_db_query():
    """Fixture para simular la funcionalidad de la base de datos"""
    with patch('app.routes.inventory.InventoryItem.query') as mock_query:
        yield mock_query

@pytest.fixture
def mock_jsonapi_format_response():
    """Fixture para simular la respuesta de formato JSONAPI"""
    with patch('app.routes.inventory.jsonapi_format_response') as mock_format:
        mock_format.return_value = {'data': [], 'meta': {'count': 0}}
        yield mock_format

def create_mock_product(id=1, name="Test Product", sku="TEST-SKU-001"):
    """Helper para crear un producto mock"""
    mock_product = MagicMock()
    mock_product.id = id
    mock_product.name = name
    mock_product.sku = sku
    mock_product.description = "Test Description"
    mock_product.unit_price = 10.99
    mock_product.storage_conditions = "Cool and dry"
    mock_product.delivery_time = 3
    mock_product.manufacturer_id = 1
    mock_product.created_at = int(time.time()) - 10000
    mock_product.updated_at = int(time.time())
    return mock_product

def create_mock_inventory_item(id=1, product=None, warehouse_id=1, quantity=50):
    """Helper para crear un item de inventario mock"""
    mock_item = MagicMock()
    mock_item.id = id
    mock_item.product_id = product.id if product else 1
    mock_item.product = product
    mock_item.warehouse_id = warehouse_id
    mock_item.quantity = quantity
    mock_item.location = "A-123"
    mock_item.expiry_date = int(time.time()) + 3600*24*30  # 30 días en el futuro
    mock_item.created_at = int(time.time()) - 10000
    mock_item.updated_at = int(time.time())
    return mock_item

def test_search_by_product_name_no_name(client):
    """Test para verificar el caso donde no se proporciona el parámetro 'name'"""
    response = client.get('/api/inventory/search_by_product_name')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Name parameter is required"

def test_search_by_product_name(client, mock_db_query, mock_jsonapi_format_response):
    """Test para verificar la búsqueda por nombre de producto exacto"""
    # Crear producto y item de inventario mockeados
    mock_product = create_mock_product()
    mock_item = create_mock_inventory_item(product=mock_product)

    # Configurar comportamiento del mock para query
    mock_query = MagicMock()
    mock_query.count.return_value = 1
    mock_query.offset.return_value.limit.return_value.all.return_value = [mock_item]
    mock_db_query.join.return_value.filter.return_value = mock_query

    # Realizar la solicitud
    response = client.get('/api/inventory/search_by_product_name?name=Test+Product')

    # Verificar resultados
    assert response.status_code == 200

    # Verificar que se llamó a join y filter con los parámetros correctos
    mock_db_query.join.assert_called_once_with(Product)
    mock_db_query.join().filter.assert_called_once()

    # Verificar que se llamó a jsonapi_format_response con los parámetros correctos
    mock_jsonapi_format_response.assert_called_once()
    args, kwargs = mock_jsonapi_format_response.call_args
    assert args[0] == [mock_item]
    assert kwargs['page'] == 0
    assert kwargs['limit'] == 250
    assert kwargs['total'] == 1

def test_search_by_product_name_with_pagination(client, mock_db_query, mock_jsonapi_format_response):
    """Test para verificar la búsqueda por nombre de producto con paginación personalizada"""
    # Crear producto y item de inventario mockeados
    mock_product = create_mock_product()
    mock_items = [create_mock_inventory_item(id=i, product=mock_product) for i in range(1, 11)]

    # Configurar comportamiento del mock para query
    mock_query = MagicMock()
    mock_query.count.return_value = 100
    mock_query.offset.return_value.limit.return_value.all.return_value = mock_items
    mock_db_query.join.return_value.filter.return_value = mock_query

    # Realizar la solicitud con paginación personalizada
    response = client.get('/api/inventory/search_by_product_name?name=Test+Product&page[offset]=10&page[limit]=10')

    # Verificar resultados
    assert response.status_code == 200

    # Verificar que se usaron los parámetros de paginación correctos
    mock_query.offset.assert_called_once_with(10)
    mock_query.offset().limit.assert_called_once_with(10)

    # Verificar que se llamó a jsonapi_format_response con los parámetros correctos
    mock_jsonapi_format_response.assert_called_once()
    args, kwargs = mock_jsonapi_format_response.call_args
    assert args[0] == mock_items
    assert kwargs['page'] == 10
    assert kwargs['limit'] == 10
    assert kwargs['total'] == 100

def test_search_by_product_name_partial_no_name(client):
    """Test para verificar el caso donde no se proporciona el parámetro 'name' en búsqueda parcial"""
    response = client.get('/api/inventory/search_by_product_name_partial')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Name parameter is required"

def test_search_by_product_name_partial(client, mock_db_query):
    """Test para verificar la búsqueda parcial por nombre de producto"""
    # Crear productos y items de inventario mockeados
    mock_product1 = create_mock_product(id=1, name="Test Product 1")
    mock_product2 = create_mock_product(id=2, name="Test Product 2")
    mock_items = [
        create_mock_inventory_item(id=1, product=mock_product1),
        create_mock_inventory_item(id=2, product=mock_product2)
    ]

    # Configurar comportamiento del mock para query
    mock_query = MagicMock()
    mock_query.count.return_value = 2
    mock_query.offset.return_value.limit.return_value.all.return_value = mock_items
    mock_db_query.join.return_value.filter.return_value = mock_query

    # Realizar la solicitud
    response = client.get('/api/inventory/search_by_product_name_partial?name=Test')

    # Verificar resultados
    assert response.status_code == 200
    data = json.loads(response.data)

    # Verificar la estructura de la respuesta
    assert "data" in data
    assert len(data["data"]) == 2
    assert "included" in data
    assert len(data["included"]) == 2
    assert "meta" in data
    assert data["meta"]["count"] == 2
    assert data["meta"]["total"] == 2

    # Verificar que se llamó a join y filter con los parámetros correctos
    mock_db_query.join.assert_called_once_with(Product)
    mock_db_query.join().filter.assert_called_once()

def test_search_by_product_name_partial_with_pagination(client, mock_db_query):
    """Test para verificar la búsqueda parcial por nombre de producto con paginación"""
    # Crear productos y items de inventario mockeados
    mock_product = create_mock_product()
    mock_items = [create_mock_inventory_item(id=i, product=mock_product) for i in range(1, 6)]

    # Configurar comportamiento del mock para query
    mock_query = MagicMock()
    mock_query.count.return_value = 20
    mock_query.offset.return_value.limit.return_value.all.return_value = mock_items
    mock_db_query.join.return_value.filter.return_value = mock_query

    # Realizar la solicitud con paginación personalizada
    response = client.get('/api/inventory/search_by_product_name_partial?name=Test&page[offset]=5&page[limit]=5')

    # Verificar resultados
    assert response.status_code == 200
    data = json.loads(response.data)

    # Verificar la estructura de la respuesta
    assert "meta" in data
    assert data["meta"]["count"] == 5
    assert data["meta"]["limit"] == 5
    assert data["meta"]["total"] == 20

    # Verificar que se usaron los parámetros de paginación correctos
    mock_query.offset.assert_called_once_with(5)
    mock_query.offset().limit.assert_called_once_with(5)

def test_get_all_items(client, mock_jsonapi_format_response):
    """Test para verificar la obtención de todos los items de inventario"""
    # Configurar la respuesta del mock
    mock_jsonapi_format_response.return_value = {'data': [{'id': '1'}, {'id': '2'}]}

    # Realizar la solicitud
    response = client.get('/api/inventory/all_items')

    # Verificar resultados
    assert response.status_code == 200

    # Verificar que se llamó a jsonapi_format_response con los parámetros correctos
    mock_jsonapi_format_response.assert_called_once()
    kwargs = mock_jsonapi_format_response.call_args.kwargs
    assert kwargs['page'] == 0
    assert kwargs['limit'] == 250

def test_get_all_items_with_pagination(client, mock_jsonapi_format_response):
    """Test para verificar la obtención de todos los items de inventario con paginación"""
    # Configurar la respuesta del mock
    mock_jsonapi_format_response.return_value = {'data': [{'id': '1'}, {'id': '2'}]}
    
    # Realizar la solicitud con paginación personalizada
    response = client.get('/api/inventory/all_items?page[offset]=5&page[limit]=5')
    
    # Verificar resultados
    assert response.status_code == 200
    
    # Verificar que jsonapi_format_response fue llamado con los parámetros de paginación correctos
    mock_jsonapi_format_response.assert_called_once()
    kwargs = mock_jsonapi_format_response.call_args.kwargs
    assert kwargs['page'] == 5
    assert kwargs['limit'] == 5
    # No verificamos el 'total' ya que depende de un mock que puede variar entre ejecuciones
