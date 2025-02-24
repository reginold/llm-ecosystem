from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from models import Invoice, ReconciliationResult, Report
from ai_agents.crew import InvoiceProcessor
from celery import Celery
import os
from datetime import datetime
from dotenv import load_dotenv
import logging
from flask_socketio import SocketIO
from bson import ObjectId
from config import db  # Add this import

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Config
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    # Ensure proper permissions
    os.chmod(UPLOAD_FOLDER, 0o777)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# Celery setup
celery = Celery(
    'tasks',
    broker=os.getenv('REDIS_URL'),
    backend=os.getenv('REDIS_URL')
)

# Configure Celery to use the app context
class FlaskTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = FlaskTask

ALLOWED_EXTENSIONS = {'pdf', 'csv', 'json', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@celery.task
def process_invoice(invoice_id: str):
    try:
        # Get invoice from MongoDB
        invoice = Invoice.get(invoice_id)
        if not invoice:
            return {'success': False, 'error': 'Invoice not found'}

        # Update status
        Invoice.update(invoice_id, {'status': 'PROCESSING'})

        # Process invoice
        processor = InvoiceProcessor()
        extracted_data = processor.process_invoice(invoice['file_path'])

        # Update invoice with extracted data
        Invoice.update(invoice_id, {
            'extracted_data': extracted_data,
            'status': 'COMPLETED'
        })

        return {
            'success': True,
            'invoice_id': invoice_id
        }

    except Exception as e:
        logger.error(f"Error processing invoice: {str(e)}")
        return {'success': False, 'error': str(e)}

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        # Debug logging
        logger.debug("Files in request: %s", request.files)
        logger.debug("Request headers: %s", request.headers)

        if 'file' not in request.files:
            logger.error("No file part in request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.error("No selected file")
            return jsonify({'error': 'No selected file'}), 400

        if not allowed_file(file.filename):
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type'}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Debug logging
        logger.debug("Saving file to: %s", file_path)
        file.save(file_path)

        # Create invoice document in MongoDB
        invoice = Invoice.create(file_path=file_path)
        
        # Start async processing
        task = process_invoice.delay(str(invoice['_id']))
        
        response_data = {
            'success': True,
            'message': 'File uploaded successfully',
            'invoice_id': str(invoice['_id']),
            'task_id': task.id
        }
        logger.debug("Sending response: %s", response_data)
        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Error in upload: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/results/<task_id>', methods=['GET'])
def get_results(task_id):
    try:
        task_result = celery.AsyncResult(task_id)
        
        if task_result.ready():
            result = task_result.get()
            if result.get('success'):
                invoice_id = result['invoice_id']
                invoice = Invoice.get(invoice_id)
                if invoice:
                    return jsonify({
                        'status': 'COMPLETED',
                        'invoice_id': invoice_id,
                        'extracted_data': invoice['extracted_data'],
                        'discrepancies': {
                            'source_type': 'image',
                            'ocr_confidence': 'high'
                        }
                    }), 200
            return jsonify({
                'status': 'FAILED',
                'error': 'Processing failed',
                'invoice_id': result.get('invoice_id')
            }), 200
        
        return jsonify({
            'status': 'PROCESSING',
            'task_id': task_id
        }), 202

    except Exception as e:
        logger.error(f"Error in get_results: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/invoice/<invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    invoice = Invoice.get(invoice_id)
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404
    invoice['_id'] = str(invoice['_id'])  # Convert ObjectId to string
    return jsonify(invoice), 200

@app.route('/api/invoice/save', methods=['POST'])
def save_invoice():
    try:
        data = request.json
        invoice_id = data.get('invoice_id')
        edited_data = data.get('edited_data')
        
        if not invoice_id or not edited_data:
            return jsonify({'error': 'Missing required data'}), 400

        # Update invoice with edited data
        invoice = Invoice.update(invoice_id, {
            'user_edited_data': edited_data,
            'status': 'COMPLETED'
        })
        
        # Create processing report
        report = Report.create(
            invoice_id=invoice_id,
            processing_status='COMPLETED',
            ocr_confidence=0.95,
            validation_results={
                'field_accuracy': 0.98,
                'missing_fields': [],
                'warnings': []
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Invoice and report saved successfully',
            'invoice_id': str(invoice['_id']),
            'report_id': str(report['_id'])
        }), 200

    except Exception as e:
        logger.error(f"Error saving invoice: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)