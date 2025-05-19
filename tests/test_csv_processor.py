import unittest
from unittest.mock import patch, MagicMock, call
import io
from datetime import datetime
from flask import Flask
from app.services.csv_processor import CSVProcessor
from app.models.product import Product
from app.models.inventory_item import InventoryItem
from app import db

# Crear una aplicación Flask para proporcionar un contexto
_test_flask_app = Flask(__name__)  # Renamed to avoid pytest collecting it as a test
_test_flask_app.config['TESTING'] = True
_test_flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

class TestCSVProcessor(unittest.TestCase):

    def setUp(self):
        # Configuración común para las pruebas
        self.bucket_name = "test-bucket"
        self.filename = "test-file.csv"
        # Crear un contexto de aplicación para las pruebas
        self.app_context = _test_flask_app.app_context()
        self.app_context.push()

        # CSV de ejemplo para las pruebas
        self.sample_csv = """sku,manufacturer_id,name,description,unit_price,storage_conditions,delivery_time,warehouse_id,quantity,location,expiry_date
SKU123,1,Test Product,This is a test product,10.99,Cool and dry,5,1,100,A1,1714974947
SKU456,2,Another Product,This is another test product,20.50,Refrigerated,3,2,50,B2,1746510947
"""

    def tearDown(self):
        # Limpiar el contexto de aplicación después de cada prueba
        self.app_context.pop()

    @patch('app.services.csv_processor.storage.Client')
    @patch('app.services.csv_processor.Product.query')
    @patch('app.services.csv_processor.InventoryItem.query')
    @patch('app.services.csv_processor.db.session')
    def test_process_new_products_and_items(self, mock_db_session, mock_inventory_item_query,
                                     mock_product_query, mock_storage_client):
        """Test procesamiento de CSV con productos e items de inventario nuevos"""
        # Configurar los mocks
        mock_storage_client_instance = mock_storage_client.return_value
        mock_bucket = mock_storage_client_instance.bucket.return_value
        mock_blob = mock_bucket.blob.return_value
        mock_blob.download_as_text.return_value = self.sample_csv

        # Simular que no existen los productos ni los items de inventario
        mock_product_query.filter_by.return_value.first.return_value = None
        mock_inventory_item_query.filter_by.return_value.first.return_value = None

        # Crear productos simulados para devolver IDs
        mock_product1 = MagicMock(id=1)
        mock_product2 = MagicMock(id=2)

        # Instanciar el procesador y ejecutar el procesamiento
        processor = CSVProcessor(self.bucket_name, self.filename)
        success, message = processor.process()

        # Verificar que el método download_as_text fue llamado
        mock_blob.download_as_text.assert_called_once()

        # Verificar que se intentó buscar los productos
        self.assertEqual(mock_product_query.filter_by.call_count, 2)

        # Verificar que se añadieron 2 productos y 2 items de inventario
        self.assertEqual(mock_db_session.add.call_count, 4)

        # Verificar que se realizó commit
        mock_db_session.commit.assert_called_once()

        # Verificar el resultado
        self.assertTrue(success)
        self.assertEqual(message, "Archivo procesado exitosamente")

    @patch('app.services.csv_processor.storage.Client')
    @patch('app.services.csv_processor.Product.query')
    @patch('app.services.csv_processor.InventoryItem.query')
    @patch('app.services.csv_processor.db.session')
    def test_process_existing_products_and_items(self, mock_db_session, mock_inventory_item_query,
                                         mock_product_query, mock_storage_client):
        """Test procesamiento de CSV con productos e items de inventario existentes"""
        # Configurar los mocks
        mock_storage_client_instance = mock_storage_client.return_value
        mock_bucket = mock_storage_client_instance.bucket.return_value
        mock_blob = mock_bucket.blob.return_value
        mock_blob.download_as_text.return_value = self.sample_csv

        # Simular que existen los productos y los items de inventario
        mock_product1 = MagicMock(id=1)
        mock_product2 = MagicMock(id=2)
        mock_product_query.filter_by.side_effect = lambda sku: MagicMock(
            first=lambda: mock_product1 if sku == 'SKU123' else mock_product2
        )

        mock_inventory_item1 = MagicMock(quantity=0, location='', expiry_date=0)
        mock_inventory_item2 = MagicMock(quantity=0, location='', expiry_date=0)
        mock_inventory_item_query.filter_by.side_effect = lambda product_id, warehouse_id: MagicMock(
            first=lambda: mock_inventory_item1 if product_id == 1 else mock_inventory_item2
        )

        # Instanciar el procesador y ejecutar el procesamiento
        processor = CSVProcessor(self.bucket_name, self.filename)
        success, message = processor.process()

        # Verificar que el método download_as_text fue llamado
        mock_blob.download_as_text.assert_called_once()

        # Verificar que se intentó buscar los productos
        self.assertEqual(mock_product_query.filter_by.call_count, 2)

        # Verificar que no se añadieron productos nuevos (ya existían)
        # Pero si actualizaron los items de inventario existentes
        self.assertEqual(mock_db_session.add.call_count, 0)

        # Verificar que se actualizaron los items de inventario
        self.assertEqual(mock_inventory_item1.quantity, 100)
        self.assertEqual(mock_inventory_item1.location, 'A1')
        self.assertEqual(mock_inventory_item1.expiry_date, 1714974947)

        self.assertEqual(mock_inventory_item2.quantity, 50)
        self.assertEqual(mock_inventory_item2.location, 'B2')
        self.assertEqual(mock_inventory_item2.expiry_date, 1746510947)

        # Verificar que se realizó commit
        mock_db_session.commit.assert_called_once()

        # Verificar el resultado
        self.assertTrue(success)
        self.assertEqual(message, "Archivo procesado exitosamente")

    @patch('app.services.csv_processor.storage.Client')
    @patch('app.services.csv_processor.Product.query')
    @patch('app.services.csv_processor.InventoryItem.query')
    @patch('app.services.csv_processor.db.session')
    def test_process_mixed_scenario(self, mock_db_session, mock_inventory_item_query,
                           mock_product_query, mock_storage_client):
        """Test procesamiento de CSV con un producto existente y otro nuevo"""
        # Configurar los mocks
        mock_storage_client_instance = mock_storage_client.return_value
        mock_bucket = mock_storage_client_instance.bucket.return_value
        mock_blob = mock_bucket.blob.return_value
        mock_blob.download_as_text.return_value = self.sample_csv

        # Simular que existe el primer producto pero no el segundo
        mock_product1 = MagicMock(id=1)
        mock_product_query.filter_by.side_effect = lambda sku: MagicMock(
            first=lambda: mock_product1 if sku == 'SKU123' else None
        )

        # Simular que existe un item de inventario para el primer producto
        mock_inventory_item1 = MagicMock(quantity=0, location='', expiry_date=0)
        mock_inventory_item_query.filter_by.side_effect = lambda product_id, warehouse_id: MagicMock(
            first=lambda: mock_inventory_item1 if product_id == 1 else None
        )

        # Instanciar el procesador y ejecutar el procesamiento
        processor = CSVProcessor(self.bucket_name, self.filename)
        success, message = processor.process()

        # Verificar que el método download_as_text fue llamado
        mock_blob.download_as_text.assert_called_once()

        # Verificar que se añadieron el segundo producto y su item de inventario
        self.assertEqual(mock_db_session.add.call_count, 2)

        # Verificar que se realizó commit
        mock_db_session.commit.assert_called_once()

        # Verificar el resultado
        self.assertTrue(success)
        self.assertEqual(message, "Archivo procesado exitosamente")

    @patch('app.services.csv_processor.storage.Client')
    @patch('app.services.csv_processor.db.session')
    @patch('app.services.csv_processor.Product')
    @patch('app.services.csv_processor.InventoryItem')
    def test_process_download_error(self, mock_inventory_item, mock_product, mock_db_session, mock_storage_client):
        """Test error al descargar el archivo CSV"""
        # Configurar el mock para simular un error al descargar
        mock_storage_client_instance = mock_storage_client.return_value
        mock_bucket = mock_storage_client_instance.bucket.return_value
        mock_blob = mock_bucket.blob.return_value
        mock_blob.download_as_text.side_effect = Exception("Error de descarga")

        # Instanciar el procesador y ejecutar el procesamiento
        processor = CSVProcessor(self.bucket_name, self.filename)
        success, message = processor.process()

        # Verificar que se llamó a rollback
        mock_db_session.rollback.assert_called_once()

        # Verificar el resultado
        self.assertFalse(success)
        self.assertEqual(message, "Error procesando el archivo: Error de descarga")

    @patch('app.services.csv_processor.storage.Client')
    @patch('app.services.csv_processor.db.session')
    @patch('app.services.csv_processor.Product.query')
    @patch('app.services.csv_processor.InventoryItem.query')
    def test_process_database_error(self, mock_inventory_item_query, mock_product_query,
                                   mock_db_session, mock_storage_client):
        """Test error al actualizar la base de datos"""
        # Configurar el mock para simular un error de base de datos
        mock_storage_client_instance = mock_storage_client.return_value
        mock_bucket = mock_storage_client_instance.bucket.return_value
        mock_blob = mock_bucket.blob.return_value
        mock_blob.download_as_text.return_value = self.sample_csv

        # Configurar mocks para Product y InventoryItem para evitar errores de None
        mock_product = MagicMock(id=1)
        mock_product_query.filter_by.return_value.first.return_value = mock_product
        mock_inventory_item_query.filter_by.return_value.first.return_value = MagicMock()

        # Simular error al hacer commit
        mock_db_session.commit.side_effect = Exception("Error de base de datos")

        # Instanciar el procesador y ejecutar el procesamiento
        processor = CSVProcessor(self.bucket_name, self.filename)
        success, message = processor.process()

        # Verificar que se llamó a rollback
        mock_db_session.rollback.assert_called_once()

        # Verificar el resultado
        self.assertFalse(success)
        self.assertEqual(message, "Error procesando el archivo: Error de base de datos")

    @patch('app.services.csv_processor.storage.Client')
    @patch('app.services.csv_processor.db.session')
    @patch('app.services.csv_processor.Product.query')
    @patch('app.services.csv_processor.InventoryItem.query')
    def test_process_csv_parse_error(self, mock_inventory_item_query, mock_product_query,
                                    mock_db_session, mock_storage_client):
        """Test error al analizar el CSV"""
        # Configurar el mock para retornar un CSV mal formado
        mock_storage_client_instance = mock_storage_client.return_value
        mock_bucket = mock_storage_client_instance.bucket.return_value
        mock_blob = mock_bucket.blob.return_value
        mock_blob.download_as_text.return_value = "mal,formado,csv\nsin,suficientes,columnas"

        # Instanciar el procesador y ejecutar el procesamiento
        processor = CSVProcessor(self.bucket_name, self.filename)
        success, message = processor.process()

        # Verificar que se llamó a rollback
        mock_db_session.rollback.assert_called_once()

        # Verificar el resultado
        self.assertFalse(success)
        self.assertTrue("Error procesando el archivo:" in message)

if __name__ == '__main__':
    unittest.main()
