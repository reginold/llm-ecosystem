import React, { useState, useCallback } from 'react';
import { useMutation } from 'react-query';
import { uploadInvoice, getReconciliationResults } from '../services/api';

interface ExtractedData {
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
}

interface ServiceData {
  service: string;
  quantity: string;
  unit_price: string;
  amount: string;
}

const UploadInvoice: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [extractedData, setExtractedData] = useState<ExtractedData | null>(null);
  const [rawResponse, setRawResponse] = useState<any>(null);
  const [isOcrProcessing, setIsOcrProcessing] = useState(false);

  const mutation = useMutation(uploadInvoice, {
    onSuccess: (data) => {
      console.log('Upload successful, full response:', data);
      setIsOcrProcessing(true);
      const pollInterval = setInterval(async () => {
        try {
          const results = await getReconciliationResults(data.task_id);
          if (results.status === 'COMPLETED') {
            setIsOcrProcessing(false);
            setRawResponse(results);
            if (results.extracted_data) {
              console.log("Raw extracted_data:", results.extracted_data);
              console.log("Type of extracted_data:", typeof results.extracted_data);
              
              // Get the nested extracted_data
              const parsedData = results.extracted_data.extracted_data;
              
              console.log("Parsed Data structure:", {
                keys: Object.keys(parsedData),
                billTo: parsedData.bill_to,
                email: parsedData.emailing_address,
                sample: JSON.stringify(parsedData, null, 2)
              });
              
              const formattedData: ExtractedData = {
                'Bill To': parsedData.bill_to || '-',
                'Emailing Address': parsedData.emailing_address || '-',
                'Invoice Number': parsedData.invoice_number || '-',
                'Invoice Date': parsedData.invoice_date || '-',
                'Invoice Amount': parsedData.invoice_amount || '-',
                'Services': (parsedData.services || []).map((service: ServiceData) => ({
                  'Service': service.service,
                  'Quantity': service.quantity,
                  'Unit Price': service.unit_price,
                  'Amount': service.amount
                }))
              };
              
              console.log("Final formatted data:", formattedData);
              setExtractedData(formattedData);
            }
            clearInterval(pollInterval);
          }
        } catch (error) {
          console.error('Error polling for results:', error);
        }
      }, 2000);
    },
    onError: (error: Error) => {
      console.error('Upload error:', error);
      setError(error.message);
      setIsOcrProcessing(false);
    },
  });

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const validateFile = (file: File) => {
    const validTypes = [
      'application/pdf',
      'image/jpeg',
      'image/png',
      'image/jpg',
      'text/plain',
      'text/csv'
    ];
    
    if (!validTypes.includes(file.type)) {
      alert('File type not supported. Please upload a PDF, image (JPG/PNG), or text file.');
      return false;
    }
    
    // Check file size (e.g., 10MB limit)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      alert('File is too large. Maximum size is 10MB.');
      return false;
    }
    
    return true;
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (validateFile(droppedFile)) {
        setFile(droppedFile);
      }
    }
  }, []);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (validateFile(selectedFile)) {
        setFile(selectedFile);
      }
    }
  }, []);

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (file) {
      mutation.mutate(file);
    }
  }, [file, mutation]);

  const renderUploadButton = () => (
    <button
      type="submit"
      disabled={!file || mutation.isLoading}
      className={`px-6 py-2.5 rounded-lg text-white font-medium transition-colors ${
        !file || mutation.isLoading
          ? 'bg-gray-400 cursor-not-allowed'
          : 'bg-blue-600 hover:bg-blue-700'
      }`}
    >
      {mutation.isLoading ? (
        <div className="flex items-center">
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
          Processing...
        </div>
      ) : (
        'Upload and Extract'
      )}
    </button>
  );

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-gray-900">Invoice Processing</h1>
          <p className="mt-2 text-sm text-gray-600">Upload your invoice and verify the extracted information</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <form onSubmit={handleSubmit}>
              <h2 className="text-lg font-medium mb-4">Upload Invoice</h2>
              <div
                className={`border-2 border-dashed rounded-lg p-8 text-center ${
                  dragActive 
                    ? 'border-blue-500 bg-blue-50' 
                    : error 
                      ? 'border-red-300 bg-red-50'
                      : 'border-gray-300 hover:border-gray-400'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <div className="space-y-4">
                  <div className="flex justify-center">
                    <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700">
                      {file ? file.name : 'Drag and drop your invoice here'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      or click to browse from your computer
                    </p>
                  </div>
                  <input
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf,.jpg,.jpeg,.png,.csv,.json"
                    className="hidden"
                    id="file-upload"
                  />
                  <label
                    htmlFor="file-upload"
                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 cursor-pointer"
                  >
                    Browse Files
                  </label>
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="mt-4 rounded-md bg-red-50 p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-red-700">{error}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Move Upload Button to the right */}
              <div className="mt-4 flex justify-end">
                {renderUploadButton()}
              </div>
            </form>
          </div>

          {/* Extracted Data Preview */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-medium mb-4">Extracted Information</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Bill To</label>
                  <div className="mt-1 p-2 bg-gray-50 rounded-md">
                    {extractedData ? extractedData['Bill To'] : '-'}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Emailing Address</label>
                  <div className="mt-1 p-2 bg-gray-50 rounded-md">
                    {extractedData ? extractedData['Emailing Address'] : '-'}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Invoice Number</label>
                  <div className="mt-1 p-2 bg-gray-50 rounded-md">
                    {extractedData ? extractedData['Invoice Number'] : '-'}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Invoice Date</label>
                  <div className="mt-1 p-2 bg-gray-50 rounded-md">
                    {extractedData ? extractedData['Invoice Date'] : '-'}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Invoice Amount</label>
                  <div className="mt-1 p-2 bg-gray-50 rounded-md">
                    {extractedData ? extractedData['Invoice Amount'] : '-'}
                  </div>
                </div>
              </div>

              {/* Services Table */}
              <div className="mt-6">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Services</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Service</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unit Price</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {extractedData?.Services?.map((service, index) => (
                        <tr key={index}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{service.Service}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{service.Quantity}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{service['Unit Price']}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{service.Amount}</td>
                        </tr>
                      )) || (
                        <tr>
                          <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">
                            No services data available
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Update OCR Raw Data Section */}
        <div className="mt-8 bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-medium mb-4">OCR Raw Data</h2>
          <div className="bg-gray-50 rounded-lg p-4">
            <pre className="whitespace-pre-wrap text-sm text-gray-700 overflow-auto max-h-96">
              {isOcrProcessing ? (
                <div className="flex flex-col items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
                  <span className="text-gray-600">OCR Processing in Progress...</span>
                  <span className="text-sm text-gray-500 mt-2">This may take a few moments</span>
                </div>
              ) : rawResponse?.extracted_data ? (
                <div className="space-y-4">
                  {Object.entries(
                    typeof rawResponse.extracted_data === 'string'
                      ? JSON.parse(rawResponse.extracted_data)
                      : rawResponse.extracted_data
                  ).map(([key, value]) => (
                    <div key={key} className="pb-2">
                      <span className="font-medium text-gray-700">{key}:</span>
                      <div className="pl-4 mt-1">
                        {key === 'Services' && Array.isArray(value) ? (
                          <div className="space-y-2">
                            {value.map((service, idx) => (
                              <div key={idx} className="pl-2 border-l-2 border-gray-200">
                                {Object.entries(service).map(([sKey, sValue]) => (
                                  <div key={sKey}>
                                    <span className="text-gray-600">{sKey}:</span>{' '}
                                    <span className="text-gray-900">
                                      {typeof sValue === 'object' 
                                        ? JSON.stringify(sValue, null, 2)
                                        : String(sValue)
                                      }
                                    </span>
                                  </div>
                                ))}
                              </div>
                            ))}
                          </div>
                        ) : typeof value === 'object' ? (
                          <div className="pl-2">
                            {Object.entries(value as object).map(([subKey, subValue]) => (
                              <div key={subKey}>
                                <span className="text-gray-600">{subKey}:</span>{' '}
                                <span className="text-gray-900">
                                  {typeof subValue === 'object'
                                    ? JSON.stringify(subValue, null, 2)
                                    : String(subValue)
                                  }
                                </span>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <span className="text-gray-900">{String(value)}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                'No OCR data available'
              )}
            </pre>
          </div>
        </div>

        {/* Save Button */}
        <div className="mt-6 flex justify-end">
          <button
            type="button"
            onClick={() => {/* Handle confirmation */}}
            disabled={!extractedData || mutation.isLoading}
            className={`px-6 py-2.5 rounded-lg text-white font-medium transition-colors ${
              !extractedData || mutation.isLoading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700'
            }`}
          >
            Save to Database
          </button>
        </div>
      </div>
    </div>
  );
};

export default UploadInvoice; 