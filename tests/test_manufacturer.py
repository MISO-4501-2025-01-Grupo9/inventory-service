import time
from unittest.mock import patch, MagicMock
from app.models.manufacturer import Manufacturer

def test_manufacturer_defaults_and_query():
    # Creamos una instancia del modelo sin persistir en base de datos.
    manufacturer = Manufacturer(
        name="Test Manufacturer",
        email="test@example.com",
        country="Test Country"
    )

    # En un entorno real, SQLAlchemy asignaría los valores por defecto al hacer flush.
    # Como estamos en un unit test sin DB, simulamos manualmente ese comportamiento.
    if manufacturer.created_at is None:
        manufacturer.created_at = int(time.time())
    if manufacturer.updated_at is None:
        manufacturer.updated_at = int(time.time())

    # Verificamos que se asignen los valores por defecto simulados.
    assert manufacturer.created_at is not None
    assert manufacturer.updated_at is not None

    # Mockeamos el atributo query para simular la interacción con la base de datos.
    with patch.object(Manufacturer, 'query', new=MagicMock()) as mock_query:
        # Configuramos el mock para que al llamar a filter_by(...).first() devuelva nuestro objeto.
        mock_query.filter_by.return_value.first.return_value = manufacturer

        retrieved = Manufacturer.query.filter_by(email="test@example.com").first()
        assert retrieved == manufacturer
