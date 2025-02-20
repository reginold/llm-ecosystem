export interface Invoice {
  id: number;
  file_path: string;
  upload_date: string;
  status: string;
  extracted_data: any;
}

export interface PurchaseOrder {
  id: number;
  po_number: string;
  items: any;
  total_amount: number;
}

export interface ReconciliationResult {
  id: number;
  invoice_id: number;
  po_id: number;
  status: string;
  discrepancies: any;
  ai_notes: string;
} 