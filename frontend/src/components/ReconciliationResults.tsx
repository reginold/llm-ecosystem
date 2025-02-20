import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import { getReconciliationResults } from '../services/api';
import { ReconciliationResult } from '../types';

const ReconciliationResults: React.FC = () => {
  const { invoiceId } = useParams<{ invoiceId: string }>();
  
  const { data, isLoading, error } = useQuery<ReconciliationResult>(
    ['reconciliation', invoiceId],
    () => getReconciliationResults(invoiceId!)
  );

  if (isLoading) {
    return <div>Loading results...</div>;
  }

  if (error) {
    return <div>Error loading results</div>;
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Reconciliation Results</h2>
      {data && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="mb-4">
            <h3 className="text-lg font-semibold">Status</h3>
            <p className="text-gray-600">{data.status}</p>
          </div>
          <div className="mb-4">
            <h3 className="text-lg font-semibold">Discrepancies</h3>
            <pre className="bg-gray-100 p-4 rounded">
              {JSON.stringify(data.discrepancies, null, 2)}
            </pre>
          </div>
          <div>
            <h3 className="text-lg font-semibold">AI Notes</h3>
            <p className="text-gray-600">{data.ai_notes}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReconciliationResults; 