import json
from flask import Blueprint, request
from app.services.csv_processor import CSVProcessor

pubsub_bp = Blueprint('pubsub', __name__)

@pubsub_bp.route('/process-csv', methods=['POST'])
def process_csv():
    try:
        # Obtener el mensaje de Pub/Sub
        envelope = request.get_json()
        if not envelope:
            return 'No message received', 400

        if not isinstance(envelope, dict) or 'message' not in envelope:
            return 'Invalid message format', 400

        # Decodificar el mensaje
        message = envelope['message']
        if not message.get('data'):
            return 'No data in message', 400

        # Decodificar los datos del mensaje
        data = json.loads(message['data'].decode('utf-8'))

        # Procesar el archivo CSV
        processor = CSVProcessor(data['bucket'], data['filename'])
        success, message = processor.process()

        if success:
            return 'CSV processed successfully', 200
        else:
            return f'Error processing CSV: {message}', 500

    except Exception as e:
        return f'Error: {str(e)}', 500
