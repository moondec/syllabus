# Kreator Sylabusów

Automatyczny system generowania sylabusów (kart przedmiotów) na podstawie programów studiów. Narzędzie analizuje dokumenty źródłowe, wyodrębnia efekty uczenia się i pozwala na szybkie przygotowanie profesjonalnej karty przedmiotu.

## Główne Funkcjonalności

*   **Import Danych:** Wczytywanie plików `.DOCX` / `.PDF` z programem studiów.
*   **Automatyczna Ekstrakcja:** Rozpoznawanie symboli efektów kierunkowych (W, U, K) oraz danych przedmiotowych (ECTS, semestr, nazwa).
*   **Wielojęzyczność (PL/EN):** Obsługa szablonów w języku polskim (`template_pl.docx`) i angielskim (`template_en.docx`). AI generuje treści w wybranym języku.
*   **Interaktywny Edytor:** Formularz React synchronizowany w czasie rzeczywistym z podpowiedziami z dokumentu źródłowego.
*   **Konfiguracja AI:** Możliwość ustawienia własnego klucza API, endpointu i modelu (domyślnie `bielik_11b`) bezpośrednio w interfejsie. Klucz jest zapamiętywany lokalnie.
*   **Eksport do Word:** Generowanie gotowego dokumentu na podstawie szablonów przy użyciu `docxtpl`.

## Stos Technologiczny

*   **Backend:** Python (FastAPI), `python-docx`, `pdfplumber`, `docxtpl`.
*   **Frontend:** React (Vite), TailwindCSS, Axios.

## Uruchomienie Projektu

Aby uruchomić aplikację, należy otworzyć dwa osobne terminale (jeden dla backendu, drugi dla frontendu).

### 1. Backend (FastAPI)
Otwórz terminal w głównym folderze projektu i wykonaj:
```bash
cd backend
# Opcjonalnie: stwórz i aktywuj venv
# python -m venv venv
# source venv/bin/activate  # Mac/Linux
# .\venv\Scripts\activate   # Windows

pip install -r ../requirements.txt
python -m uvicorn main:app --reload
```
Serwer API będzie dostępny pod adresem: `http://localhost:8000`

### 2. Frontend (React + Vite)
Otwórz drugi terminal w głównym folderze projektu i wykonaj:
```bash
cd frontend
npm install
npm run dev
```
Aplikacja będzie dostępna pod adresem: `http://localhost:5173`


## TODO / Przyszłe Ulepszenia

*   **Integracja z LLM (np. Bielik):** Wykorzystanie modeli językowych do automatycznego generowania propozycji treści dla pól takich jak "Cel przedmiotu", "Wiedza", "Umiejętności" na podstawie samej nazwy przedmiotu i przypisanych symboli efektów.
*   **Perfekcyjne Mapowanie Dokumentu:** Dalsze udoskonalanie szablonu `template.docx` i stylizacji tabel, aby generowany plik był identyczny z oficjalnym wzorem Uczelni (np. specyficzne obramowania, logotypy, układy sekcji).
*   **Walidacja Efektów:** Automatyczne sprawdzanie, czy wybrane przez użytkownika symbole efektów pokrywają się z wymogami programu studiów dla danej grupy przedmiotów.
*   **Obsługa Wielu Szablonów:** System wyboru z jakiego szablonu (dla jakiego Wydziału/Instytutu) ma zostać wygenerowany sylabus.
*   **Moduł Archiwizacji:** Możliwość zapisu wygenerowanych sylabusów w bazie danych w celu ich późniejszej edycji.

## Licencja

Projekt udostępniony na licencji **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
Możesz swobodnie kopiować, rozpowszechniać i zmieniać materiał w dowolnym celu, pod warunkiem podania autorstwa.
