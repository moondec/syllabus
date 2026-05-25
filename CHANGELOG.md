# Changelog

All notable changes to this project will be documented in this file.

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
