import re

def extract_general_info(tables, text):
    """Extracts general information from the text and tables."""
    info = {}

    # Extract from text (Since PDF plumer often misses invisible-border tables)
    field_of_study_match = re.search(r"Nazwa kierunku studiów:\s*(.*)", text)
    if field_of_study_match:
        info["kierunek"] = field_of_study_match.group(1).strip()
    else:
        kierunek_match = re.search(r"Kierunek:\s*(.*?)(?=\n|Klasyfikacja|Dziedzina)", text)
        if kierunek_match:
            info["kierunek"] = kierunek_match.group(1).strip()

    level_match = re.search(r"Poziom kształcenia:\s*(.*?)(?=\n|Klasyfikacja|Tytuł)", text)
    if level_match:
        info["poziom"] = level_match.group(1).strip()
        
    profile_match = re.search(r"Profil kształcenia:\s*(.*?)(?=\n|Klasyfikacja|Tytuł)", text)
    if profile_match:
        info["profil"] = profile_match.group(1).strip()
        
    forma_match = re.search(r"Forma studiów:\s*(.*?)(?=\n|Klasyfikacja|Dyscyplina|Tytuł|Liczba)", text)
    if forma_match:
        info["forma"] = forma_match.group(1).strip()

    # Fallback to tables just in case a traditional docx table holds it
    if len(tables) > 0 and len(tables[0]) > 0:
        table1 = tables[0]
        for row in table1:
            for cell in row:
                if not cell: continue
                if "poziom" not in info:
                    lm = re.search(r"Poziom kształcenia:\s*(.*)", str(cell))
                    if lm: info["poziom"] = lm.group(1).strip()
                if "profil" not in info:
                    pm = re.search(r"Profil kształcenia:\s*(.*)", str(cell))
                    if pm: info["profil"] = pm.group(1).strip()
                if "forma" not in info:
                    fm = re.search(r"Forma studiów:\s*(.*)", str(cell))
                    if fm: info["forma"] = fm.group(1).strip()

    return info

def extract_outcomes_info(text):
    """
    Extracts symbols (W, U, K) and reference sections from text.
    """
    info = {
        "learning_outcomesW": "",
        "learning_outcomesU": "",
        "learning_outcomesK": "",
        "ref_kierunkowe": "",
        "ref_weryfikacja": ""
    }
    
    # Extract reference sections for UI help
    kierunkowe_match = re.search(r"(?i)Kierunkowe efekty uczenia się.*?(?=\n\n|\n\d+\.|\nSposoby)", text, re.DOTALL)
    if kierunkowe_match:
        info["ref_kierunkowe"] = kierunkowe_match.group(0).strip()
        
    weryfikacja_match = re.search(r"(?i)Sposoby weryfikacji i oceny.*?(?=\n\n|\n\d+\.)", text, re.DOTALL)
    if weryfikacja_match:
        info["ref_weryfikacja"] = weryfikacja_match.group(0).strip()

    # Extract symbols using regex
    # Looking for patterns like P6S_WG01, K1_W01, etc.
    all_symbols = re.findall(r"\b[A-Z0-9_]+_[WUK]\d+(?:\s+\d+)?\b", text)
    
    unique_w = sorted(list(set([s for s in all_symbols if "_W" in s])))
    unique_u = sorted(list(set([s for s in all_symbols if "_U" in s])))
    unique_k = sorted(list(set([s for s in all_symbols if "_K" in s])))
    
    info["learning_outcomesW"] = ", ".join(unique_w)
    info["learning_outcomesU"] = ", ".join(unique_u)
    info["learning_outcomesK"] = ", ".join(unique_k)
    
    return info

def extract_data_from_docx_v2(tables, text, pages=None):
    """
    Extracts subject data from a list of tables and text from a DOCX file.
    """
    general_info = extract_general_info(tables, text)
    outcomes_info = extract_outcomes_info(text)
    subjects = []
    
    tables_with_poziom = []
    if pages:
        current_poziom = general_info.get("poziom", "")
        for page_data in pages:
            page_text = page_data.get("text", "")
            poziom_match = re.search(r"(?i)poziom kształcenia:\s*(.*)", page_text)
            if poziom_match:
                found_poziom = poziom_match.group(1).split("Klasyfikacja")[0].split("Profil")[0].strip()
                current_poziom = found_poziom
            for t in page_data.get("tables", []):
                tables_with_poziom.append((t, current_poziom))
    else:
        for t in tables:
            tables_with_poziom.append((t, general_info.get("poziom", "")))

    # State machine variables
    name_col = -1
    ects_col = -1
    content_col = -1
    outcomes_col = -1
    unit_col = -1
    extracting = False
    
    for table, current_poziom in tables_with_poziom:
        for row_idx, row in enumerate(table):
            # Safe string join for the row to check if it's a header
            header_text = " ".join([str(c) for c in row if c is not None]).lower()
            
            if "nazwa przedmiotu" in header_text and "ects" in header_text:
                header = [str(h).strip().lower().replace('\n', ' ') for h in row if h is not None]
                try:
                    name_col = [i for i, h in enumerate(header) if "nazwa przedmiotu" in h][0]
                    ects_col = header.index("ects")
                    content_cols = [i for i, h in enumerate(header) if "treści programowe" in h]
                    content_col = content_cols[0] if content_cols else -1
                    outcomes_cols = [i for i, h in enumerate(header) if "efektów uczenia się" in h]
                    outcomes_col = outcomes_cols[0] if outcomes_cols else -1
                    unit_cols = [i for i, h in enumerate(header) if "jednostka realizująca" in h]
                    unit_col = unit_cols[0] if unit_cols else -1
                    extracting = True
                    continue # Skip the header row itself
                except (ValueError, IndexError):
                    extracting = False
                    continue

            # Jeśli przechodzimy do nowej tabeli (row_idx == 0),
            # musimy sprawdzić, czy nie jest to przypadkiem "tabela innego typu"
            if row_idx == 0 and extracting:
                stop_words = ["symbol", "sposoby weryfikacji", "rozliczenie godzin", "kierunkowe efekty uczenia", "kryteria oceny"]
                if any(sw in header_text for sw in stop_words):
                    extracting = False
                    continue

            if extracting:
                max_required_col = max(name_col, ects_col)
                if len(row) > max_required_col:
                    name_val = str(row[name_col]) if row[name_col] is not None else ""
                    ects_val = str(row[ects_col]) if row[ects_col] is not None else ""
                    
                    if not name_val.strip() or "nazwa przedmiotu" in name_val.lower():
                        continue
                        
                    name_and_sem = name_val.split('\n')
                    subject_name = ""
                    semester = ""
                    if len(name_and_sem) > 0:
                        match = re.match(r"(\d)\.", name_and_sem[0])
                        if match:
                            semester = match.group(1)
                        subject_name = " ".join(name_and_sem)

                    english_name = ""
                    if len(name_and_sem) > 1:
                        if all(c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ " for c in name_and_sem[1]):
                            english_name = name_and_sem[1]

                    tresci_val = str(row[content_col]) if content_col != -1 and len(row) > content_col and row[content_col] else ""
                    efekty_val = str(row[outcomes_col]) if outcomes_col != -1 and len(row) > outcomes_col and row[outcomes_col] else ""
                    unit_val = str(row[unit_col]) if unit_col != -1 and len(row) > unit_col and row[unit_col] else ""

                    subject_info = {
                        "nazwa_przedmiotu": subject_name.strip(),
                        "nazwa_angielska": english_name.strip(),
                        "semestr": semester.strip(),
                        "ects": ects_val.strip(),
                        "tresci": tresci_val.strip(),
                        "efekty": efekty_val.strip(),
                        "jednostka": unit_val.strip(),
                        "cel_przedmiotu": "",
                        "zalozenia": "",
                        "metody_dydaktyczne": "",
                        "metody_weryfikacji": "",
                        "literatura": "",
                        "wiedza": "",
                        "umiejetnosci": "",
                        "kompetencje": ""
                    }
                    subject_info.update(general_info)
                    subject_info.update(outcomes_info)
                    if current_poziom:
                        subject_info["poziom"] = current_poziom
                    subjects.append(subject_info)

    if not subjects:
        import text_parser
        return text_parser.extract_subjects_from_text(text)

    return subjects
