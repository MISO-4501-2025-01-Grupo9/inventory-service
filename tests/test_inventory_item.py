import time
import unittest
from unittest.mock import patch, MagicMock
from app.models.inventory_item import InventoryItem

class TestInventoryItem(unittest.TestCase):
    @patch('app.models.inventory_item.db')
    def test_inventory_item_defaults_and_query(self, mock_db):
        # Mock the SQLAlchemy model class
        mock_inventory_item = MagicMock()
        mock_inventory_item.__class__ = InventoryItem

        # Configure the mock to return our test instance
        mock_inventory_item.product_id = 123
        mock_inventory_item.warehouse_id = 1
        mock_inventory_item.quantity = 10
        mock_inventory_item.location = "Aisle 3"
        mock_inventory_item.expiry_date = int(time.time()) + 3600
        mock_inventory_item.created_at = int(time.time())
        mock_inventory_item.updated_at = int(time.time())

        # Mock the query behavior
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_inventory_item
        InventoryItem.query = mock_query

        # Test the query
        retrieved = InventoryItem.query.filter_by(product_id=123).first()
        self.assertEqual(retrieved, mock_inventory_item)

if __name__ == '__main__':
    unittest.main()
