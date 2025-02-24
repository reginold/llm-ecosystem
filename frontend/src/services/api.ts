// Remove this line since we're not using it
// import { Invoice } from '../types';

// Update this to match the backend URL from docker-compose
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

interface UploadResponse {
  success: boolean;
  message: string;
  invoice_id: string;
  task_id: string;
}

interface SaveInvoiceData {
  invoice_id: string;
  edited_data: {
    'Bill To': string;
    'Emailing Address': string;
    'Invoice Number': string;
    'Invoice Date': string;
    'Invoice Amount': string;
    'Services': Array<{
      Service: string;
      Quantity: string;
      'Unit Price': string;
      Amount: string;
    }>;
  };
}

export const uploadInvoice = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    console.log('Uploading to:', `${API_BASE_URL}/api/upload`); // Note the /api/upload path
    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Upload failed:', response.status, errorText); // Debug log
      throw new Error(`Upload failed: ${response.status} ${errorText}`);
    }

    return response.json();
  } catch (error) {
    console.error('Upload error:', error); // Debug log
    throw error;
  }
};

export const getReconciliationResults = async (taskId: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/results/${taskId}`);
    if (!response.ok) {
      throw new Error('Error getting results');
    }
    return response.json();
  } catch (error) {
    console.error('Results error:', error);
    throw error;
  }
};

export const saveInvoiceData = async (data: SaveInvoiceData): Promise<any> => {
  try {
    console.log('Saving data:', data);
    const response = await fetch(`${API_BASE_URL}/api/invoice/save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Save failed:', response.status, errorText);
      throw new Error(`Save failed: ${response.status} ${errorText}`);
    }

    return response.json();
  } catch (error) {
    console.error('Save error:', error);
    throw error;
  }
}; 