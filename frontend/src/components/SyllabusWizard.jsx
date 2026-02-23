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

                                {(() => {
                                    // Group and sort subjects
                                    const grouped = extractedSubjects.reduce((acc, subj) => {
                                        let level = subj.poziom || 'Nieokreślony poziom studiów';
                                        // Capitalize first letter of level
                                        level = level.charAt(0).toUpperCase() + level.slice(1);
                                        if (!acc[level]) acc[level] = [];
                                        acc[level].push(subj);
                                        return acc;
                                    }, {});

                                    const parsePrefix = (name) => {
                                        if (!name || typeof name !== 'string') return [999, 999];
                                        const match = name.match(/^(\d+)\.(\d+)\.?/);
                                        if (match) return [parseInt(match[1], 10), parseInt(match[2], 10)];
                                        return [999, 999]; // fallback
                                    };

                                    Object.keys(grouped).forEach(level => {
                                        grouped[level].sort((a, b) => {
                                            const nameA = a.nazwa_przedmiotu || '';
                                            const nameB = b.nazwa_przedmiotu || '';
                                            const [a1, a2] = parsePrefix(nameA);
                                            const [b1, b2] = parsePrefix(nameB);
                                            if (a1 !== b1) return a1 - b1;
                                            if (a2 !== b2) return a2 - b2;
                                            return nameA.localeCompare(nameB);
                                        });
                                    });

                                    return Object.entries(grouped).map(([level, subjects]) => {
                                        const levelLower = level.toLowerCase();
                                        let theme = {
                                            bg: "bg-white",
                                            border: "border-slate-200",
                                            hoverBorder: "hover:border-indigo-400",
                                            hoverShadow: "hover:shadow-indigo-500/10",
                                            badgeBg: "bg-indigo-100",
                                            badgeText: "text-indigo-700",
                                            borderBottom: "border-indigo-100",
                                            subjectHoverText: "group-hover:text-indigo-600"
                                        };

                                        if (levelLower.includes("pierwszego")) {
                                            theme = {
                                                bg: "bg-emerald-50/50",
                                                border: "border-emerald-200/60",
                                                hoverBorder: "hover:border-emerald-400",
                                                hoverShadow: "hover:shadow-emerald-500/20",
                                                badgeBg: "bg-emerald-100",
                                                badgeText: "text-emerald-700",
                                                borderBottom: "border-emerald-100",
                                                subjectHoverText: "group-hover:text-emerald-600"
                                            };
                                        } else if (levelLower.includes("drugiego")) {
                                            theme = {
                                                bg: "bg-blue-50/50",
                                                border: "border-blue-200/60",
                                                hoverBorder: "hover:border-blue-400",
                                                hoverShadow: "hover:shadow-blue-500/20",
                                                badgeBg: "bg-blue-100",
                                                badgeText: "text-blue-700",
                                                borderBottom: "border-blue-100",
                                                subjectHoverText: "group-hover:text-blue-600"
                                            };
                                        }

                                        return (
                                            <div key={level} className="mb-10 animate-in fade-in slide-in-from-bottom-2">
                                                <div className={`flex items-center gap-3 mb-5 border-b pb-3 ${theme.borderBottom}`}>
                                                    <div className={`${theme.badgeBg} ${theme.badgeText} px-3 py-1 rounded-md text-sm font-semibold inline-flex items-center`}>
                                                        Studia
                                                    </div>
                                                    <h3 className="text-xl font-bold text-slate-800">{level}</h3>
                                                    <span className="text-sm font-medium text-slate-400 ml-auto bg-slate-100 px-2 py-1 rounded-lg">
                                                        {subjects.length} przedmiotów
                                                    </span>
                                                </div>

                                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                                    {subjects.map((subj, index) => (
                                                        <div
                                                            onClick={() => handleSelectSubject(subj)}
                                                            key={`${level}-${index}`}
                                                            className={`group p-5 rounded-xl border transition-all flex flex-col justify-between cursor-pointer ${theme.bg} ${theme.border} ${theme.hoverBorder} hover:shadow-md ${theme.hoverShadow}`}
                                                        >
                                                            <div>
                                                                <h3 className={`font-semibold text-slate-800 line-clamp-2 leading-tight transition-colors ${theme.subjectHoverText}`}>
                                                                    {subj.nazwa_przedmiotu || 'Przedmiot bez nazwy'}
                                                                </h3>
                                                                <p className="text-sm text-slate-500 mt-2 line-clamp-1">
                                                                    {subj.kierunek ? `Kierunek: ${subj.kierunek}` : 'Brak danych o kierunku'}
                                                                </p>
                                                            </div>
                                                            <div className="mt-4 pt-4 border-t border-slate-200/50 flex items-center justify-between text-sm">
                                                                <span className="font-medium text-slate-600">Semestr: {subj.semestr || '-'}</span>
                                                                <span className="bg-white/60 border border-slate-200/50 text-slate-700 font-medium px-2 py-1 rounded-md">
                                                                    ECTS: {subj.ects || '-'}
                                                                </span>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        );
                                    });
                                })()}
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
