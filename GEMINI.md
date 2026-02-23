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
    * **Efekty Uczenia Się (Kluczowe):** Ekstrakcja symboli kierunkowych z podziałem na 3 kategorie:
        * **WIEDZA (W):** np. `P6S_WG01`
        * **UMIEJĘTNOŚCI (U):** np. `P6S_UW03`
        * **KOMPETENCJE SPOŁECZNE (K):** np. `P6S_KK01`
* **Interaktywny Edytor:**
    * Wyświetla wyekstrahowane symbole (W, U, K).
    * Wyświetla sekcje "Kierunkowe efekty uczenia się" i "Sposoby weryfikacji" jako pomoc dla użytkownika (bez wklejania ich do docelowego dokumentu).
    * Pozwala na ręczne wypełnienie pól: `{{wiedza}}`, `{{umiejętności}}`, `{{kompetencje}}`, `{{cel_przedmiotu}}`, `{{metody_dydaktyczne}}`, `{{metody_weryfikacji}}`, `{{literatura}}`.
* **Eksport do Pliku:** Generowanie dokumentu na podstawie `template.docx` przy użyciu `docxtpl`.

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