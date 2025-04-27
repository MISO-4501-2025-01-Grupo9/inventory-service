import json
from flask import Blueprint, request
from app.services.csv_processor import CSVProcessor

pubsub_bp = Blueprint('pubsub', __name__)

@pubsub_bp.route('/process-csv', methods=['POST'])
def process_csv():
    try:
        print("=== Iniciando procesamiento de mensaje Pub/Sub ===")
        print(f"Headers recibidos: {dict(request.headers)}")

        # Obtener el mensaje de Pub/Sub
        envelope = request.get_json()
        print(f"Mensaje recibido (raw): {envelope}")

        if not envelope:
            print("Error: No se recibió mensaje")
            return 'No message received', 400

        if not isinstance(envelope, dict):
            print(f"Error: El mensaje no es un diccionario. Tipo recibido: {type(envelope)}")
            return 'Invalid message format', 400

        if 'message' not in envelope:
            print(f"Error: No se encontró la clave 'message' en el envelope. Claves disponibles: {envelope.keys()}")
            return 'Invalid message format', 400

        # Obtener los datos del mensaje
        message = envelope['message']
        print(f"Contenido del mensaje: {message}")

        if not message.get('data'):
            print("Error: No se encontró 'data' en el mensaje")
            return 'No data in message', 400

        # Los datos vienen como string JSON, necesitamos deserializarlos
        data_str = message['data']
        print(f"Datos recibidos (string): {data_str}")

        try:
            data = json.loads(data_str)
            print(f"Datos deserializados: {data}")
        except json.JSONDecodeError as e:
            print(f"Error deserializando datos: {str(e)}")
            return 'Invalid JSON data', 400

        if not isinstance(data, dict):
            print(f"Error: Los datos no son un diccionario. Tipo recibido: {type(data)}")
            return 'Invalid data format', 400

        # Validar campos requeridos
        if 'bucket' not in data:
            print("Error: Falta el campo 'bucket' en los datos")
            return 'Missing required field: bucket', 400

        if 'filename' not in data:
            print("Error: Falta el campo 'filename' en los datos")
            return 'Missing required field: filename', 400

        print(f"Procesando archivo: bucket={data['bucket']}, filename={data['filename']}")

        # Procesar el archivo CSV
        processor = CSVProcessor(data['bucket'], data['filename'])
        success, message = processor.process()

        if success:
            print("CSV procesado exitosamente")
            return 'CSV processed successfully', 200
        else:
            print(f"Error procesando CSV: {message}")
            return f'Error processing CSV: {message}', 500

    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return f'Error: {str(e)}', 500
