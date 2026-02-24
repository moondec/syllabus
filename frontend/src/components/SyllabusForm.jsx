import React, { useState } from 'react';
import { Info, Sparkles, Loader2 } from 'lucide-react';
import MultiSelectDropdown from './MultiSelectDropdown';
import { aiGenerate } from '../services/apiService';

const fields = [
    { key: 'nazwa_przedmiotu', label: 'Nazwa przedmiotu', desc: 'Pełna nazwa kursu/modułu (PL)', type: 'text' },
    { key: 'ects', label: 'Punkty ECTS', desc: 'Liczba punktów ECTS', type: 'text' },
    { key: 'nazwa_angielska', label: 'Nazwa w j. angielskim', desc: 'Tłumaczenie nazwy przedmiotu (EN)', type: 'text', ai: true },
    { key: 'jednostka', label: 'Jednostka realizująca', desc: 'Katedra lub wydział', type: 'text' },
    { key: 'kierownik', label: 'Kierownik przedmiotu', desc: 'Tytuł i nazwisko prowadzącego', type: 'text' },
    { key: 'kierunek', label: 'Kierunek studiów', desc: 'Sprecyzowany kierunek studiów', type: 'text' },
    { key: 'poziom', label: 'Poziom kształcenia', desc: 'np. Studia I lub II stopnia', type: 'text' },
    { key: 'profil', label: 'Profil kształcenia', desc: 'np. ogólnoakademicki / praktyczny', type: 'text' },
    { key: 'semestr', label: 'Semestr', desc: 'Numer semestru realizacji kursu', type: 'text' },
    { key: 'zakres', label: 'Zakres / Specjalizacja', desc: 'W zakresie / Moduł kształcenia / Specjalizacja', type: 'text' },
    { key: 'forma', label: 'Forma studiów', desc: 'np. stacjonarne / niestacjonarne', type: 'text' },

    // Description fields (AI-powered)
    { key: 'cel_przedmiotu', label: 'Cel przedmiotu', desc: 'Główne cele kształcenia', type: 'textarea', ai: true },
    { key: 'metody_dydaktyczne', label: 'Metody dydaktyczne', desc: 'Sposoby prowadzenia zajęć', type: 'textarea', ai: true },
    { key: 'wiedza', label: 'Wiedza (Opisowo)', desc: 'Opis zdobytych kwalifikacji w zakresie wiedzy', type: 'textarea', ai: true },
    { key: 'umiejetnosci', label: 'Umiejętności (Opisowo)', desc: 'Opis zdobytych kwalifikacji w zakresie umiejętności', type: 'textarea', ai: true },
    { key: 'kompetencje', label: 'Kompetencje społeczne (Opisowo)', desc: 'Opis zdobytych kwalifikacji w zakresie kompetencji', type: 'textarea', ai: true },

    // Learning outcomes (Symbols)
    { key: 'learning_outcomesW', label: 'Symbole: WIEDZA', desc: 'Kierunkowe efekty uczenia się (W)', type: 'multi-select', category: 'W' },
    { key: 'learning_outcomesU', label: 'Symbole: UMIEJĘTNOŚCI', desc: 'Kierunkowe efekty uczenia się (U)', type: 'multi-select', category: 'U' },
    { key: 'learning_outcomesK', label: 'Symbole: KOMPETENCJE', desc: 'Kierunkowe efekty uczenia się (K)', type: 'multi-select', category: 'K' },

    { key: 'metody_weryfikacji', label: 'Sposoby weryfikacji', desc: 'Metody weryfikacji efektów uczenia się', type: 'textarea', ai: true },
    { key: 'kursSym', label: 'Symbole przedmiotowe', desc: 'Dopasowanie symboli do treści programowych', type: 'textarea', ai: true },
    { key: 'tresci', label: 'Treści programowe', desc: 'Opis wykładów, ćwiczeń, laboratoriów itd.', type: 'textarea', ai: true },

    { key: 'formy_zaliczenia', label: 'Formy zaliczenia', desc: 'Opis egzaminów, zaliczeń itd.', type: 'textarea' },
    { key: 'procOcena', label: 'Udział w ocenie końcowej (%)', desc: 'Procentowy udział poszczególnych form zaliczenia', type: 'text' },
    { key: 'literatura', label: 'Literatura', desc: 'Literatura podstawowa i uzupełniająca', type: 'textarea' }
];

export default function SyllabusForm({ data, onChange, providerConfig, language = 'pl' }) {
    const [aiLoading, setAiLoading] = useState({});

    const handleChange = (field, value) => {
        onChange(prev => ({ ...prev, [field]: value }));
    };

    const handleAIGenerate = async (fieldKey) => {
        try {
            setAiLoading(prev => ({ ...prev, [fieldKey]: true }));

            // Build context info for the LLM based on what's available
            const contextInfo = {
                tresci: data.tresci || '',
                kierunek: data.kierunek || '',
                poziom: data.poziom || '',
                cel_przedmiotu: data.cel_przedmiotu || ''
            };

            // For outcomes fields, provide descriptions of selected symbols
            if (['wiedza', 'umiejetnosci', 'kompetencje'].includes(fieldKey)) {
                let categoryMap = { 'wiedza': 'W', 'umiejetnosci': 'U', 'kompetencje': 'K' };
                let cat = categoryMap[fieldKey];
                let selectedSymbolsStr = data[`learning_outcomes${cat}`] || '';
                let selectedSymbols = selectedSymbolsStr.split(',').map(s => s.trim()).filter(Boolean);

                let availableForCat = (data.available_outcomes && data.available_outcomes[cat]) || [];
                let symbolsInfo = availableForCat.filter(s => selectedSymbols.includes(s.symbol));

                contextInfo.symbols_info = symbolsInfo;
            }

            const fieldValue = data[fieldKey] || '';
            const generatedText = await aiGenerate(data.nazwa_przedmiotu, fieldKey, contextInfo, providerConfig, language, fieldValue);

            // Set generated text to the field
            handleChange(fieldKey, generatedText);

        } catch (error) {
            let msg = error.message || 'Wystąpił błąd podczas generowania tekstu.';
            if (msg.includes('Brak klucza API')) {
                msg = "Brak klucza API do modelu LLM. Kliknij przycisk 'Ustawienia AI' na górze strony, aby go wprowadzić.";
            }
            alert(msg);
        } finally {
            setAiLoading(prev => ({ ...prev, [fieldKey]: false }));
        }
    };

    return (
        <div className="space-y-6">
            {/* Sekcja referencyjna - Podpowiedzi z dokumentu */}
            {(data.ref_kierunkowe || data.ref_weryfikacja) && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-6 space-y-4 shadow-sm">
                    <h4 className="font-bold text-amber-800 flex items-center gap-2">
                        <Info className="w-5 h-5" />
                        Informacje pomocnicze z programu studiów
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {data.ref_kierunkowe && (
                            <div className="bg-white/50 rounded-lg p-3 border border-amber-100">
                                <h5 className="text-xs font-bold text-amber-900 uppercase mb-2">Kierunkowe efekty uczenia się:</h5>
                                <div className="text-xs text-slate-700 max-h-40 overflow-y-auto whitespace-pre-wrap">
                                    {data.ref_kierunkowe}
                                </div>
                            </div>
                        )}
                        {data.ref_weryfikacja && (
                            <div className="bg-white/50 rounded-lg p-3 border border-amber-100">
                                <h5 className="text-xs font-bold text-amber-900 uppercase mb-2">Sposoby weryfikacji:</h5>
                                <div className="text-xs text-slate-700 max-h-40 overflow-y-auto whitespace-pre-wrap">
                                    {data.ref_weryfikacja}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Sekcja godzinowa */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="bg-emerald-50/50 border-b border-slate-200 px-6 py-4 flex items-center justify-between">
                    <h3 className="font-semibold text-slate-800">Wymiar godzinowy</h3>
                    <span className="text-xs font-medium text-emerald-600 bg-emerald-100 px-2 py-1 rounded-full uppercase tracking-wider">
                        Plan studiów
                    </span>
                </div>
                <div className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Stacjonarne */}
                        <div>
                            <h4 className="text-sm font-bold text-slate-700 mb-3 uppercase tracking-wide">Stacjonarne</h4>
                            <div className="space-y-2">
                                {[
                                    { key: 'numWS', label: 'Wykłady' },
                                    { key: 'numCS', label: 'Ćwiczenia' },
                                    { key: 'numPS', label: 'Zajęcia terenowe' },
                                    { key: 'numLS', label: 'Laboratoria' },
                                    { key: 'numKS', label: 'Konsultacje' },
                                    { key: 'numPwS', label: 'Praca własna' },
                                    { key: 'numInS', label: 'Inne zajęcia' },
                                    { key: 'numTS', label: 'ŁĄCZNIE', bold: true },
                                ].map(h => (
                                    <div key={h.key} className="flex items-center gap-3">
                                        <label className={`text-sm ${h.bold ? 'font-bold text-slate-800' : 'text-slate-600'} w-32 flex-shrink-0`}>{h.label}</label>
                                        <input
                                            type="text"
                                            value={data[h.key] || ''}
                                            onChange={(e) => handleChange(h.key, e.target.value)}
                                            className={`w-20 text-center bg-slate-50 border border-slate-200 rounded-md px-2 py-1.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 ${h.bold ? 'font-bold bg-emerald-50 border-emerald-200' : ''}`}
                                        />
                                    </div>
                                ))}
                            </div>
                        </div>
                        {/* Niestacjonarne */}
                        <div>
                            <h4 className="text-sm font-bold text-slate-700 mb-3 uppercase tracking-wide">Niestacjonarne</h4>
                            <div className="space-y-2">
                                {[
                                    { key: 'numWNS', label: 'Wykłady' },
                                    { key: 'numCNS', label: 'Ćwiczenia' },
                                    { key: 'numPNS', label: 'Zajęcia terenowe' },
                                    { key: 'numLNS', label: 'Laboratoria' },
                                    { key: 'numKNS', label: 'Konsultacje' },
                                    { key: 'numPwNS', label: 'Praca własna' },
                                    { key: 'numInNS', label: 'Inne zajęcia' },
                                    { key: 'numTNS', label: 'ŁĄCZNIE', bold: true },
                                ].map(h => (
                                    <div key={h.key} className="flex items-center gap-3">
                                        <label className={`text-sm ${h.bold ? 'font-bold text-slate-800' : 'text-slate-600'} w-32 flex-shrink-0`}>{h.label}</label>
                                        <input
                                            type="text"
                                            value={data[h.key] || ''}
                                            onChange={(e) => handleChange(h.key, e.target.value)}
                                            className={`w-20 text-center bg-slate-50 border border-slate-200 rounded-md px-2 py-1.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 ${h.bold ? 'font-bold bg-emerald-50 border-emerald-200' : ''}`}
                                        />
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="bg-indigo-50/50 border-b border-slate-200 px-6 py-4 flex items-center justify-between">
                    <h3 className="font-semibold text-slate-800">Edytor Sylabusa</h3>
                    <span className="text-xs font-medium text-indigo-600 bg-indigo-100 px-2 py-1 rounded-full uppercase tracking-wider">
                        Tryb Ręczny
                    </span>
                </div>

                <div className="p-6 md:p-8 space-y-8">
                    {fields.map((f) => (
                        <div key={f.key} className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start border-b border-slate-100 pb-8 last:border-0 last:pb-0">
                            <div className="md:col-span-4 lg:col-span-3">
                                <label className="block text-sm font-semibold text-slate-700 mb-1">
                                    {f.key === 'nazwa_przedmiotu' ? (language === 'en' ? 'Nazwa w j. angielskim' : 'Nazwa przedmiotu') :
                                        f.key === 'nazwa_angielska' ? (language === 'en' ? 'Nazwa w j. polskim' : 'Nazwa w j. angielskim') :
                                            f.label}
                                </label>
                                <p className="text-xs text-slate-500 italic">{f.desc}</p>
                            </div>
                            <div className="md:col-span-8 lg:col-span-9 relative">
                                {f.type === 'textarea' ? (
                                    <div className="relative">
                                        <textarea
                                            value={data[f.key] || ''}
                                            onChange={(e) => handleChange(f.key, e.target.value)}
                                            placeholder={f.base_value || ''}
                                            rows={5}
                                            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-shadow resize-y disabled:opacity-70 disabled:bg-slate-100"
                                            disabled={aiLoading[f.key]}
                                        />
                                        {f.ai && (
                                            <button
                                                type="button"
                                                onClick={() => handleAIGenerate(f.key)}
                                                disabled={aiLoading[f.key]}
                                                className="absolute right-3 bottom-3 bg-gradient-to-r from-violet-600 to-indigo-600 text-white p-2 rounded-lg shadow hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed group flex items-center justify-center"
                                                title="Wygeneruj propozycję za pomocą AI"
                                            >
                                                {aiLoading[f.key] ? (
                                                    <Loader2 className="w-5 h-5 animate-spin" />
                                                ) : (
                                                    <Sparkles className="w-5 h-5 group-hover:scale-110 transition-transform" />
                                                )}
                                            </button>
                                        )}
                                    </div>
                                ) : f.type === 'multi-select' ? (
                                    <MultiSelectDropdown
                                        selected={data[f.key] || ''}
                                        options={data.available_outcomes ? data.available_outcomes[f.category] : []}
                                        onChange={(val) => handleChange(f.key, val)}
                                        label={f.label}
                                    />
                                ) : (
                                            <div className="relative">
                                                <input
                                                    type="text"
                                                    value={data[f.key] || ''}
                                                    onChange={(e) => handleChange(f.key, e.target.value)}
                                                    placeholder={f.placeholder || ''}
                                                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-shadow"
                                                />
                                                {f.ai && (
                                                    <button
                                                        type="button"
                                                        onClick={() => handleAIGenerate(f.key)}
                                                        disabled={aiLoading[f.key]}
                                                        className="absolute right-2 top-1/2 -translate-y-1/2 bg-indigo-100 text-indigo-600 p-1.5 rounded-md hover:bg-indigo-200 transition-colors disabled:opacity-50"
                                                        title="Przetłumacz / Generuj za pomocą AI"
                                                    >
                                                        {aiLoading[f.key] ? (
                                                            <Loader2 className="w-4 h-4 animate-spin" />
                                                        ) : (
                                                            <Sparkles className="w-4 h-4" />
                                                        )}
                                                    </button>
                                                )}
                                            </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
