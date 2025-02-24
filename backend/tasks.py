from celery import Celery
from models import Invoice
from ai_agents.crew import InvoiceProcessor
import logging

logger = logging.getLogger(__name__)

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