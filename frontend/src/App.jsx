import React, { useState, useEffect } from 'react';
import { FileUp, FileText } from 'lucide-react';
import axios from 'axios';
import SyllabusWizard from './components/SyllabusWizard';
import ErrorBoundary from './components/ErrorBoundary';

const FRONTEND_VERSION = "1.1.0";

function App() {
  const [backendVersion, setBackendVersion] = useState('');

  useEffect(() => {
    axios.get('/api/version')
      .then(response => {
        if (response.data && response.data.version) {
          setBackendVersion(response.data.version);
        }
      })
      .catch(err => {
        console.error("Failed to fetch backend version", err);
        setBackendVersion('Błąd');
      });
  }, []);
  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800 font-sans selection:bg-indigo-100 selection:text-indigo-900">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-indigo-600 p-2 rounded-lg">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-violet-600">
              Kreator Sylabusów
            </h1>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        <ErrorBoundary>
          <SyllabusWizard />
        </ErrorBoundary>
      </main>

      <footer className="py-4 text-center text-xs text-slate-400 bg-white border-t border-slate-200">
        <div className="flex justify-center gap-4">
          <span>Frontend: v{FRONTEND_VERSION}</span>
          <span>Backend: {backendVersion ? `v${backendVersion}` : 'łączenie...'}</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
