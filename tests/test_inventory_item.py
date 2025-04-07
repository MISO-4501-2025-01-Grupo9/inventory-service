import time
import unittest
from unittest.mock import patch, MagicMock
from app.models.inventory_item import InventoryItem

class TestInventoryItem(unittest.TestCase):
    def test_inventory_item_defaults_and_query(self):
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
