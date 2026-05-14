# Kreator Sylabusów

Automatyczny system generowania sylabusów (kart przedmiotów) na podstawie programów studiów. Narzędzie analizuje dokumenty źródłowe, wyodrębnia efekty uczenia się i pozwala na szybkie przygotowanie profesjonalnej karty przedmiotu.

## Główne Funkcjonalności

*   **Import Danych:** Wczytywanie plików `.DOCX` / `.PDF` z programem studiów.
*   **Automatyczna Ekstrakcja:** Rozpoznawanie symboli efektów kierunkowych (W, U, K) oraz danych przedmiotowych (ECTS, semestr, nazwa).
*   **Wielojęzyczność (PL/EN):** Obsługa szablonów w języku polskim (`template_pl.docx`) i angielskim (`template_en.docx`). AI generuje treści w wybranym języku.
*   **Interaktywny Edytor:** Formularz React synchronizowany w czasie rzeczywistym z podpowiedziami z dokumentu źródłowego.
*   **Wbudowana Baza Danych Archiwalnych:** Zapis gotowych sylabusów do lokalnej bazy danych SQLite z pełną indeksacją ułatwiającą powrót do wcześniejszych prac. Opcja spłaszczonego grupowania kart (Wyświetlanie hierarchii "Wydział -> Kierunek").
*   **Konfiguracja AI:** Możliwość ustawienia własnego klucza API, endpointu i modelu (domyślnie `bielik_11b` na hostowanym przez PCSS https://pcss.plcloud.pl). Wymaga klucza, który jest zapamiętywany lokalnie.
*   **Eksport do Word:** Niezawodne środowisko generowania i pobierania przekształconych wizualnie szablonów `docxtpl` - wspierane i zabezpieczone do użytku na każdej współczesnej przeglądarce (Safari, Firefox, Chrome).

---

## Nowości w wersji v1.1.1

1. **Pełna obsługa planów studiów w formacie `.docx`:** Dodano natywne wsparcie dla plików MS Word zawierających plany studiów (I i II stopnia), uwzględniając nowe mapowanie tabel 11-kolumnowych. Pozwala to uniknąć błędów nieczytelności lub rozstrzelonych liter powstających podczas ich konwersji do PDF.
2. **Zaawansowane parsowanie wielostronicowych programów studiów:** Usprawniono maszynę stanów detekcji tabel przedmiotowych w plikach PDF (usunięcie słowa `"symbol"` z listy wyjątków przerywających ekstrakcję). Pozwala to na pełne, bezbłędne odczytanie wszystkich przedmiotów dla obu poziomów studiów (np. 111 przedmiotów na kierunku Ekonomia) zawartych w jednym pliku źródłowym bez przedwczesnego ucinania listy na skutek wzmianek o symbolach w treściach programowych.
3. **Wizualizacja wersji oprogramowania w czasie rzeczywistym:** Dodano nowy endpoint `/api/version` na backendzie oraz dynamiczną stopkę informacyjną w interfejsie React, informującą na bieżąco o załadowanych kompilacjach systemu.

---

## Nowości w wersji v1.0.0

1. **Usprawnione Archiwum (Grupowanie):** Wbudowaliśmy zaawansowany "Przełącznik Grupowania" pozwalający sortować archiwalne sylabusy bezpośrednio według opcji "Wydział" (Katedra) lub według "Kierunków Studiów".
2. **Bezbłędny interfejs pobierania (Cross-browser):** Wyeliminowano trudny błąd przeglądarki Chrome z gubieniem rozszerzeń `.docx`. Pliki są teraz pobierane niezawodnym łączem przez ukrytą ramkę `iframe` w locie wymuszając nagłówek CORS `Content-Disposition`.
3. **Pojedynczy Kontener Docker Compose:** Dodano pełne wsparcie dla architektury konteneryzacji - Konfiguracja NGINX jako serwera frontonowego (reverse proxy) dla statycznego frontendu tworzonego przez Vite oraz przekierowującego żądania przez określony port do backendu opartego na FastAPI.
4. **Zaawansowany Parser Planów Studiów II Stopnia:** Dodano obsługę pionowego układu dokumentów PDF (orientacja portrait) z nietypową strukturą 13-kolumnową, co umożliwia bezbłędną ekstrakcję godzin dla przedmiotów na studiach magisterskich.
5. **Ujednolicony interfejs Drag & Drop:** Przyciski ładowania planów studiów (I i II stopnia, S/NS) we frontendzie wspierają teraz pełne przeciąganie i upuszczanie plików z dynamicznym podglądem stanu (identycznie jak główny uploader programu studiów).
6. **Wsparcie dla zewnętrznych środowisk sieciowych (macvlan/Cloud):** Pobieranie wygenerowanych dokumentów w pełni współpracuje z wdrożeniami na zewnętrznych serwerach dzięki wykorzystaniu ścieżek względnych w oparciu o Nginx Reverse Proxy.

---

## Uruchomienie Projektu - Sposób 1: Pół-automatyczny (Docker Compose) 🐳 - ZALECANY

> **Wymagania wstępne:** Do skorzystania z tej opcji musisz mieć zainstalowane oprogramowanie **Docker** na swoim urządzeniu.
> * **macOS / Windows:** Najprościej pobrać i zainstalować aplikację [Docker Desktop](https://www.docker.com/products/docker-desktop/).
> * **Linux (Ubuntu/Debian):** Wpisz w terminalu skrypt instalacyjny: `curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh`. Dla starszych systemów użyj menedżera pakietów bazując na [oficjalnej dokumentacji Dockera](https://docs.docker.com/engine/install/).
> * **Sprawdzenie poprawności:** Otwórz terminal i upewnij się, że wpisanie komendy `docker version` po zainstalowaniu nie wyrzuca błędów.

Otwórz jeden terminal i w **głównym folderze projektu** wpisz pojedynczą komendę:
```bash
docker compose up -d --build
```

**Dostęp:**
Kontener NGINX natychmiast opublikuje cały frontend na głównym porcie. Zintegruje go automatycznie w tle z backendem! Aplikacja uruchamia się po wejściu w przeglądarce na adres:
`http://localhost:8080` (Port 8080)

*Informacja techniczna: Plik konfiguracyjny sam mapuje bazę danych i podmontowuje ją w niewidocznym lokalnie, bezpiecznym wolumenie typu `sqlite_data`. Zapisane sylabusy pozostaną nienaruszone nawet po restartach obrazów Dockera (Dopóki nie wywołasz ręcznie komendy wpisującej destrukcję `docker compose down -v`)*

---

---

## Rozwiązywanie problemów: `docker: command not found`

Jeżeli zainstalowałeś Docker Desktop, ale komenda `docker` nie jest rozpoznawana w terminalu, spróbuj następujących kroków:

1. **Otwórz Docker Desktop:** Upewnij się, że aplikacja jest uruchomiona i przeszedłeś przez proces wstępnej konfiguracji.
2. **Ustawienia Docker Desktop:** Wejdź w `Settings` (ikona zębatki) -> `General` -> `Choose how to install Docker CLI tools` i upewnij się, że wybrana jest opcja **System (recommended)**. Kliknij `Apply & Restart`.
3. **Ręczne dodanie do ścieżki (macOS):** Jeżeli problem nadal występuje, możesz dodać link symboliczny ręcznie w terminalu:
   ```bash
   sudo ln -s /Applications/Docker.app/Contents/Resources/bin/docker /usr/local/bin/docker
   sudo ln -s /Applications/Docker.app/Contents/Resources/bin/docker-compose /usr/local/bin/docker-compose
   ```
4. **Restart terminala:** Po dokonaniu zmian zamknij i otwórz ponownie terminal.

---

## Zarządzanie Kontenerami (Przydatne Komendy) 🛠️

Jeżeli używasz **Sposobu 1 (Docker Compose)**, oto lista najczęstszych operacji:

*   **Zatrzymanie aplikacji:**
    ```bash
    docker compose stop
    ```
*   **Uruchomienie zatrzymanej aplikacji:**
    ```bash
    docker compose start
    ```
*   **Restart całej aplikacji:**
    ```bash
    docker compose restart
    ```
*   **Aktualizacja (zastosowanie zmian w kodzie):**
    Gdy pobierzesz nową wersję z Gita lub wprowadzisz własne zmiany, przebuduj obrazy:
    ```bash
    docker compose up -d --build
    ```
*   **Całkowite usunięcie kontenerów (czysty start):**
    ```bash
    docker compose down
    ```
*   **Usunięcie kontenerów wraz z danymi (UWAGA: Czyści bazę SQLite!):**
    ```bash
    docker compose down -v
    ```

---

## Uruchomienie Projektu - Sposób 2: Natywnie (Developer / Node.js + Python) 💻

Jeżeli chcesz zainstalować projekt bezpośrednio w swoim środowisku developerskim:

Aby uruchomić aplikację, otwórz **dwa osobne** terminale bash/cmd i ustaw ścieżkę do głównego folderu narzędzia Kreator Sylabusów.

### 1. Panel Backendowy (FastAPI + Python)
W pierwszym oknie terminala skieruj ścieżkę tylko do backendu i zainstaluj/aktywuj moduły Pythonowe:
```bash
cd backend

# Opcjonalnie (ale zalecane!): stwórz i aktywuj środowisko izolowane
python -m venv venv
source venv/bin/activate  # Mac / Linux
# venv\Scripts\activate   # Windows CMD

# Gdy już jest aktywowane i masz przedrostek (venv)
pip install -r requirements.txt
python -m uvicorn main:app --reload
```
Serwer API będzie nasłuchiwał po cichu interakcji pod adresem lokalnym: `http://localhost:8000`

### 2. Panel Frontendowy (React + Vite)
Otwórz drugie okno terminala w nadrzędnym folderze repozytorium (nie zamykając w tle poprzedniego z pythonem!), przejdź na drugą ścieżkę:
```bash
cd frontend
npm install
npm run dev
```
Otworzy się proces Reacta (HMR Hot-reload), a konsola wypisze ci adres `http://localhost:5173`. Wejdź w niego w przeglądarce klikając.

---

## Licencja

Projekt udostępniony na licencji **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
Możesz swobodnie kopiować, rozpowszechniać i zmieniać materiał w dowolnym celu, pod warunkiem podania autorstwa.
