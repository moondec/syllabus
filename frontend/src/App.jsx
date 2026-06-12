import React, { useState, useEffect } from 'react';
import { FileUp, FileText } from 'lucide-react';
import axios from 'axios';
import SyllabusWizard from './components/SyllabusWizard';
import ErrorBoundary from './components/ErrorBoundary';

const FRONTEND_VERSION = "1.3.0";

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
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800 font-sans selection:bg-green-100 selection:text-green-900">
      <header className="bg-green-800 border-b border-green-900 sticky top-0 z-10 shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <img src="https://up.poznan.pl/sites/default/files/2024-10/logo_biale_polskie_uklad_poziomy.png" alt="UPP Logo" className="h-10" />
            <h1 className="text-xl font-bold text-white border-l border-green-600 pl-4">
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

      <footer className="py-4 text-center text-xs text-slate-500 bg-white border-t border-slate-200">
        <div className="flex flex-col sm:flex-row justify-center items-center gap-2 sm:gap-6 mb-2">
          <div className="flex gap-4">
            <span>Frontend: v{FRONTEND_VERSION}</span>
            <span>Backend: {backendVersion ? `v${backendVersion}` : 'łączenie...'}</span>
          </div>
          <span className="hidden sm:inline text-slate-300">|</span>
          <a 
            href="/README.md" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-green-600 hover:text-green-800 transition-colors hover:underline flex items-center gap-1 font-medium"
          >
            Dokumentacja projektu (README)
          </a>
        </div>
        <div className="mt-2">
          Autor: Marek Urbaniak | Kontakt: <a href="mailto:marek.urbaniak@up.poznan.pl" className="text-green-600 hover:underline">marek.urbaniak@up.poznan.pl</a>
        </div>
      </footer>
    </div>
  );
}

export default App;
