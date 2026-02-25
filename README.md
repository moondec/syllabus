# Kreator Sylabusów

Automatyczny system generowania sylabusów (kart przedmiotów) na podstawie programów studiów. Narzędzie analizuje dokumenty źródłowe, wyodrębnia efekty uczenia się i pozwala na szybkie przygotowanie profesjonalnej karty przedmiotu.

## Główne Funkcjonalności

*   **Import Danych:** Wczytywanie plików `.DOCX` / `.PDF` z programem studiów.
*   **Automatyczna Ekstrakcja:** Rozpoznawanie symboli efektów kierunkowych (W, U, K) oraz danych przedmiotowych (ECTS, semestr, nazwa).
*   **Wielojęzyczność (PL/EN):** Obsługa szablonów w języku polskim (`template_pl.docx`) i angielskim (`template_en.docx`). AI generuje treści w wybranym języku.
*   **Interaktywny Edytor:** Formularz React synchronizowany w czasie rzeczywistym z podpowiedziami z dokumentu źródłowego.
*   **Konfiguracja AI:** Możliwość ustawienia własnego klucza API, endpointu i modelu (domyślnie `bielik_11b` na hostowanym przez PCSS https://pcss.plcloud.pl). **Wymaga ustawienia własnego API Key bezpośrednio w interfejsie. Klucz jest zapamiętywany lokalnie.**
*   **Eksport do Word:** Generowanie gotowego dokumentu na podstawie szablonów przy użyciu `docxtpl`.

## Stos Technologiczny

*   **Backend:** Python (FastAPI), `python-docx`, `pdfplumber`, `docxtpl`.
*   **Frontend:** React (Vite), TailwindCSS, Axios.

## Instrukcja Obsługi

Aplikacja prowadzi użytkownika przez proces tworzenia sylabusa w 4 prostych krokach:

### Krok 1: Import Dokumentów Źródłowych
1. **Wgraj Program Studiów:** Wybierz plik `.docx` lub `.pdf` zawierający ogólny opis kierunku i tabelę efektów uczenia się.
2. **Wgraj Plany Studiów (Plan godzinowy):** Możesz wgrać do 4 różnych plików PDF z planami zajęć. System automatycznie dopasuje godziny do przedmiotu na podstawie jego nazwy i stopnia studiów:
   * **Studia I stopnia:** Plany dla trybu stacjonarnego i niestacjonarnego.
   * **Studia II stopnia:** Plany dla trybu stacjonarnego i niestacjonarnego.
   * *Wskazówka: System sam rozpozna stopień przedmiotu przy jego wyborze.*

### Krok 2: Wybór Przedmiotu
Z listy wyekstrahowanej z programu studiów wybierz przedmiot, dla którego chcesz przygotować sylabus. Po kliknięciu "Wybierz", system:
* Pobierze nazwę, ECTS i semestr z programu.
* Automatycznie dołączy liczby godzin z wgranych wcześniej planów studiów (S i NS).

### Krok 3: Edycja i Wspomaganie AI
Wypełnij pola formularza. Możesz to zrobić na trzy sposoby:
* **Ręcznie:** Wpisz tekst bezpośrednio w pole.
* **Z pomocą AI:** Kliknij ikonę błyskawicy/gwiazdek przy polach takich jak *Cel*, *Metody* czy *Treści*. AI zaproponuje profesjonalnie sformułowaną treść.
* **Hybrydowo (Polecane):** Wpisz kilka słów kluczowych lub punktów, które chcesz zawrzeć (np. "nauka Pythona, API, bazy danych"), a następnie kliknij przycisk AI. Model **rozwinie Twoje wskazówki** w pełny, poprawny językowo tekst sylabusa.
* **Symbole efektów:** Wybierz symbole (W, U, K) z rozwijanych list. Podpowiedzi z programu studiów zobaczysz w żółtej sekcji na górze edytora.

### Krok 4: Eksport
1. Wybierz język dokumentu (PL/EN) na górze strony.
2. Kliknij **"Eksportuj DOCX"**.
3. Gotowy, sformatowany plik zostanie pobrany na Twój dysk.

---

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

## Licencja

Projekt udostępniony na licencji **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
Możesz swobodnie kopiować, rozpowszechniać i zmieniać materiał w dowolnym celu, pod warunkiem podania autorstwa.
