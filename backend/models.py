from datetime import datetime
from bson import ObjectId
from config import db

class Invoice:
    collection = db.invoices

    @staticmethod
    def create(file_path: str) -> dict:
        invoice = {
            'file_path': file_path,
            'bill_to': None,
            'emailing_address': None,
            'invoice_number': None,
            'invoice_date': None,
            'invoice_amount': None,
            'services': [],
            'status': 'PENDING',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = Invoice.collection.insert_one(invoice)
        invoice['_id'] = str(result.inserted_id)
        return invoice

    @staticmethod
    def get(invoice_id: str) -> dict:
        return Invoice.collection.find_one({'_id': ObjectId(invoice_id)})

    @staticmethod
    def update(invoice_id: str, data: dict) -> dict:
        # Only save the essential fields
        allowed_fields = {
            'bill_to', 'emailing_address', 'invoice_number',
            'invoice_date', 'invoice_amount', 'services',
            'status', 'updated_at'
        }
        
        # Filter out unwanted fields
        filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
        filtered_data['updated_at'] = datetime.utcnow()
        
        Invoice.collection.update_one(
            {'_id': ObjectId(invoice_id)},
            {'$set': filtered_data}
        )
        return Invoice.get(invoice_id)

class PurchaseOrder:
    collection = db.purchase_orders

    @staticmethod
    def create(po_number: str, issue_date: datetime, items: dict, total_amount: float, status: str) -> dict:
        order = {
            'po_number': po_number,
            'issue_date': issue_date,
            'items': items,
            'total_amount': total_amount,
            'status': status
        }
        result = PurchaseOrder.collection.insert_one(order)
        order['_id'] = str(result.inserted_id)
        return order

    @staticmethod
    def get(po_id: str) -> dict:
        return PurchaseOrder.collection.find_one({'_id': ObjectId(po_id)})

    @staticmethod
    def update(po_id: str, data: dict) -> dict:
        data['updated_at'] = datetime.utcnow()
        PurchaseOrder.collection.update_one(
            {'_id': ObjectId(po_id)},
            {'$set': data}
        )
        return PurchaseOrder.get(po_id)

class ReconciliationResult:
    collection = db.reconciliation_results

    @staticmethod
    def create(invoice_id: str, po_id: str, status: str, discrepancies: dict, ai_notes: str) -> dict:
        result = {
            'invoice_id': invoice_id,
            'po_id': po_id,
            'status': status,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'discrepancies': discrepancies,
            'ai_notes': ai_notes
        }
        result = ReconciliationResult.collection.insert_one(result)
        result['_id'] = str(result.inserted_id)
        return result

    @staticmethod
    def get(result_id: str) -> dict:
        return ReconciliationResult.collection.find_one({'_id': ObjectId(result_id)})

    @staticmethod
    def update(result_id: str, data: dict) -> dict:
        data['updated_at'] = datetime.utcnow()
        ReconciliationResult.collection.update_one(
            {'_id': ObjectId(result_id)},
            {'$set': data}
        )
        return ReconciliationResult.get(result_id)

class Report:
    collection = db.reports

    @staticmethod
    def create(invoice_id: str, processing_status: str, ocr_confidence: float, validation_results: dict) -> dict:
        report = {
            'invoice_id': invoice_id,
            'created_at': datetime.utcnow(),
            'processing_status': processing_status,
            'ocr_confidence': ocr_confidence,
            'processing_time': 0.0,  # Can be calculated
            'validation_results': validation_results,
            'error_logs': []
        }
        result = Report.collection.insert_one(report)
        report['_id'] = str(result.inserted_id)
        return report

    @staticmethod
    def get_by_invoice(invoice_id: str) -> list:
        return list(Report.collection.find({'invoice_id': invoice_id})) 