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

## Nowości w wersji v1.3.0

1. **Nowe Logo i Kolorystyka**: Wprowadzono nową identyfikację wizualną, dodano oficjalne logo Uniwersytetu Przyrodniczego w Poznaniu w nagłówku. Zmieniono główny motyw kolorystyczny na ciemną zieleń charakterystyczną dla uczelni.
2. **Autorstwo i Kontakt**: W stopce aplikacji umieszczono dane autora wraz z kontaktowym adreresem e-mail.
3. **Poprawka Pobrań (Kodowanie Znaków)**: Wyeliminowano problem z błędem serwera (500) przy próbie pobrania plików zawierających polskie znaki w nazwie (np. "ż", "ś") na niektórych systemach Linux/Docker, polegając na natywnym wsparciu FastAPI.

---

## Nowości w wersji v1.2.4

1. **Kompatybilność z wdrożeniami Portainer / IT**: Obsługa uniwersyteckiej wirtualizacji przy użyciu dedykowanych sieci `macvlan` oraz zewnętrznych wolumenów bazodanowych podpiętych pod `/app/data`.
2. **Dynamiczna konfiguracja SSL/HTTP**: Serwer Nginx we frontendzie automatycznie generuje certyfikaty self-signed przy braku certyfikatów zewnętrznych lub pozwala na całkowite wyłączenie protokołu HTTPS i wymuszenia SSL (opcje `DISABLE_SSL` / `HTTP_ONLY`).

---

## Nowości w wersji v1.2.2

1. **Obsługa planów z numeracją (Architektura Krajobrazu)**: Wprowadzono dynamiczną detekcję obecności liczby porządkowej (Lp.) w 11-kolumnowych tabelach PDF, zapobiegając przesunięciom kolumn i gubieniu przedmiotów.
2. **Sumowanie godzin z plusami**: Zintegrowano nową funkcję sumującą w `_safe_int`, która poprawnie interpretuje i sumuje godziny z oznaczeniami typu `30+10T` zamiast ich konkatenowania.

---

## Nowości w wersji v1.2.1

1. **Adaptacyjny parser PDF (Automatyczna detekcja kolumn)**: Wprowadzono zaawansowaną heurystykę auto-detekcji kolumn (`_auto_detect_columns`), która eliminuje problem pomijania wierszy w nietypowych tabelach PDF.
2. **Kaskadowe re-parsowanie (snap_tolerance cascade)**: W przypadku wykrycia małej liczby przedmiotów (< 10), parser automatycznie powtarza analizę z różnymi poziomami tolerancji łączenia kolumn (6, 10, 15), aby scalić sztuczne, nałożone na siebie kolumny.
3. **Obsługa układu 10-kolumnowego**: Dodano natywne wsparcie dla 10-kolumnowych planów studiów (np. anglojęzycznych planów typu Geoinformation), co pozwoliło na pełne wczytanie brakujących przedmiotów.

---

## Nowości w wersji v1.2.0

1. **Wsparcie dla SSL/TLS (HTTPS)**: Dodano obsługę bezpiecznego szyfrowania SSL na poziomie Nginx w kontenerze frontendowym. Zaimplementowano protokoły TLS 1.2 oraz TLS 1.3 z nowoczesnymi szyframi i HSTS. Ruch HTTP (port 80) jest automatycznie przekierowywany na HTTPS (port 443).
2. **Dynamiczny odnośnik do dokumentacji**: Dodano bezpośredni link do dokumentacji projektu w stopce aplikacji React.
3. **Bezpieczne klucze**: Wygenerowano klucz prywatny oraz CSR w katalogu `ssl/` (automatycznie ignorowane przez gita za pomocą `.gitignore`).

Pełna lista zmian dostępna jest w pliku [CHANGELOG.md](file:///Users/marekurbaniak/Documents/Cursor/syllabus/CHANGELOG.md).

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
Kontener NGINX opublikuje cały frontend na standardowych portach HTTP (`80`) i HTTPS (`443`). Po wdrożeniu certyfikatu SSL aplikacja uruchamia się po wejściu w przeglądarce na adres:
`https://syllabus.up.poznan.pl` (z automatycznym przekierowaniem z portu 80).

**Konfiguracja certyfikatów SSL:**
Przed uruchomieniem aplikacji w wersji SSL z Docker Compose:
1. Przekaż plik `ssl/syllabus.csr` administratorowi sieci w celu podpisania.
2. Zapisz otrzymany certyfikat w lokalnym katalogu jako `ssl/up_puls_wildcard.pem`.
(Oryginalny wygenerowany klucz prywatny znajduje się pod nazwą `ssl/klucz_prywatny.pem`).
3. Uruchom kontener poleceniem `docker compose up -d --build`.

*Informacja techniczna: Plik konfiguracyjny sam mapuje bazę danych i podmontowuje ją w niewidocznym lokalnie, bezpiecznym wolumenie typu `sqlite_data`. Zapisane sylabusy pozostaną nienaruszone nawet po restartach obrazów Dockera (Dopóki nie wywołasz ręcznie komendy wpisującej destrukcję `docker compose down -v`)*

### Wdrożenie produkcyjne (np. Portainer / Uniwersytecki Dział IT) 🌐

W przypadku wdrożeń na infrastrukturze uniwersyteckiej przy użyciu menedżerów kontenerów typu **Portainer** (z dedykowanymi sieciami `macvlan` oraz zewnętrznymi wolumenami), system automatycznie wspiera elastyczną konfigurację:

1. **Dynamiczna lokalizacja bazy danych:**
   Backend automatycznie wykrywa zamontowanie wolumenu pod `/app/data` (standard dla Portainera) i używa go do zapisu bazy SQLite (`syllabus.db`). Jeżeli wolumen nie jest tam podmontowany (np. przy deweloperskim uruchomieniu), baza zostanie zapisana w lokalnym katalogu roboczym backendu (`/app/backend/data`).

2. **Automatyczne/Elastyczne SSL:**
   - **Brak zewnętrznego SSL / Brak podmontowanych certyfikatów:** Kontener frontendowy automatycznie wygeneruje tymczasowy certyfikat **self-signed** przy każdym uruchomieniu, aby serwer Nginx mógł poprawnie wystartować i obsługiwać bezpieczny protokół HTTPS.
   - **Terminacja SSL na zewnętrznym proxy / firewallu:** Jeśli SSL jest obsługiwany przez router/firewall sieciowy uniwersytetu i ruch do kontenera trafia po zwykłym HTTP, ustaw zmienną środowiskową we frontendzie: `DISABLE_SSL=true`. Wyłączy to przekierowanie na HTTPS i skonfiguruje Nginx do pracy na czystym porcie 80.
   - **Własny certyfikat SSL:** Podmontuj swoje pliki certyfikatu do katalogu `/etc/nginx/ssl` w kontenerze frontendowym jako `/etc/nginx/ssl/up_puls_wildcard.pem` oraz `/etc/nginx/ssl/klucz_prywatny.pem`.

Szczegółowy plik konfiguracyjny dedykowany dla tego typu instalacji znajduje się w pliku [docker-compose.portainer.yml](file:///Users/marekurbaniak/Documents/Cursor/syllabus/docker-compose.portainer.yml).

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
