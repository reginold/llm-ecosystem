import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import { getReconciliationResults } from '../services/api';

const ReconciliationResults: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  
  console.log('Current taskId from params:', taskId);
  
  const { data, isLoading, error } = useQuery(
    ['results', taskId],
    () => getReconciliationResults(taskId!),
    {
      refetchInterval: (data) => {
        console.log('Current data status:', data?.status);
        return data?.status === 'PROCESSING' ? 1000 : false;
      },
      enabled: !!taskId,
      retry: 3,
      staleTime: 0,
      cacheTime: 0
    }
  );

  console.log('Current data:', data);

  if (!taskId) {
    return <div>No task ID provided</div>;
  }

  if (isLoading || data?.status === 'PROCESSING') {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Processing your invoice...</p>
          <p className="mt-2 text-sm text-gray-500">Task ID: {taskId}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 text-red-700 rounded-lg">
        Error loading results: {error instanceof Error ? error.message : 'Unknown error'}
      </div>
    );
  }

  if (!data || !data.extracted_data) {
    return (
      <div className="p-6">
        <div className="text-center text-gray-600">
          No results available yet
          <div className="mt-2 text-sm">Task ID: {taskId}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Invoice Analysis Results</h2>
      
      <div className="bg-white shadow rounded-lg p-6">
        <div className="grid grid-cols-2 gap-6">
          {/* Left column: Extracted Data */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Extracted Information</h3>
            <pre className="bg-gray-50 p-4 rounded overflow-auto">
              {data.extracted_data ? (
                typeof data.extracted_data === 'string' 
                  ? JSON.stringify(JSON.parse(data.extracted_data), null, 2)
                  : JSON.stringify(data.extracted_data, null, 2)
              ) : 'Processing...'}
            </pre>
          </div>

          {/* Right column: Discrepancies and Analysis */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Processing Details</h3>
            {data.discrepancies ? (
              <div className="space-y-4">
                <div className="bg-gray-50 p-4 rounded">
                  <p className="font-medium">Source Type</p>
                  <p className="text-sm text-gray-600">{data.discrepancies.source_type}</p>
                </div>
                
                <div className="bg-gray-50 p-4 rounded">
                  <p className="font-medium">OCR Confidence</p>
                  <div className={`text-sm ${
                    data.discrepancies.ocr_confidence === 'high' 
                      ? 'text-green-600' 
                      : 'text-yellow-600'
                  }`}>
                    {data.discrepancies.ocr_confidence.toUpperCase()}
                  </div>
                </div>

                <div className="bg-gray-50 p-4 rounded">
                  <p className="font-medium">Analysis Result</p>
                  <pre className="text-sm text-gray-600 mt-2 overflow-auto">
                    {typeof data.discrepancies.analysis_result === 'string'
                      ? data.discrepancies.analysis_result
                      : JSON.stringify(data.discrepancies.analysis_result, null, 2)
                    }
                  </pre>
                </div>
              </div>
            ) : (
              <div>Processing...</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReconciliationResults; 