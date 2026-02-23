import React, { useCallback, useRef, useState } from 'react';
import { UploadCloud, File, X } from 'lucide-react';

export default function FileUploader({ onFileSelect }) {
    const [isDragActive, setIsDragActive] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const fileInputRef = useRef(null);

    const handleDrag = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setIsDragActive(true);
        } else if (e.type === 'dragleave') {
            setIsDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFiles(e.dataTransfer.files);
        }
    }, []);

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFiles(e.target.files);
        }
    };

    const handleFiles = (files) => {
        const file = files[0];
        const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];

        if (validTypes.includes(file.type) || file.name.endsWith('.pdf') || file.name.endsWith('.docx')) {
            setSelectedFile(file);
        } else {
            alert('Tylko pliki .pdf oraz .docx są akceptowane.');
        }
    };

    const submitFile = () => {
        if (selectedFile) {
            onFileSelect(selectedFile);
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto">
            <div
                className={`relative rounded-2xl border-2 border-dashed transition-all duration-200 ease-in-out p-12 text-center flex flex-col items-center justify-center gap-4 ${isDragActive
                        ? 'border-indigo-500 bg-indigo-50/50'
                        : selectedFile
                            ? 'border-emerald-500 bg-emerald-50/30'
                            : 'border-slate-300 hover:border-slate-400 bg-slate-50'
                    }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => !selectedFile && fileInputRef.current?.click()}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    className="hidden"
                    accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    onChange={handleChange}
                />

                {selectedFile ? (
                    <div className="flex items-center gap-4 animate-in fade-in zoom-in duration-300">
                        <div className="w-14 h-14 bg-emerald-100 text-emerald-600 rounded-xl flex items-center justify-center">
                            <File className="w-7 h-7" />
                        </div>
                        <div className="text-left">
                            <p className="text-sm font-semibold text-slate-800 line-clamp-1">{selectedFile.name}</p>
                            <p className="text-xs text-slate-500">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                        </div>
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                setSelectedFile(null);
                                if (fileInputRef.current) fileInputRef.current.value = '';
                            }}
                            className="p-2 ml-4 hover:bg-red-50 text-slate-400 hover:text-red-500 rounded-full transition-colors"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                ) : (
                    <>
                        <div className="w-16 h-16 bg-white border border-slate-200 text-slate-400 shadow-sm rounded-full flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
                            <UploadCloud className="w-8 h-8 flex-shrink-0" />
                        </div>
                        <div>
                            <p className="text-lg font-medium text-slate-800">
                                Przeciągnij i upuść plik
                            </p>
                            <p className="text-sm text-slate-500 mt-1">
                                lub <span className="text-indigo-600 font-medium">przeglądaj pliki</span>, by wybrać dokument.
                            </p>
                            <p className="text-xs text-slate-400 mt-4">Odczytujemy pliki .PDF oraz .DOCX</p>
                        </div>
                    </>
                )}
            </div>

            {selectedFile && (
                <div className="mt-8 text-center animate-in slide-in-from-bottom-4 fade-in duration-500">
                    <button
                        onClick={submitFile}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-600/20 rounded-xl px-8 py-3.5 font-semibold text-lg hover:-translate-y-0.5 transition-all duration-200"
                    >
                        Przetwórz Program Studiów
                    </button>
                </div>
            )}
        </div>
    );
}
