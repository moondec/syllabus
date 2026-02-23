import React, { useState } from 'react';
import FileUploader from './FileUploader';
import SyllabusForm from './SyllabusForm';
import { processDocument, generateSyllabus } from '../services/apiService';
import { Loader2, Download, AlertCircle, ChevronRight, List, ArrowLeft } from 'lucide-react';

export default function SyllabusWizard() {
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [extractedSubjects, setExtractedSubjects] = useState([]); // Array z API po ekstrakcji wielu subjectow
    const [syllabusData, setSyllabusData] = useState(null); // Obecnie edytowany pojedynczy sylabus

    const handleFileUpload = async (file) => {
        setLoading(true);
        setError(null);
        try {
            const data = await processDocument(file);
            // Backend zwraca listę przedmiotów lub ew. jeden obiekt, zróbmy fallback do tablicy
            const subjectsArray = Array.isArray(data) ? data : [data];
            setExtractedSubjects(subjectsArray);

            if (subjectsArray.length === 1) {
                // Jesli jest tylko jeden przedmiot, od razu przeskocz do jego edycji
                setSyllabusData(subjectsArray[0] || { nazwa_przedmiotu: '', ects: '' });
                setStep(3);
            } else {
                // Jeśli więcej, daj wybór użykownikowi
                setStep(2);
            }

        } catch (err) {
            setError(err.message || 'Wystąpił błąd podczas analizy pliku');
        } finally {
            setLoading(false);
        }
    };

    const handleSelectSubject = (subject) => {
        setSyllabusData(subject);
        setStep(3);
    };

    const handleGenerateDocument = async () => {
        setLoading(true);
        setError(null);
        try {
            await generateSyllabus(syllabusData, 'docx');
            setStep(4);
        } catch (err) {
            setError(err.message || 'Wystąpił błąd podczas generowania dokumentu');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
            {/* PROGRESS BAR */}
            <div className="bg-slate-50 border-b border-slate-200 px-6 py-4 flex flex-wrap gap-2 md:gap-4 text-xs md:text-sm font-medium text-slate-500">
                <span className={step >= 1 ? "text-indigo-600" : ""}>1. Wgraj program</span>
                <ChevronRight className="w-4 h-4 md:w-5 md:h-5 text-slate-300" />
                <span className={step >= 2 ? "text-indigo-600" : ""}>2. Wybierz przedmiot</span>
                <ChevronRight className="w-4 h-4 md:w-5 md:h-5 text-slate-300" />
                <span className={step >= 3 ? "text-indigo-600" : ""}>3. Weryfikuj tabelę</span>
                <ChevronRight className="w-4 h-4 md:w-5 md:h-5 text-slate-300" />
                <span className={step >= 4 ? "text-indigo-600" : ""}>4. Zapisz Sylabus</span>
            </div>

            <div className="p-4 md:p-8">
                {error && (
                    <div className="mb-6 bg-red-50 text-red-700 p-4 rounded-lg flex gap-3 items-start border border-red-200 animate-in fade-in">
                        <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                        <p>{error}</p>
                    </div>
                )}

                {step === 1 && (
                    <div className="max-w-xl mx-auto py-8">
                        <div className="text-center mb-8">
                            <h2 className="text-2xl font-bold text-slate-800 mb-2">Rozpocznij tworzenie sylabusa</h2>
                            <p className="text-slate-500">Wgraj plik z programem studiów (.docx lub .pdf), a my postaramy się wyciągnąć z niego potrzebne informacje do tabeli.</p>
                        </div>
                        {loading ? (
                            <div className="flex flex-col items-center justify-center p-12 bg-indigo-50 rounded-xl border-2 border-dashed border-indigo-200">
                                <Loader2 className="w-8 h-8 text-indigo-600 animate-spin mb-4" />
                                <p className="text-indigo-900 font-medium">Analizuję dokument...</p>
                                <p className="text-indigo-700/70 text-sm mt-1">To może potrwać kilka sekund</p>
                            </div>
                        ) : (
                            <FileUploader onFileSelect={handleFileUpload} />
                        )}
                    </div>
                )}

                {step === 2 && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-4xl mx-auto py-4">
                        {extractedSubjects.length > 0 ? (
                            <>
                                <div className="mb-8">
                                    <h2 className="text-2xl font-bold text-slate-800">Znaleziono wiele przedmiotów</h2>
                                    <p className="text-slate-500 mt-1">Z twojego pliku wyodrębniono {extractedSubjects.length} pozycji. Wybierz ten, dla którego chcesz przygotować gotowy dokument (kartę przedmiotu).</p>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {extractedSubjects.map((subj, index) => (
                                        <div
                                            onClick={() => handleSelectSubject(subj)}
                                            key={index}
                                            className="group p-5 rounded-xl border border-slate-200 bg-white hover:border-indigo-300 hover:shadow-md hover:shadow-indigo-500/10 cursor-pointer transition-all flex flex-col justify-between"
                                        >
                                            <div>
                                                <h3 className="font-semibold text-slate-800 line-clamp-2 leading-tight group-hover:text-indigo-600 transition-colors">{subj.nazwa_przedmiotu || 'Przedmiot bez nazwy'}</h3>
                                                <p className="text-sm text-slate-500 mt-2 line-clamp-1">{subj.kierunek ? `Kierunek: ${subj.kierunek}` : 'Brak danych o kierunku'}</p>
                                            </div>
                                            <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between text-sm">
                                                <span className="font-medium text-slate-600">Semestr: {subj.semestr || '-'}</span>
                                                <span className="bg-slate-100 text-slate-700 font-medium px-2 py-1 rounded-md">ECTS: {subj.ects || '-'}</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </>
                        ) : (
                            <div className="text-center py-12">
                                <div className="w-16 h-16 bg-amber-100 text-amber-600 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <AlertCircle className="w-8 h-8" />
                                </div>
                                <h2 className="text-2xl font-bold text-slate-800 mb-2">Nie wykryto tabeli przedmiotów</h2>
                                <p className="text-slate-500 mb-6 max-w-lg mx-auto">Format dokumentu różni się od obsługiwanego, stąd nie byliśmy w stanie automatycznie wyciągnąć danych. Możesz wypełnić dokument ręcznie.</p>
                                <button
                                    onClick={() => handleSelectSubject({ nazwa_przedmiotu: '', ects: '' })}
                                    className="bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-600/20 rounded-xl px-8 py-3 font-medium transition-all"
                                >
                                    Przejdź do ręcznego uzupełniania
                                </button>
                            </div>
                        )}
                    </div>
                )}

                {step === 3 && syllabusData && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                            <div className="flex items-center gap-3">
                                {extractedSubjects.length > 1 && (
                                    <button
                                        onClick={() => setStep(2)}
                                        className="text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 p-2 rounded-lg transition-colors"
                                        title="Wróć do listy przedmiotów"
                                    >
                                        <ArrowLeft className="w-5 h-5" />
                                    </button>
                                )}
                                <div>
                                    <h2 className="text-2xl font-bold text-slate-800">Weryfikacja Danych</h2>
                                    <p className="text-slate-500">Sprawdź pobrane informacje i uzupełnij brakujące pola w formularzu wybranego przedmiotu.</p>
                                </div>
                            </div>
                            <button
                                onClick={handleGenerateDocument}
                                disabled={loading}
                                className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-xl font-medium flex items-center gap-2 transition-colors disabled:opacity-50"
                            >
                                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Download className="w-5 h-5" />}
                                Eksportuj DOCX
                            </button>
                        </div>

                        <SyllabusForm data={syllabusData} onChange={setSyllabusData} />
                    </div>
                )}

                {step === 4 && (
                    <div className="text-center py-16 animate-in zoom-in duration-500">
                        <div className="w-20 h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
                            <Download className="w-10 h-10" />
                        </div>
                        <h2 className="text-3xl font-bold text-slate-800 mb-4">Twój sylabus jest gotowy!</h2>
                        <p className="text-slate-500 mb-8 max-w-md mx-auto">Pobieranie dokumentu `.docx` powinno się rozpocząć automatycznie. Jeśli chcesz, możesz utworzyć kolejny.</p>
                        <button
                            onClick={() => { setStep(1); setSyllabusData(null); setExtractedSubjects([]); }}
                            className="bg-slate-100 hover:bg-slate-200 text-slate-800 px-6 py-3 rounded-xl font-semibold transition-colors"
                        >
                            Utwórz nowy sylabus
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
