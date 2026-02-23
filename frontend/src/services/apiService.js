import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const processDocument = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await axios.post(`${API_BASE_URL}/process-document`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.error || 'Błąd połączenia z serwerem. Upewnij się, że backend jest uruchomiony na porcie 8000.');
    }
};

export const generateSyllabus = async (data, format = 'docx') => {
    try {
        const response = await axios.post(`${API_BASE_URL}/generate-syllabus`, data, {
            responseType: 'blob', // Ważne dla obsługi plików binarnych (PDF/DOCX)
        });

        const fileExt = format === 'pdf' ? 'pdf' : 'docx';
        const blob = new Blob([response.data], {
            type: format === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        });

        // Wymuszanie pobrania pliku w przegladarce klienta
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `wygenerowany_sylabus.${fileExt}`);
        document.body.appendChild(link);
        link.click();

        // Cleanup
        link.parentNode.removeChild(link);
        window.URL.revokeObjectURL(url);

        return true;
    } catch (error) {
        if (error.response?.data instanceof Blob) {
            // Odkodowanie tekstu z error.response gdy jest to blob
            const text = await error.response.data.text();
            try { return JSON.parse(text).error; } catch (e) { throw new Error('Nieoczekiwany błąd generowania dokumentu'); }
        }
        throw new Error('Błąd połączenia z serwerem podczas generacji pliku.');
    }
};
