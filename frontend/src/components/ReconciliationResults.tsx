import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import { getReconciliationResults } from '../services/api';
import { ReconciliationResult } from '../types';

const ReconciliationResults: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  
  const { data, isLoading, error } = useQuery<ReconciliationResult>(
    ['results', taskId],
    () => getReconciliationResults(taskId!)
  );

  if (isLoading) return <div>Loading results...</div>;
  if (error) return <div>Error loading results</div>;
  if (!data) return <div>No results found</div>;

  const { discrepancies, extracted_data } = data;

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Invoice Analysis Results</h2>
      
      <div className="bg-white shadow rounded-lg p-6">
        <div className="grid grid-cols-2 gap-6">
          {/* Left column: Extracted Data */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Extracted Information</h3>
            <pre className="bg-gray-50 p-4 rounded overflow-auto">
              {extracted_data ? JSON.stringify(JSON.parse(extracted_data), null, 2) : 'No data available'}
            </pre>
          </div>

          {/* Right column: Discrepancies and Analysis */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Processing Details</h3>
            {discrepancies ? (
              <div className="space-y-4">
                <div className="bg-gray-50 p-4 rounded">
                  <p className="font-medium">Source Type</p>
                  <p className="text-sm text-gray-600">{discrepancies.source_type}</p>
                </div>
                
                <div className="bg-gray-50 p-4 rounded">
                  <p className="font-medium">OCR Confidence</p>
                  <div className={`text-sm ${
                    discrepancies.ocr_confidence === 'high' 
                      ? 'text-green-600' 
                      : 'text-yellow-600'
                  }`}>
                    {discrepancies.ocr_confidence.toUpperCase()}
                  </div>
                </div>

                <div className="bg-gray-50 p-4 rounded">
                  <p className="font-medium">Extracted Text Sample</p>
                  <p className="text-sm text-gray-600 mt-2">
                    {discrepancies.extracted_text}
                  </p>
                </div>

                <div className="bg-gray-50 p-4 rounded">
                  <p className="font-medium">Analysis Result</p>
                  <pre className="text-sm text-gray-600 mt-2 overflow-auto">
                    {discrepancies.analysis_result}
                  </pre>
                </div>
              </div>
            ) : (
              <div>No processing details available</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReconciliationResults; 