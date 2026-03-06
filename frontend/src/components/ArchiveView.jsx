import React, { useState, useEffect } from 'react';
import { listSyllabuses, getSyllabus, deleteSyllabus, generateSyllabus } from '../services/apiService';
import { Loader2, Trash2, Edit3, Download, Search, AlertCircle, FileText, Calendar, ArrowLeft, ChevronDown, ChevronRight, Building2, GraduationCap } from 'lucide-react';

export default function ArchiveView({ onEditSyllabus, onBack }) {
    const [syllabuses, setSyllabuses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [groupMode, setGroupMode] = useState('unit'); // 'unit' | 'field'
    const [deleteConfirmId, setDeleteConfirmId] = useState(null);
    const [expandedGroups, setExpandedGroups] = useState(new Set());

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

    const executeDelete = async (id) => {
        try {
            await deleteSyllabus(id);
            setSyllabuses(prev => prev.filter(s => s.id !== id));
            setDeleteConfirmId(null);
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

    // Grupowanie syllabusów zależnie od włączonego trybu
    const groupedSyllabuses = React.useMemo(() => {
        const filteredSyllabuses = syllabuses.filter(s =>
            (s.subject_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
            (s.field_of_study || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
            (s.unit || '').toLowerCase().includes(searchTerm.toLowerCase())
        );

        const groups = {};

        filteredSyllabuses.forEach(syllabus => {
            const key = groupMode === 'unit'
                ? (syllabus.unit || 'Brak przypisanej jednostki (Wydziału)')
                : (syllabus.field_of_study || 'Brak określonego kierunku');

            if (!groups[key]) {
                groups[key] = [];
            }
            groups[key].push(syllabus);
        });

        // Posortuj klucze alfabetycznie
        const sortedGroups = {};
        Object.keys(groups).sort().forEach(key => {
            sortedGroups[key] = groups[key];
        });

        return sortedGroups;
    }, [syllabuses, searchTerm, groupMode]);

    // Otwórz wszystkie grupy, jeśli jest wyszukiwanie lub po zmianie trybu, żeby ułatwić podgląd
    useEffect(() => {
        if (searchTerm.length > 0) {
            setExpandedGroups(new Set(Object.keys(groupedSyllabuses)));
        } else if (expandedGroups.size === 0 && Object.keys(groupedSyllabuses).length > 0) {
            // Domyślnie rozwiń pierwszą grupę lub wszystko zależnie od preferencji
            setExpandedGroups(new Set([Object.keys(groupedSyllabuses)[0]]));
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [searchTerm, groupMode, syllabuses.length]);

    const toggleGroup = (group) => {
        setExpandedGroups(prev => {
            const next = new Set(prev);
            if (next.has(group)) next.delete(group);
            else next.add(group);
            return next;
        });
    };

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
                <div className="flex flex-col md:flex-row items-center gap-4 w-full md:w-auto mt-4 md:mt-0">
                    <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200">
                        <button
                            onClick={() => setGroupMode('unit')}
                            className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all ${groupMode === 'unit' ? 'bg-white text-indigo-700 shadow-sm border border-slate-200' : 'text-slate-500 hover:text-slate-700'}`}
                        >
                            Wydziały / Katedry
                        </button>
                        <button
                            onClick={() => setGroupMode('field')}
                            className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all ${groupMode === 'field' ? 'bg-white text-indigo-700 shadow-sm border border-slate-200' : 'text-slate-500 hover:text-slate-700'}`}
                        >
                            Kierunki studiów
                        </button>
                    </div>

                    <div className="relative max-w-sm w-full md:w-64">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <input
                            type="text"
                            placeholder="Szukaj przedmiotu..."
                            value={searchTerm}
                            onChange={e => setSearchTerm(e.target.value)}
                            className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 shadow-sm"
                        />
                    </div>
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
            ) : Object.keys(groupedSyllabuses).length === 0 ? (
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
                ) : Object.keys(groupedSyllabuses).length === 0 ? (
                    <div className="text-center py-20 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200">
                        <p className="text-slate-500 max-w-xs mx-auto mt-2">
                            Nie znaleziono sylabusów pasujących do Twojego wyszukiwania.
                        </p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {Object.entries(groupedSyllabuses).map(([groupName, syllabusesArray]) => {
                            const isExpanded = expandedGroups.has(groupName);

                            return (
                                <div key={groupName} className="bg-white border text-left border-slate-200 rounded-xl overflow-hidden shadow-sm">
                                    {/* Group Header */}
                                    <button
                                        onClick={() => toggleGroup(groupName)}
                                        className="w-full flex items-center justify-between p-4 bg-slate-50 hover:bg-slate-100 transition-colors border-b border-slate-200"
                                    >
                                        <div className="flex items-center gap-3">
                                            {groupMode === 'unit' ? (
                                                <Building2 className={`w-5 h-5 ${isExpanded ? 'text-indigo-600' : 'text-slate-400'}`} />
                                                    ) : (
                                                        <GraduationCap className={`w-5 h-5 ${isExpanded ? 'text-emerald-600' : 'text-slate-400'}`} />
                                                    )}
                                                    <h3 className="font-bold text-slate-800 text-left">{groupName}</h3>
                                                    <span className={`text-xs font-bold px-2 py-0.5 rounded-full ml-2 ${groupMode === 'unit' ? 'bg-indigo-100 text-indigo-700' : 'bg-emerald-100 text-emerald-700'}`}>
                                                        {syllabusesArray.length} sylabusów
                                                    </span>
                                                </div>
                                                {isExpanded ? <ChevronDown className="w-5 h-5 text-slate-400" /> : <ChevronRight className="w-5 h-5 text-slate-400" />}
                                            </button>

                                            {/* Syllabuses List */}
                                            {isExpanded && (
                                                <div className="p-3 bg-white space-y-2">
                                                    {syllabusesArray.map(syllabus => (
                                                        <div
                                                            key={syllabus.id}
                                                            onClick={(e) => {
                                                                if (deleteConfirmId !== syllabus.id) handleEdit(syllabus.id);
                                                            }}
                                                            className={`group border rounded-lg p-4 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 ${deleteConfirmId === syllabus.id ? 'border-red-300 bg-red-50/50' : 'border-slate-200 bg-white hover:border-indigo-400 hover:shadow-md cursor-pointer'}`}
                                                        >
                                                            <div className="flex-1 min-w-0">
                                                                <div className="flex items-center gap-2 mb-1">
                                                                    <h5 className="text-base font-bold text-slate-800 truncate group-hover:text-indigo-600 transition-colors">
                                                                        {syllabus.subject_name || 'Bez nazwy'}
                                                                    </h5>
                                                                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-100 text-slate-500">
                                                                        ID: {syllabus.id}
                                                                    </span>
                                                                </div>
                                                                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
                                                                    {groupMode === 'unit' && (
                                                                        <div className="flex items-center gap-1.5 font-medium text-emerald-700">
                                                                            <GraduationCap className="w-3.5 h-3.5" />
                                                                            <span>{syllabus.field_of_study || 'Brak kierunku'}</span>
                                                                        </div>
                                                                    )}
                                                                    {groupMode === 'field' && (
                                                                        <div className="flex items-center gap-1.5 font-medium text-indigo-700">
                                                                            <Building2 className="w-3.5 h-3.5" />
                                                                            <span>{syllabus.unit || 'Brak wydziału'}</span>
                                                                        </div>
                                                                    )}
                                                                    <div className="w-1 h-1 rounded-full bg-slate-300 hidden md:block"></div>
                                                                    <div className="flex items-center gap-1.5">
                                                                        <span>Semestr: {syllabus.semester || '-'}</span>
                                                                    </div>
                                                                    {syllabus.level && (
                                                                        <>
                                                                            <div className="w-1 h-1 rounded-full bg-slate-300 hidden md:block"></div>
                                                                            <div className="flex items-center gap-1.5">
                                                                                <span>{syllabus.level}</span>
                                                                            </div>
                                                                        </>
                                                                    )}
                                                                    <div className="w-1 h-1 rounded-full bg-slate-300 hidden md:block"></div>
                                                                    <div className="flex items-center gap-1.5">
                                                                        <Calendar className="w-3.5 h-3.5" />
                                                                        <span>{formatDate(syllabus.updated_at)}</span>
                                                                    </div>
                                                                </div>
                                                                <div className="mt-2 text-[10px] text-slate-400 italic truncate max-w-2xl">
                                                                    {syllabus.legal_basis}
                                                                </div>
                                                            </div>

                                                            <div className="flex items-center gap-1">
                                                                <button
                                                                    onClick={(e) => handleDownload(syllabus.id, e)}
                                                                    className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-md transition-all"
                                                                    title="Pobierz DOCX"
                                                                >
                                                                    <Download className="w-4 h-4" />
                                                                </button>
                                                                <button
                                                                    onClick={(e) => { e.stopPropagation(); handleEdit(syllabus.id); }}
                                                                    className="p-2 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-md transition-all"
                                                                    title="Edytuj"
                                                                >
                                                                    <Edit3 className="w-4 h-4" />
                                                                </button>

                                                                {deleteConfirmId === syllabus.id ? (
                                                                    <div className="flex items-center gap-1 bg-red-100 p-1.5 rounded-lg ml-2 animate-in fade-in zoom-in duration-200">
                                                                        <span className="text-xs font-bold text-red-800 px-1 hidden sm:inline">Usunąć?</span>
                                                                        <button
                                                                            onClick={(e) => { e.stopPropagation(); executeDelete(syllabus.id); }}
                                                                            className="bg-red-600 hover:bg-red-700 text-white text-xs font-bold px-3 py-1.5 rounded transition-colors"
                                                                        >
                                                                            Tak
                                                                        </button>
                                                                        <button
                                                                            onClick={(e) => { e.stopPropagation(); setDeleteConfirmId(null); }}
                                                                            className="bg-white hover:bg-slate-100 text-slate-700 border border-red-200 text-xs font-bold px-3 py-1.5 rounded transition-colors"
                                                                        >
                                                                            Nie
                                                                        </button>
                                                                    </div>
                                                                ) : (
                                                                        <button
                                                                            onClick={(e) => { e.stopPropagation(); setDeleteConfirmId(syllabus.id); }}
                                                                            className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-all"
                                                                            title="Usuń"
                                                                        >
                                                                            <Trash2 className="w-4 h-4" />
                                                                        </button>
                                                                )}
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                </div>
            )}
        </div>
    );
}
