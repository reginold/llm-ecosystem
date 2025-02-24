import React from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import UploadInvoice from './components/UploadInvoice';
import ReconciliationResults from './components/ReconciliationResults';
import Layout from './components/Layout';

const queryClient = new QueryClient();

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<UploadInvoice />} />
            <Route path="/results/:taskId" element={<ReconciliationResults />} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
};

export default App; 