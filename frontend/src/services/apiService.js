import axios from 'axios';

// Z proxy w vite.config.js, wszystkie requesty /api/* sa przekierowywane na backend
const API_BASE_URL = '/api';

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
        // Krok 1: Wyslij dane do backendu i otrzymaj URL do pobrania
        const response = await axios.post(`${API_BASE_URL}/generate-syllabus`, data);

        const downloadUrl = response.data?.download_url;
        if (!downloadUrl) {
            throw new Error(response.data?.error || 'Brak URL do pobrania pliku');
        }

        // Krok 2: Przekieruj przegladarke do endpointu GET (same-origin dzieki proxy)
        window.location.href = downloadUrl;

        return true;
    } catch (error) {
        if (error.response?.data?.error) {
            throw new Error(error.response.data.error);
        }
        throw new Error(error.message || 'Błąd połączenia z serwerem podczas generacji pliku.');
    }
};
