import React, { useState, useEffect } from 'react';
import { listSyllabuses, getSyllabus, deleteSyllabus, generateSyllabus } from '../services/apiService';
import { Loader2, Trash2, Edit3, Download, Search, AlertCircle, FileText, Calendar, ArrowLeft } from 'lucide-react';

export default function ArchiveView({ onEditSyllabus, onBack }) {
    const [syllabuses, setSyllabuses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchSyllabuses();
    }, []);

    const fetchSyllabuses = async () => {
        setLoading(true);
        try {
            const data = await listSyllabuses();
            setSyllabuses(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id, e) => {
        e.stopPropagation();
        if (!window.confirm('Czy na pewno chcesz usunąć ten sylabus?')) return;
        
        try {
            await deleteSyllabus(id);
            setSyllabuses(prev => prev.filter(s => s.id !== id));
        } catch (err) {
            alert('Błąd podczas usuwania: ' + err.message);
        }
    };

    const handleEdit = async (id) => {
        try {
            const fullData = await getSyllabus(id);
            // fullData contains the 'data' JSON field plus id, legal_basis etc.
            // We want to pass the nested 'data' but include the database id and legal_basis
            const editData = {
                ...fullData.data,
                id: fullData.id,
                legal_basis: fullData.legal_basis
            };
            onEditSyllabus(editData);
        } catch (err) {
            alert('Błąd podczas pobierania danych: ' + err.message);
        }
    };

    const handleDownload = async (id, e) => {
        e.stopPropagation();
        try {
            const fullData = await getSyllabus(id);
            const language = fullData.data?.language || 'pl';
            await generateSyllabus({ ...fullData.data, language }, 'docx');
        } catch (err) {
            alert('Błąd podczas generowania pliku: ' + err.message);
        }
    };

    const filteredSyllabuses = syllabuses.filter(s => 
        (s.subject_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
        (s.field_of_study || '').toLowerCase().includes(searchTerm.toLowerCase())
    );

    const formatDate = (dateStr) => {
        if (!dateStr) return '-';
        const date = new Date(dateStr);
        return date.toLocaleDateString('pl-PL') + ' ' + date.toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className="animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                <div className="flex items-center gap-3">
                    <button 
                        onClick={onBack}
                        className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                    <div>
                        <h2 className="text-2xl font-bold text-slate-800">Archiwum Sylabusów</h2>
                        <p className="text-sm text-slate-500">List zapisanych i wcześniej edytowanych kart przedmiotów.</p>
                    </div>
                </div>

                <div className="relative max-w-sm w-full">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input 
                        type="text"
                        placeholder="Szukaj przedmiotu lub kierunku..."
                        value={searchTerm}
                        onChange={e => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                    />
                </div>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl flex gap-3 items-center mb-6">
                    <AlertCircle className="w-5 h-5" />
                    <p>{error}</p>
                </div>
            )}

            {loading ? (
                <div className="flex flex-col items-center justify-center py-20">
                    <Loader2 className="w-10 h-10 text-indigo-600 animate-spin mb-4" />
                    <p className="text-slate-500 font-medium">Ładowanie archiwum...</p>
                </div>
            ) : filteredSyllabuses.length === 0 ? (
                <div className="text-center py-20 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200">
                    <div className="w-16 h-16 bg-slate-100 text-slate-400 rounded-full flex items-center justify-center mx-auto mb-4">
                        <FileText className="w-8 h-8" />
                    </div>
                    <h3 className="text-lg font-bold text-slate-700">Brak zapisanych sylabusów</h3>
                    <p className="text-slate-500 max-w-xs mx-auto mt-2">
                        {searchTerm ? 'Nie znaleziono sylabusów pasujących do Twojego wyszukiwania.' : 'Tu pojawią się Twoje zapisane projekty.'}
                    </p>
                    <button 
                        onClick={onBack}
                        className="mt-6 text-indigo-600 font-semibold hover:text-indigo-700 underline underline-offset-4"
                    >
                        Przejdź do kreatora
                    </button>
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-4">
                    {filteredSyllabuses.map(syllabus => (
                        <div 
                            key={syllabus.id}
                            onClick={() => handleEdit(syllabus.id)}
                            className="group bg-white border border-slate-200 rounded-xl p-5 hover:border-indigo-400 hover:shadow-md transition-all cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4"
                        >
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                    <h3 className="text-lg font-bold text-slate-800 truncate group-hover:text-indigo-600 transition-colors">
                                        {syllabus.subject_name || 'Bez nazwy'}
                                    </h3>
                                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-100 text-slate-500">
                                        ID: {syllabus.id}
                                    </span>
                                </div>
                                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-slate-500">
                                    <div className="flex items-center gap-1.5">
                                        <span className="font-medium">{syllabus.field_of_study || 'Brak kierunku'}</span>
                                    </div>
                                    <div className="w-1.5 h-1.5 rounded-full bg-slate-200 hidden md:block"></div>
                                    <div className="flex items-center gap-1.5">
                                        <span>Semestr: {syllabus.semester || '-'}</span>
                                    </div>
                                    <div className="w-1.5 h-1.5 rounded-full bg-slate-200 hidden md:block"></div>
                                    <div className="flex items-center gap-1.5">
                                        <Calendar className="w-3.5 h-3.5" />
                                        <span>{formatDate(syllabus.updated_at)}</span>
                                    </div>
                                </div>
                                <div className="mt-2 text-[10px] text-slate-400 italic truncate max-w-2xl">
                                    {syllabus.legal_basis}
                                </div>
                            </div>

                            <div className="flex items-center gap-2">
                                <button 
                                    onClick={(e) => handleDownload(syllabus.id, e)}
                                    className="p-2.5 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all"
                                    title="Pobierz DOCX"
                                >
                                    <Download className="w-5 h-5" />
                                </button>
                                <button 
                                    onClick={() => handleEdit(syllabus.id)}
                                    className="p-2.5 text-slate-500 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-all"
                                    title="Edytuj"
                                >
                                    <Edit3 className="w-5 h-5" />
                                </button>
                                <button 
                                    onClick={(e) => handleDelete(syllabus.id, e)}
                                    className="p-2.5 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
                                    title="Usuń"
                                >
                                    <Trash2 className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
