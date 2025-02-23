export interface Invoice {
  id: string;
  status: string;
  file_path: string;
  created_at: string;
  extracted_data: any;
  validation_status: string;
  confidence_score: number;
  discrepancies: {
    source_type: string;
    ocr_confidence: string;
    extracted_text: string;
    analysis_result: string;
  };
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
  discrepancies: {
    source_type: string;
    ocr_confidence: string;
    extracted_text: string;
    analysis_result: string;
  };
  extracted_data: string;
  ai_notes: string;
} 