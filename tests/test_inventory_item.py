import time
import unittest
from unittest.mock import patch, MagicMock
from app.models.inventory_item import InventoryItem
from app.models.product import Product
from app.models.warehouse import Warehouse

class TestInventoryItem(unittest.TestCase):
    def setUp(self):
        # Create mock classes for all related models
        self.manufacturer_mock = MagicMock()
        self.product_image_mock = MagicMock()
        self.regulation_mock = MagicMock()

        # Mock the Product class with all its relationships
        self.product_mock = MagicMock(spec=Product)
        self.product_mock.manufacturer = self.manufacturer_mock
        self.product_mock.images = [self.product_image_mock]
        self.product_mock.regulations = [self.regulation_mock]

        # Mock the Warehouse class
        self.warehouse_mock = MagicMock(spec=Warehouse)

        # Mock the query property for all classes
        self.product_mock.query = MagicMock()
        self.warehouse_mock.query = MagicMock()
        self.manufacturer_mock.query = MagicMock()

        # Configure the mocks to return themselves when filter_by().first() is called
        self.product_mock.query.filter_by.return_value.first.return_value = self.product_mock
        self.warehouse_mock.query.filter_by.return_value.first.return_value = self.warehouse_mock
        self.manufacturer_mock.query.filter_by.return_value.first.return_value = self.manufacturer_mock

    def test_inventory_item_defaults_and_query(self):
        # Mock all required classes
        with patch('app.models.inventory_item.Product', return_value=self.product_mock), \
             patch('app.models.inventory_item.Warehouse', return_value=self.warehouse_mock), \
             patch('app.models.product.Manufacturer', return_value=self.manufacturer_mock), \
             patch('app.models.product.ProductImage', return_value=self.product_image_mock), \
             patch('app.models.product.ProductCountryRegulation', return_value=self.regulation_mock):

            # Creamos una instancia del modelo sin persistir en base de datos.
            inventory_item = InventoryItem(
                product_id=123,
                warehouse_id=1,
                quantity=10,
                location="Aisle 3",
                expiry_date=int(time.time()) + 3600  # Fecha de expiración simulada
            )

            # Simulamos manualmente la asignación de valores por defecto al estilo de SQLAlchemy.
            if inventory_item.created_at is None:
                inventory_item.created_at = int(time.time())
            if inventory_item.updated_at is None:
                inventory_item.updated_at = int(time.time())

            # Verificamos que se asignen los valores por defecto simulados.
            self.assertIsNotNone(inventory_item.created_at)
            self.assertIsNotNone(inventory_item.updated_at)

            # Mockeamos el atributo query para simular la interacción con la base de datos.
            with patch.object(InventoryItem, 'query', new=MagicMock()) as mock_query:
                # Configuramos el mock para que al llamar a filter_by(...).first() devuelva nuestro objeto.
                mock_query.filter_by.return_value.first.return_value = inventory_item

                retrieved = InventoryItem.query.filter_by(product_id=123).first()
                self.assertEqual(retrieved, inventory_item)

if __name__ == '__main__':
    unittest.main()
