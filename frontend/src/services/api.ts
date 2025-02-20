import axios from 'axios';
import { Invoice } from '../types';

const API_BASE_URL = 'http://localhost:5000/api';

interface UploadResponse {
  success: boolean;
  invoice: Invoice;
  message: string;
  task_id: string;
}

export const uploadInvoice = async (file: File): Promise<UploadResponse> => {
  try {
    const formData = new FormData();
    formData.append('invoice_file', file);
    
    const response = await axios.post<UploadResponse>(`${API_BASE_URL}/upload-invoice`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total!);
        console.log('Upload Progress:', percentCompleted);
      },
    });
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.message || 'Error uploading invoice');
    }
    throw error;
  }
};

export const getReconciliationResults = async (invoiceId: string) => {
  const response = await axios.get(`${API_BASE_URL}/results/${invoiceId}`);
  return response.data;
}; 