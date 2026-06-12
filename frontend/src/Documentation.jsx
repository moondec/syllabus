import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';

export default function Documentation() {
  const [content, setContent] = useState('Ładowanie dokumentacji...');

  useEffect(() => {
    fetch('/README.md')
      .then(res => {
        if (!res.ok) throw new Error('Network response was not ok');
        return res.text();
      })
      .then(text => setContent(text))
      .catch(err => {
        console.error("Błąd podczas ładowania dokumentacji:", err);
        setContent('Błąd wczytywania dokumentacji. Upewnij się, że plik README.md jest dostępny.');
      });
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans selection:bg-green-100 selection:text-green-900 flex flex-col">
      <header className="bg-green-800 border-b border-green-900 shadow-md flex-shrink-0">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <img src="https://up.poznan.pl/sites/default/files/2024-10/logo_biale_polskie_uklad_poziomy.png" alt="UPP Logo" className="h-10" />
            <h1 className="text-xl font-bold text-white border-l border-green-600 pl-4 hidden sm:block">
              Instrukcja Kreatora Sylabusów
            </h1>
          </div>
        </div>
      </header>

      <main className="flex-1 w-full max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white p-6 sm:p-10 rounded-xl shadow-sm border border-slate-200">
          <div className="prose prose-slate prose-green max-w-none">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        </div>
      </main>
    </div>
  );
}
