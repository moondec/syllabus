# Changelog

All notable changes to this project will be documented in this file.

## [1.2.3] - 2026-05-29

### Added
- **Kompatybilność z wdrożeniami Portainer / IT**:
  - Obsługa sieci typu `macvlan` oraz dynamiczne wykrywanie uniwersyteckiej konfiguracji zapisu bazy danych SQLite (preferowanie `/app/data` podpiętego jako wolumen Portainera z automatycznym fallbackiem do `./data`).
  - Skrypt rozruchowy `30-setup-certs.sh` w kontenerze Nginx (frontend) automatycznie generujący certyfikaty SSL self-signed, gdy brak zewnętrznych kluczy SSL, zapobiegając awarii startu serwera.
  - Opcjonalne zmienne środowiskowe `DISABLE_SSL` oraz `HTTP_ONLY` umożliwiające wyłączenie wymuszenia SSL (przydatne przy terminacji ruchu SSL na zewnętrznym firewallu lub load balancerze).
  - Szablon konfiguracyjny `docker-compose.portainer.yml` dedykowany dla Działów IT uczelni.

### Changed
- **Wersja Oprogramowania**: Podniesiono wersję frontendu i backendu do `v1.2.3`.

---

## [1.2.2] - 2026-05-27

### Fixed
- **Poprawki parsowania planów Architektury Krajobrazu**:
  - Wprowadzono dynamiczną detekcję kolumny z liczbą porządkową (Lp.) w układach 11-kolumnowych planów PDF, zapobiegając błędnemu przesunięciu mapowania kolumn i pomijaniu przedmiotów.
  - Usprawniono funkcję `_safe_int`, dodając obsługę wartości godzinowych ze znakiem plus (np. `"30+10T"`), które są teraz rozbijane i sumowane zamiast błędnego łączenia w jedną dużą liczbę (np. `"305"`).

### Changed
- **Wersja Aplikacji**: Podniesiono wersję frontendu i backendu do `v1.2.2`.

---

## [1.2.1] - 2026-05-27

### Added
- **Adaptacyjny parser PDF**: Wprowadzono inteligentny mechanizm dopasowywania kolumn w planach studiów PDF w celu uniknięcia utraty przedmiotów.
- **Wsparcie dla layoutów 10-kolumnowych**: Obsługa planów w języku angielskim (np. kierunek Geoinformation) zawierających 10 kolumn.
- **Uniwersalna heurystyka detekcji (`_auto_detect_columns`)**: System samodzielnie analizuje nietypowe liczby kolumn (zastępując pomijanie wierszy w parserze).
- **Kaskadowe re-parsowanie PDF (Adaptive Tolerance Cascade)**: Automatyczne ponowne parsowanie dokumentu z dynamicznie rosnącą tolerancją tolerancji łączenia kolumn (`snap_tolerance`: 6, 10, 15) przy niskiej liczbie wykrytych przedmiotów.
- **Early stopping w kaskadzie**: Zatrzymanie prób re-parsowania po osiągnięciu progu 10 pomyślnie wczytanych przedmiotów w celu zachowania optymalnego parsowania pozostałych części pliku.

### Changed
- **Wersja Aplikacji**: Podniesiono wersję frontendu i backendu do `v1.2.1`.
- **Integracja API**: Przekazano ścieżkę fizyczną pliku `file_path` z API backendu do parsera, aby umożliwić re-parsowanie z nowymi parametrami tolerancji.

---

## [1.2.0] - 2026-05-25

### Added
- **SSL / HTTPS Support**: Wdrożono bezpieczną komunikację HTTPS z przekierowaniem z portu HTTP (80) do HTTPS (443).
- **Konfiguracja SSL w Nginx**: Dodano obsługę TLS 1.2 oraz TLS 1.3, nowoczesne szyfry, HSTS (Strict-Transport-Security) oraz przekazywanie nagłówków proxy (`X-Real-IP`, `X-Forwarded-Proto` itp.).
- **Generowanie Klucza Prywatnego i CSR**: Dodano skrypty/klucze w katalogu `ssl/` (klucz prywatny + Certificate Signing Request dla domeny `syllabus.up.poznan.pl`).
- **Montowanie Wolumenu SSL**: Powiązano lokalny folder `./ssl` z kontenerem Nginx w trybie tylko do odczytu (`ro`) w `docker-compose.yml`.
- **Link do Dokumentacji**: Dodano odnośnik do dokumentacji projektu (`README.md` w repozytorium GitHub) w stopce interfejsu użytkownika.
- **Bezpieczeństwo**: Dodano folder `ssl/` do `.gitignore` w celu ochrony poufnych danych (klucze prywatne i certyfikaty).

### Changed
- **Eksponowanie Portów**: Zmieniono domyślny port frontendu z `8080` na standardowy HTTP (`80`) i HTTPS (`443`).
- **Wersja Aplikacji**: Podniesiono wersję frontendu i backendu do `v1.2.0`.

---

## [1.1.1] - 2026-05-15

### Added
- **Obsługa planów w formacie DOCX**: Natywne wsparcie dla plików MS Word zawierających plany studiów z mapowaniem tabel 11-kolumnowych.
- **Wizualizacja wersji oprogramowania**: Endpoint `/api/version` na backendzie oraz dynamiczna stopka informacyjna w React wyświetlająca wersje obu komponentów.

### Fixed
- **Parsowanie programów wielostronicowych**: Usunięcie słowa `"symbol"` z listy wyjątków przerywających ekstrakcję w parserze PDF, co uniemożliwia przedwczesne ucinanie listy przedmiotów.

---

## [1.0.0] - 2026-05-01

### Added
- **Moduł Archiwalny**: Zapisywanie gotowych sylabusów do lokalnej bazy danych SQLite z zaawansowanym grupowaniem po "Wydziale" lub "Kierunku Studiów".
- **Docker Compose**: Pełna konteneryzacja aplikacji (Nginx jako reverse proxy + FastAPI backend).
- **Parser 13-kolumnowy**: Obsługa pionowego układu planów studiów II stopnia.
- **Interfejs Drag & Drop**: Obsługa przeciągania plików z planami studiów we frontendzie.
- **Poprawka pobierania plików**: Usunięcie problemu z gubieniem rozszerzenia `.docx` w przeglądarkach Chrome przez wdrożenie mechanizmu `iframe`.
