# Kreator Sylabusów

Automatyczny system generowania sylabusów (kart przedmiotów) na podstawie programów studiów. Narzędzie analizuje dokumenty źródłowe, wyodrębnia efekty uczenia się i pozwala na szybkie przygotowanie profesjonalnej karty przedmiotu.

## Główne Funkcjonalności

*   **Import Danych:** Wczytywanie plików `.DOCX` / `.PDF` z programem studiów.
*   **Automatyczna Ekstrakcja:** Rozpoznawanie symboli efektów kierunkowych (W, U, K) oraz danych przedmiotowych (ECTS, semestr, nazwa).
*   **Interaktywny Edytor:** Formularz React synchronizowany w czasie rzeczywistym z podpowiedziami z dokumentu źródłowego.
*   **Eksport do Word:** Generowanie gotowego dokumentu na podstawie `template.docx` przy użyciu `docxtpl`.

## Stos Technologiczny

*   **Backend:** Python (FastAPI), `python-docx`, `pdfplumber`, `docxtpl`.
*   **Frontend:** React (Vite), TailwindCSS, Axios.

## Uruchomienie Projektu

### Backend
1. Przejdź do folderu `backend`.
2. Zainstaluj zależności: `pip install -r requirements.txt`.
3. Uruchom serwer: `python -m uvicorn main:app --reload`.

### Frontend
1. Przejdź do folderu `frontend`.
2. Zainstaluj zależności: `npm install`.
3. Uruchom aplikację: `npm run dev`.

## TODO / Przyszłe Ulepszenia

*   **Integracja z LLM (np. Bielik):** Wykorzystanie modeli językowych do automatycznego generowania propozycji treści dla pól takich jak "Cel przedmiotu", "Wiedza", "Umiejętności" na podstawie samej nazwy przedmiotu i przypisanych symboli efektów.
*   **Perfekcyjne Mapowanie Dokumentu:** Dalsze udoskonalanie szablonu `template.docx` i stylizacji tabel, aby generowany plik był identyczny z oficjalnym wzorem Uczelni (np. specyficzne obramowania, logotypy, układy sekcji).
*   **Walidacja Efektów:** Automatyczne sprawdzanie, czy wybrane przez użytkownika symbole efektów pokrywają się z wymogami programu studiów dla danej grupy przedmiotów.
*   **Obsługa Wielu Szablonów:** System wyboru z jakiego szablonu (dla jakiego Wydziału/Instytutu) ma zostać wygenerowany sylabus.
*   **Moduł Archiwizacji:** Możliwość zapisu wygenerowanych sylabusów w bazie danych w celu ich późniejszej edycji.

## Licencja

Projekt udostępniony na licencji **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
Możesz swobodnie kopiować, rozpowszechniać i zmieniać materiał w dowolnym celu, pod warunkiem podania autorstwa.
