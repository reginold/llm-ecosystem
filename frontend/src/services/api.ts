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
    });
    
    console.log('Upload response:', response.data);
    
    if (!response.data.task_id) {
      throw new Error('No task ID received from server');
    }
    
    return response.data;
  } catch (error) {
    console.error('Upload error:', error);
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.message || 'Error uploading invoice');
    }
    throw error;
  }
};

export const getReconciliationResults = async (taskId: string) => {
  console.log('Fetching results for task:', taskId);
  if (!taskId) {
    throw new Error('No task ID provided');
  }
  const response = await axios.get(`${API_BASE_URL}/results/${taskId}`);
  console.log('Results response:', response.data);
  return response.data;
}; 