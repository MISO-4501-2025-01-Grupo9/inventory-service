import csv
import io
from datetime import datetime
from google.cloud import storage
from app import db
from app.models.product import Product
from app.models.inventory_item import InventoryItem

class CSVProcessor:
    def __init__(self, bucket_name, filename):
        self.bucket_name = bucket_name
        self.filename = filename
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket_name)
        self.blob = self.bucket.blob(filename)

    def process(self):
        try:
            # Descargar el archivo CSV
            csv_content = self.blob.download_as_text()

            # Procesar el CSV
            csv_file = io.StringIO(csv_content)
            reader = csv.DictReader(csv_file)

            for row in reader:
                # Crear o actualizar el producto
                product = Product.query.filter_by(sku=row['sku']).first()
                if not product:
                    product = Product(
                        manufacturer_id=int(row['manufacturer_id']),
                        name=row['name'],
                        description=row['description'],
                        sku=row['sku'],
                        unit_price=float(row['unit_price']),
                        storage_conditions=row['storage_conditions'],
                        delivery_time=int(row['delivery_time'])
                    )
                    db.session.add(product)
                    db.session.flush()  # Para obtener el ID del producto

                # Crear o actualizar el item de inventario
                inventory_item = InventoryItem.query.filter_by(
                    product_id=product.id,
                    warehouse_id=int(row['warehouse_id'])
                ).first()

                if not inventory_item:
                    inventory_item = InventoryItem(
                        product_id=product.id,
                        warehouse_id=int(row['warehouse_id']),
                        quantity=int(row['quantity']),
                        location=row['location'],
                        expiry_date=int(row['expiry_date'])
                    )
                    db.session.add(inventory_item)
                else:
                    inventory_item.quantity = int(row['quantity'])
                    inventory_item.location = row['location']
                    inventory_item.expiry_date = int(row['expiry_date'])
                    inventory_item.updated_at = int(datetime.now().timestamp())

            # Guardar todos los cambios
            db.session.commit()
            return True, "Archivo procesado exitosamente"

        except Exception as e:
            db.session.rollback()
            return False, f"Error procesando el archivo: {str(e)}"
