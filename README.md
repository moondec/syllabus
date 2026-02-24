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


## Zrealizowane / Ostatnie Ulepszenia

*   [x] **Integracja z LLM (Bielik):** Pełna integracja z modelami językowymi (np. Bielik) do automatycznego generowania propozycji treści dla wszystkich kluczowych pól sylabusa (cel, metody, treści, efekty). Obsługa kontekstu użytkownika i tłumaczeń PL/EN. *Może wymagać drobnego doszlifowania promptów.*
*   [x] **Wielojęzyczność:** Dynamiczny wybór języka dokumentu i AI bezpośrednio w edytorze.

## TODO / Przyszłe Ulepszenia

*   **Perfekcyjne Mapowanie Dokumentu:** Dalsze udoskonalanie szablonu `template.docx` i stylizacji tabel, aby generowany plik był identyczny z oficjalnym wzorem Uczelni.
*   **Walidacja Efektów:** Automatyczne sprawdzanie, czy wybrane przez użytkownika symbole efektów pokrywają się z wymogami programu studiów.
*   **Obsługa Wielu Szablonów:** System wyboru szablonu dla różnych jednostek organizacyjnych.
*   **Moduł Archiwizacji:** Zapis i edycja wcześniej wygenerowanych sylabusów w chmurze/bazie danych.

## Licencja

Projekt udostępniony na licencji **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
Możesz swobodnie kopiować, rozpowszechniać i zmieniać materiał w dowolnym celu, pod warunkiem podania autorstwa.
