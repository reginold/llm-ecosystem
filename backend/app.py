from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from models import db, Invoice, ReconciliationResult
from ai_agents.crew import InvoiceProcessor
from celery import Celery
import os
from datetime import datetime
from dotenv import load_dotenv
import logging
from flask_socketio import SocketIO

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db.init_app(app)

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
def process_invoice(invoice_id: int):
    invoice = None  # Initialize invoice variable
    try:
        logger.info(f"Processing invoice: {invoice_id}")
        # Get invoice from database
        with app.app_context():  # Add app context for database operations
            invoice = Invoice.query.get(invoice_id)
            if not invoice:
                logger.error(f"Invoice not found: {invoice_id}")
                return {'success': False, 'error': 'Invoice not found'}

            # Update status to processing
            invoice.status = 'PROCESSING'
            db.session.commit()
            logger.info(f"Updated invoice status to PROCESSING: {invoice_id}")

            # Initialize AI processing with socketio
            crew = InvoiceProcessor()
            extracted_data = crew.process_invoice(invoice.file_path)
            
            # Log the extracted data
            logger.info(f"Extracted Data for invoice {invoice_id}: {extracted_data}")

            # Update invoice with extracted data
            invoice.extracted_data = extracted_data
            invoice.status = 'COMPLETED'
            db.session.commit()
            logger.info(f"Updated invoice with extracted data: {invoice_id}")

            # Create reconciliation result
            result = ReconciliationResult(
                invoice_id=invoice.id,
                status='COMPLETED',
                discrepancies={},  # This would be populated by the AI
                ai_notes="Invoice processed successfully"
            )
            db.session.add(result)
            db.session.commit()
            logger.info(f"Created reconciliation result for invoice: {invoice_id}")

            return {
                'success': True,
                'invoice_id': invoice.id,
                'status': 'COMPLETED'
            }

    except Exception as e:
        logger.error(f"Error processing invoice {invoice_id}: {str(e)}", exc_info=True)
        if invoice:
            with app.app_context():  # Add app context for database operations
                invoice.status = 'FAILED'
                invoice.error_message = str(e)
                db.session.commit()
        return {'success': False, 'error': str(e)}

@app.route('/api/upload-invoice', methods=['POST'])
def upload_invoice():
    try:
        if 'invoice_file' not in request.files:
            logger.error("No file part in request")
            return jsonify({
                'success': False,
                'message': 'No file provided'
            }), 400

        file = request.files['invoice_file']

        if file.filename == '':
            logger.error("No selected file")
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400

        if not allowed_file(file.filename):
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({
                'success': False,
                'message': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400

        # Secure the filename and save the file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        logger.info(f"File saved: {file_path}")

        # Create invoice record
        invoice = Invoice(
            filename=filename,
            file_path=file_path,
            status='PENDING',
            upload_date=datetime.utcnow()
        )
        db.session.add(invoice)
        db.session.commit()
        logger.info(f"Invoice record created: {invoice.id}")

        # Start async processing
        task = process_invoice.delay(invoice.id)
        logger.info(f"Task created: {task.id}")

        return jsonify({
            'success': True,
            'message': 'Invoice uploaded successfully',
            'invoice': invoice.to_dict(),
            'task_id': task.id
        }), 202

    except Exception as e:
        logger.error(f"Error in upload_invoice: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/results/<task_id>', methods=['GET'])
def get_results(task_id):
    try:
        logger.info(f"Checking task status: {task_id}")
        task_result = celery.AsyncResult(task_id)
        
        if task_result.ready():
            result = task_result.get()
            logger.info(f"Task completed: {result}")
            if result.get('success'):
                invoice_id = result['invoice_id']
                # Get the invoice data directly
                invoice = Invoice.query.get(invoice_id)
                if invoice:
                    return jsonify({
                        'status': 'COMPLETED',
                        'extracted_data': invoice.extracted_data,
                        'discrepancies': {
                            'source_type': 'image',
                            'ocr_confidence': 'high',
                            'extracted_text': 'Processed with Qwen VL',
                            'analysis_result': invoice.extracted_data
                        }
                    }), 200
            return jsonify(result), 200
        
        logger.info(f"Task still processing: {task_id}")
        return jsonify({
            'status': 'PROCESSING',
            'task_id': task_id
        }), 202

    except Exception as e:
        logger.error(f"Error in get_results: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/invoice/<int:invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    return jsonify(invoice.to_dict()), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 