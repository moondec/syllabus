### **Projekt: Aplikacja Webowa "Kreator Sylabusów"**

#### **1. Cel Projektu**

Stworzenie aplikacji internetowej, która zautomatyzuje proces generowania sylabusów (kart przedmiotów). Aplikacja ma za zadanie wczytać program studiów z pliku `.DOCX` lub `.PDF`, automatycznie wypełnić szablon sylabusa danymi dla wskazanego przedmiotu, umożliwić użytkownikowi ręczną edycję tych danych, a na koniec wyeksportować gotowy dokument do formatu `.DOCX` lub `.PDF`.

---

#### **2. Główne Funkcjonalności**

* [cite_start]**Import Danych:** Użytkownik może wgrać plik `.DOCX` / `.PDF` z programem studiów lub podać do niego adres URL[cite: 25].
#### **2. Główne Funkcjonalności**

* **Import Danych:** Użytkownik może wgrać plik `.DOCX` / `.PDF` z programem studiów.
* **Automatyczna Ekstrakcja:** System analizuje dokument (tabele lub tekst surowy) i identyfikuje:
    * Listę przedmiotów, ECTS, semestr, jednostkę realizującą.
    * **Obsługa wielu poziomów kształcenia:** Jeden plik (`.DOCX` / `.PDF`) może zawierać zarówno program studiów **I stopnia** jak i **II stopnia**. Każdy stopień posiada ten sam układ tabel (ale inną treść). Efekty i przedmioty nie mogą się mieszać między poziomami. Rozpoznawanie stopnia odbywa się na podstawie markera `Poziom kształcenia: studia ... stopnia` w dokumencie.
    * **Efekty Uczenia Się (Kluczowe):** Ekstrakcja symboli kierunkowych z podziałem na 3 kategorie:
        * **WIEDZA (W):** np. `IS1A_WG01`
        * **UMIEJĘTNOŚCI (U):** np. `IS1A_UW03`
        * **KOMPETENCJE SPOŁECZNE (K):** np. `IS1A_KK01`
    * **Struktura Tabeli Efektów (sekcja 3 programu):** Tabela z 3 kolumnami (`Symbol | Kierunkowe efekty uczenia się | Sposoby weryfikacji i oceny efektów uczenia się`) podzielona na sekcje nagłówkami (wiersze z pustą kolumną Symbol):
        * "WIEDZA – absolwent zna i rozumie:" (Kategoria W)
        * "UMIEJĘTNOŚCI – absolwent potrafi:" (Kategoria U)
        * "KOMPETENCJE SPOŁECZNE – absolwent jest gotów do:" (Kategoria K)
    * **Kluczowa reguła:** Nagłówki sekcji identyfikowane są **wyłącznie** gdy kolumna `Symbol` jest pusta — opisy efektów mogą zawierać te same słowa kluczowe (np. "potrafi") i nie mogą być traktowane jako nagłówki.
* **Interaktywny Edytor:**
    * Wyświetla wyekstrahowane symbole (W, U, K) w formie **menu rozwijanego**.
    * Pozwala na **wielokrotny wybór** symboli z listy, z możliwością dodawania kolejnych pasujących.
    * Wyświetla **opis danego efektu** przy wyborze (jako pomoc), ale do dokumentu końcowego trafia jedynie sam symbol.
    * Wyświetla sekcje "Kierunkowe efekty uczenia się" i "Sposoby weryfikacji" jako pomoc dla użytkownika.
    * Pozwala na ręczne wypełnienie pól: `{{wiedza}}`, `{{umiejetnosci}}`, `{{kompetencje}}`, `{{cel_przedmiotu}}`, `{{metody_dydaktyczne}}`, `{{metody_weryfikacji}}`, `{{literatura}}`.
* **Eksport do Pliku:** Generowanie dokumentu na podstawie `template_pl.docx` i `template_en.docx` w zależności od języka wybranego przez użytkownika przy użyciu `docxtpl`. 

* **Wielojęzyczność:** Obsługa języka polskiego i angielskiego. Użytkownik może wybrać język dokumentu i AI generuje treści w wybranym języku.

---

Znaczenie tagów w szablonie:
{{ name }} - nazwa przedmiotu po polsku (dane skopiowne z programu studiów)
{{ ects }} - liczba ECTS (dane skopiowne z programu studiów)
{{ name_en }} - nazwa przedmiotu po angielsku (dane skopiowne z programu studiów, w razie potrzeby uzupełnia AI)
{{ unit }} - jednostka realizująca (dane skopiowne z programu studiów)
{{ kierownik }} - kierownik przedmiotu (dane uzupełnia użytkownik)
{{ field_of_study }} - kierunek studiów (dane skopiowne z programu studiów)
{{ level }} - poziom kształcenia (dane skopiowne z programu studiów)
{{ profile }} - profil kształcenia (dane skopiowne z programu studiów)
{{ semester }} - semestr (dane skopiowne z programu studiów)
{{ zakres }} - W zakresie / Specjalizacja magisterska / Moduł kształcenia
{{ numWS }} - liczba godzin wykładów na studiach stacjonarnych (dane skopiowne z planu studiów)
{{ numWNS }} - liczba godzin wykładów na studiach niestacjonarnych (dane skopiowne z planu studiów)
{{ numCS }} - liczba godzin ćwiczeń na studiach stacjonarnych (dane skopiowne z planu studiów)
{{ numCNS }} - liczba godzin ćwiczeń na studiach niestacjonarnych (dane skopiowne z planu studiów)
{{ numPS }} - liczba godzin terenowych na studiach stacjonarnych (dane skopiowne z planu studiów)
{{ numPNS }} - liczba godzin terenowych na studiach niestacjonarnych (dane skopiowne z planu studiów)
{{ numLS }}  - liczba godzin laboratoriów na studiach stacjonarnych (dane skopiowne z planu studiów)
{{ numLNS }} - liczba godzin laboratoriów na studiach niestacjonarnych (dane skopiowne z planu studiów)
{{ numKS }} - liczba godzin konsultacji na studiach stacjonarnych (dane skopiowne z planu studiów)
{{ numKNS }} - liczba godzin konsultacji na studiach niestacjonarnych (dane skopiowne z planu studiów)
{{ numPwS }} - liczba godzin praktyk na studiach stacjonarnych (dane skopiowne z planu studiów)
{{ numPwNS }} - liczba godzin praktyk na studiach niestacjonarnych (dane skopiowne z planu studiów)
{{ numInS }} - liczba godzin innych zajęć na studiach stacjonarnych (dane skopiowne z planu studiów)
{{ numInNS }} - liczba godzin innych zajęć na studiach niestacjonarnych (dane skopiowne z planu studiów)
{{ numTS  }} - całkowita liczba godzin zajęć na studiach stacjonarnych (dane skopiowne z planu studiów)
{{ numTNS }} - całkowita liczba godzin zajęć na studiach niestacjonarnych (dane skopiowne z planu studiów)
{{ cel_przedmiotu }} - cel przedmiotu (zadanie AI)
{{ metody_dydaktyczne }} - metody dydaktyczne (zadanie AI)
{{ wiedza }} - opis zdobytych kwalifikacji w zakresie wiedzy, przez absolwenta (zadanie AI)
{{ umiejetnosci }} - opis zdobytych kwalifikacji w zakresie umiejętności, przez absolwenta (zadanie AI)
{{ kompetencje }} - opis zdobytych kwalifikacji w zakresie kompetencji społecznych, przez absolwenta (zadanie AI)
{{ learning_outcomesW }} - kierunkowe efekty uczenia się w zakresie wiedzy (skopiowane z programu studiów)
{{ learning_outcomesU }} - kierunkowe efekty uczenia się w zakresie umiejętności (skopiowane z programu studiów)
{{ learning_outcomesK }} - kierunkowe efekty uczenia się w zakresie kompetencji społecznych (skopiowane z programu studiów)
{{ metody_weryfikacji }} - sposoby weryfikacji efektów uczenia się (zadanie AI)
{{ kursSym }} - symbole przedmiotowe powiązane z symbolami kierunkowymi. Dopasowanie symboli przedmiotowych do symboli kierunkowych jest dokonywane na podstawie analizy treści programowych (zadanie AI).
{{ content }} - treści programowe, przekazywane w ramach przedmiotu. Opis wykładów, ćwiczeń, laboratoriów, praktyk, konsultacji, samokształcenia, itp. (zadanie AI)
{{ formy_zaliczenia }} - W jaki sposób zorgonizowane będzie zaliczenie przedmiotu. Opis egzaminów, zaliczeń, itp. (czy egzamin ustny, test, zadania obliczeniowe, projekt) (wypełnia użytkownik)
{{ procOcena }} - procentowy udział poszczególnych form zaliczenia w ocenie końcowej (wypełnia użytkownik)
{{ literatura }} - literatura (wypełnia użytkownik)


---

#### **3. Stos Technologiczny i Implementacja**

* **Backend:** **Python (FastAPI)** + `python-docx` + `pdfplumber` + `docxtpl`.
    * Tagowanie w szablonie: `{{ learning_outcomesW }}`, `{{ learning_outcomesU }}`, `{{ learning_outcomesK }}` dla symboli.
* **Frontend:** **React (Vite)** + **TailwindCSS**.
    * Dynamiczny formularz synchronizowany w czasie rzeczywistym.
* **Logika Parsowania:** Obsługa "bloków tekstu" (regex) jako fallback gdy dokument nie posiada sformatowanych tabel.

---

#### **4. Architektura i Przepływ**

1.  **Frontend:** Upload -> `POST /api/process-document`.
2.  **Backend:** Parsowanie dokumentu -> Zwrócenie listy przedmiotów (JSON).
3.  **Frontend:** Wybór przedmiotu -> Edycja danych w formularzu.
4.  **Backend:** `POST /api/generate-syllabus` -> Renderowanie Jinja2 w Word -> Download.

---

#### **5. Kluczowe Wnioski z Rozwoju**

* **Składnia Szablonu:** Plik `template.docx` musi zawierać czyste tagi Jinja (unikać błędów typu `{{ {{ tag }} }}`).
* **Efekty Uczenia:** Automatyczna ekstrakcja powinna celować w sekcje opisowe "Efekty uczenia się osiągnięte przez studenta", ale ostateczna decyzja o treściach opisowych należy do użytkownika.
* **Formatowanie:** Generowany plik DOCX powinien zachowywać strukturę tabelaryczną sylabusu (szablon użytkownika).