from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    file_path = db.Column(db.String(255))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50))  # PENDING, PROCESSING, COMPLETED, FAILED
    error_message = db.Column(db.Text, nullable=True)
    extracted_data = db.Column(db.JSON, nullable=True)
    
    reconciliation_result = db.relationship('ReconciliationResult', backref='invoice', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'upload_date': self.upload_date.isoformat(),
            'status': self.status,
            'error_message': self.error_message,
            'extracted_data': self.extracted_data
        }

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(50), unique=True)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.Column(db.JSON)
    total_amount = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id,
            'po_number': self.po_number,
            'issue_date': self.issue_date.isoformat(),
            'items': self.items,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'status': self.status
        }

class ReconciliationResult(db.Model):
    __tablename__ = 'reconciliation_results'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=True)
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    discrepancies = db.Column(db.JSON, nullable=True)
    ai_notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'po_id': self.po_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'discrepancies': self.discrepancies,
            'ai_notes': self.ai_notes
        } 