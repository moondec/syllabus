import React, { useState, useRef, useEffect } from 'react';
import { Check, ChevronDown, X, Info } from 'lucide-react';

export default function MultiSelectDropdown({ selected, options, onChange, label }) {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);

    // selected is a string like "SYM1, SYM2"
    const selectedArray = selected ? selected.split(',').map(s => s.trim()).filter(Boolean) : [];

    useEffect(() => {
        function handleClickOutside(event) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const toggleOption = (symbol) => {
        let newSelected;
        if (selectedArray.includes(symbol)) {
            newSelected = selectedArray.filter(s => s !== symbol);
        } else {
            newSelected = [...selectedArray, symbol];
        }
        onChange(newSelected.join(', '));
    };

    const removeOption = (e, symbol) => {
        e.stopPropagation();
        const newSelected = selectedArray.filter(s => s !== symbol);
        onChange(newSelected.join(', '));
    };

    return (
        <div className="relative" ref={dropdownRef}>
            <div 
                onClick={() => setIsOpen(!isOpen)}
                className="min-h-[42px] w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 flex flex-wrap gap-2 cursor-pointer hover:border-indigo-400 transition-colors"
            >
                {selectedArray.length > 0 ? (
                    selectedArray.map(symbol => (
                        <span 
                            key={symbol} 
                            className="bg-indigo-100 text-indigo-700 text-xs font-semibold px-2 py-1 rounded-md flex items-center gap-1 group"
                        >
                            {symbol}
                            <X 
                                className="w-3 h-3 cursor-pointer hover:text-indigo-900" 
                                onClick={(e) => removeOption(e, symbol)}
                            />
                        </span>
                    ))
                ) : (
                    <span className="text-slate-400 text-sm py-1">Wybierz efekty kierunkowe...</span>
                )}
                <div className="ml-auto flex items-center">
                    <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
                </div>
            </div>

            {isOpen && (
                <div className="absolute z-50 mt-2 w-full bg-white border border-slate-200 rounded-xl shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-100 max-h-60 overflow-y-auto">
                    {options && options.length > 0 ? (
                        <div className="py-2">
                            {options.map((option) => (
                                <div 
                                    key={option.symbol}
                                    onClick={() => toggleOption(option.symbol)}
                                    className={`px-4 py-3 flex items-start gap-3 hover:bg-slate-50 transition-colors cursor-pointer border-b border-slate-50 last:border-0 ${selectedArray.includes(option.symbol) ? 'bg-indigo-50/50' : ''}`}
                                >
                                    <div className={`mt-0.5 w-4 h-4 rounded border flex items-center justify-center transition-colors ${selectedArray.includes(option.symbol) ? 'bg-indigo-600 border-indigo-600 text-white' : 'border-slate-300 bg-white'}`}>
                                        {selectedArray.includes(option.symbol) && <Check className="w-3 h-3" />}
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2">
                                            <span className="font-bold text-sm text-slate-900">{option.symbol}</span>
                                        </div>
                                        {option.description && (
                                            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                                                {option.description}
                                            </p>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="p-4 text-center text-sm text-slate-500 italic">
                            Brak dostępnych efektów dla tej kategorii.
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
