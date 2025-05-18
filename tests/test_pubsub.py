import pytest
import json
import base64
from unittest.mock import patch, MagicMock
from flask import Flask
from app.routes.pubsub import pubsub_bp

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(pubsub_bp)
    with app.test_client() as client:
        yield client

def create_pubsub_message(data):
    """Helper method to create a PubSub message payload"""
    json_data = json.dumps(data)
    encoded_data = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
    return {
        'message': {
            'data': encoded_data,
            'messageId': '123456',
            'publishTime': '2023-01-01T00:00:00Z'
        }
    }

@patch('app.routes.pubsub.CSVProcessor')
def test_process_csv_success(mock_csv_processor, client):
    # Configurar el mock para simular un procesamiento exitoso
    processor_instance = MagicMock()
    processor_instance.process.return_value = (True, "CSV procesado exitosamente")
    mock_csv_processor.return_value = processor_instance

    # Crear un mensaje de PubSub simulado
    message_data = {
        'bucket': 'test-bucket',
        'filename': 'test-file.csv'
    }
    request_data = create_pubsub_message(message_data)

    # Enviar la solicitud
    response = client.post('/process-csv', json=request_data)

    # Verificar resultados
    assert response.status_code == 200
    assert response.data.decode('utf-8') == 'CSV processed successfully'

    # Verificar que el procesador fue llamado con los argumentos correctos
    mock_csv_processor.assert_called_once_with('test-bucket', 'test-file.csv')
    processor_instance.process.assert_called_once()

@patch('app.routes.pubsub.CSVProcessor')
def test_process_csv_failure(mock_csv_processor, client):
    # Configurar el mock para simular un error en el procesamiento
    processor_instance = MagicMock()
    processor_instance.process.return_value = (False, "Error al procesar")
    mock_csv_processor.return_value = processor_instance

    # Crear un mensaje de PubSub simulado
    message_data = {
        'bucket': 'test-bucket',
        'filename': 'test-file.csv'
    }
    request_data = create_pubsub_message(message_data)

    # Enviar la solicitud
    response = client.post('/process-csv', json=request_data)

    # Verificar resultados
    assert response.status_code == 500
    assert 'Error processing CSV: Error al procesar' in response.data.decode('utf-8')

def test_process_csv_no_message(client):
    # Enviar una solicitud sin mensaje
    response = client.post('/process-csv', json={})

    # Verificar resultados
    assert response.status_code == 400
    assert response.data.decode('utf-8') == 'No message received'

def test_process_csv_invalid_format(client):
    # Enviar una solicitud con formato inválido
    response = client.post('/process-csv', json="not_a_dict")

    # Verificar resultados
    assert response.status_code == 400
    assert response.data.decode('utf-8') == 'Invalid message format'

def test_process_csv_no_message_key(client):
    # Enviar una solicitud sin la clave 'message'
    response = client.post('/process-csv', json={'not_message': {}})

    # Verificar resultados
    assert response.status_code == 400
    assert response.data.decode('utf-8') == 'Invalid message format'

def test_process_csv_no_data(client):
    # Enviar una solicitud sin 'data' en el mensaje
    request_data = {
        'message': {
            'not_data': 'something'
        }
    }
    response = client.post('/process-csv', json=request_data)

    # Verificar resultados
    assert response.status_code == 400
    assert response.data.decode('utf-8') == 'No data in message'

def test_process_csv_invalid_base64(client):
    # Enviar una solicitud con datos base64 inválidos
    request_data = {
        'message': {
            'data': 'invalid_base64!'
        }
    }
    response = client.post('/process-csv', json=request_data)

    # Verificar resultados
    assert response.status_code == 400
    assert response.data.decode('utf-8') == 'Invalid base64 data'

def test_process_csv_invalid_json(client):
    # Enviar una solicitud con JSON inválido después de decodificar base64
    # Codificar una cadena que no sea JSON válido
    invalid_json = "not_valid_json"
    encoded_data = base64.b64encode(invalid_json.encode('utf-8')).decode('utf-8')

    request_data = {
        'message': {
            'data': encoded_data
        }
    }
    response = client.post('/process-csv', json=request_data)

    # Verificar resultados
    assert response.status_code == 400
    assert response.data.decode('utf-8') == 'Invalid JSON data'

def test_process_csv_missing_bucket(client):
    # Crear un mensaje sin el campo 'bucket'
    message_data = {
        'filename': 'test-file.csv'
    }
    request_data = create_pubsub_message(message_data)

    # Enviar la solicitud
    response = client.post('/process-csv', json=request_data)

    # Verificar resultados
    assert response.status_code == 400
    assert response.data.decode('utf-8') == 'Missing required field: bucket'

def test_process_csv_missing_filename(client):
    # Crear un mensaje sin el campo 'filename'
    message_data = {
        'bucket': 'test-bucket'
    }
    request_data = create_pubsub_message(message_data)

    # Enviar la solicitud
    response = client.post('/process-csv', json=request_data)

    # Verificar resultados
    assert response.status_code == 400
    assert response.data.decode('utf-8') == 'Missing required field: filename'
