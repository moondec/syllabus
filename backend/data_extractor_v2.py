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
    Extracts reference sections from text.
    """
    info = {
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
    
    return info

def _parse_outcomes_table(table):
    """
    Parses a single outcomes table (Symbol | Kierunkowe efekty | Sposoby weryfikacji).
    Returns a dict {"W": [...], "U": [...], "K": [...]}.
    Each entry has: symbol, description, verification.
    """
    outcomes = {"W": [], "U": [], "K": []}
    current_category = None
    
    header = table[0]
    header_text = " ".join([str(c) for c in header if c is not None]).lower()
    
    is_outcomes_table = (
        (("symbol" in header_text or "kod" in header_text) and "efekt" in header_text) or
        "sposoby weryfikacji" in header_text
    ) and "nazwa przedmiotu" not in header_text
    
    if not is_outcomes_table:
        return None
    
    # Find columns
    symbol_col = -1
    desc_col = -1
    verif_col = -1
    for i, col_name in enumerate(header):
        c_name = str(col_name).lower()
        if "symbol" in c_name or "kod" in c_name:
            symbol_col = i
        elif "weryfik" in c_name or "sposoby" in c_name:
            verif_col = i
        elif "efekt" in c_name:
            desc_col = i
    
    if desc_col == -1:
        for i, col_name in enumerate(header):
            if "kierunkow" in str(col_name).lower():
                desc_col = i
    
    if symbol_col == -1 or desc_col == -1:
        return None
    
    for row in table[1:]:
        sym_raw = str(row[symbol_col]).strip() if row[symbol_col] else ""
        
        # Section headers have EMPTY symbol column
        if not sym_raw:
            row_text = " ".join([str(c) for c in row if c]).lower()
            if "wiedza" in row_text and ("zna" in row_text or "rozumie" in row_text):
                current_category = "W"
            elif ("umiejętności" in row_text or "umiejetnosci" in row_text) and "potrafi" in row_text:
                current_category = "U"
            elif ("kompetencje" in row_text) and ("gotów" in row_text or "gotow" in row_text):
                current_category = "K"
            continue
            
        if len(row) > max(symbol_col, desc_col):
            sym = sym_raw
            desc = str(row[desc_col]).strip() if row[desc_col] else ""
            verif = str(row[verif_col]).strip() if verif_col != -1 and len(row) > verif_col and row[verif_col] else ""
            
            if sym and len(sym) < 20:
                sym = sym.replace(" ", "")
                cat = current_category
                if not cat:
                    if "_W" in sym: cat = "W"
                    elif "_U" in sym: cat = "U"
                    elif "_K" in sym: cat = "K"
                
                if cat:
                    outcomes[cat].append({"symbol": sym, "description": desc, "verification": verif})
    
    return outcomes


def extract_detailed_outcomes(tables, pages=None):
    """
    Extracts detailed (Symbol, Description) pairs per degree level.
    
    Returns dict keyed by normalized level string:
      {
        "studia pierwszego stopnia": {"W": [...], "U": [...], "K": [...]},
        "studia drugiego stopnia":   {"W": [...], "U": [...], "K": [...]},
        "": {"W": [...], ...}  # fallback when no level detected
      }
    """
    outcomes_by_level = {}
    
    if pages:
        # PDF path: track level per page
        current_poziom = ""
        in_outcomes_section = False  # True when we found an outcomes table and are expecting continuations
        current_category = None  # Track W/U/K across page breaks
        
        for page_data in pages:
            page_text = page_data.get("text", "")
            poziom_match = re.search(r"(?i)poziom kształcenia:\s*(.*?)(?:\n|Klasyfikacja|$)", page_text)
            if poziom_match:
                found = poziom_match.group(1).split("Klasyfikacja")[0].split("Profil")[0].strip()
                current_poziom = found
                in_outcomes_section = False  # New level section resets
                current_category = None
            
            for table in page_data.get("tables", []):
                if not table or len(table) < 2:
                    continue
                parsed = _parse_outcomes_table(table)
                if parsed:
                    in_outcomes_section = True
                    current_category = None
                    if current_poziom not in outcomes_by_level:
                        outcomes_by_level[current_poziom] = {"W": [], "U": [], "K": []}
                    for cat in ["W", "U", "K"]:
                        outcomes_by_level[current_poziom][cat].extend(parsed[cat])
                        # Track last category
                        if parsed[cat]:
                            current_category = cat
                elif in_outcomes_section:
                    # This might be a continuation table (no header row, split by PDF page)
                    # Check if first row looks like outcomes data (short symbol + longer text)
                    first_row = table[0]
                    if len(first_row) >= 2:
                        first_cell = str(first_row[0]).strip() if first_row[0] else ""
                        # Continuation rows: either a symbol or a section header
                        if first_cell and (len(first_cell) < 20 or not first_cell):
                            if current_poziom not in outcomes_by_level:
                                outcomes_by_level[current_poziom] = {"W": [], "U": [], "K": []}
                            
                            for row in table:
                                sym_raw = str(row[0]).strip() if row[0] else ""
                                row_text = " ".join([str(c) for c in row if c]).lower()
                                
                                # Check for section headers FIRST (may appear in col 0 in PDF)
                                is_header = False
                                if "wiedza" in row_text and ("zna" in row_text or "rozumie" in row_text):
                                    current_category = "W"
                                    is_header = True
                                elif ("umiejętności" in row_text or "umiejetnosci" in row_text) and "potrafi" in row_text:
                                    current_category = "U"
                                    is_header = True
                                elif ("kompetencje" in row_text) and ("gotów" in row_text or "gotow" in row_text):
                                    current_category = "K"
                                    is_header = True
                                
                                if is_header or not sym_raw:
                                    continue
                                
                                desc = str(row[1]).strip() if len(row) > 1 and row[1] else ""
                                sym = sym_raw.replace(" ", "")
                                
                                if sym and len(sym) < 20:
                                    cat = current_category
                                    if not cat:
                                        if "_W" in sym: cat = "W"
                                        elif "_U" in sym: cat = "U"
                                        elif "_K" in sym: cat = "K"
                                    
                                    if cat:
                                        current_category = cat
                                        outcomes_by_level[current_poziom][cat].append({"symbol": sym, "description": desc})
                        else:
                            in_outcomes_section = False  # Not a continuation, stop
    else:
        # DOCX path: scan all tables, detect level from info tables
        current_poziom = ""
        for table in tables:
            if not table or len(table) < 1:
                continue
            
            # Check if this table contains a "Poziom kształcenia" marker
            for row in table:
                for cell in row:
                    if cell:
                        pm = re.search(r"(?i)poziom kształcenia:\s*(.*)", str(cell))
                        if pm:
                            current_poziom = pm.group(1).split("Klasyfikacja")[0].split("Profil")[0].strip()
            
            # Try to parse as outcomes table
            if len(table) >= 2:
                parsed = _parse_outcomes_table(table)
                if parsed:
                    if current_poziom not in outcomes_by_level:
                        outcomes_by_level[current_poziom] = {"W": [], "U": [], "K": []}
                    for cat in ["W", "U", "K"]:
                        outcomes_by_level[current_poziom][cat].extend(parsed[cat])
    
    # If only one level found, return it directly for backward compatibility
    return outcomes_by_level


def extract_data_from_docx_v2(tables, text, pages=None):
    """
    Extracts subject data from a list of tables and text from a DOCX file.
    """
    general_info = extract_general_info(tables, text)
    outcomes_info = extract_outcomes_info(text)
    detailed_outcomes_by_level = extract_detailed_outcomes(tables, pages)
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
        # DOCX: track level per table from info tables (e.g. Table 0)
        current_poziom = general_info.get("poziom", "")
        for t in tables:
            # Check if this table contains a "Poziom kształcenia" marker
            if t:
                for row in t:
                    for cell in row:
                        if cell:
                            pm = re.search(r"(?i)poziom kształcenia:\s*(.*)", str(cell))
                            if pm:
                                current_poziom = pm.group(1).split("Klasyfikacja")[0].split("Profil")[0].strip()
            tables_with_poziom.append((t, current_poziom))

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
                    
                    # Identify ALL outcomes symbols columns (avoid matching the content column)
                    outcomes_cols = []
                    for i, h in enumerate(header):
                        if ("efektów uczenia się" in h or "symbol" in h or "odniesienie" in h) and "treści" not in h:
                            outcomes_cols.append(i)
                    
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
                    
                    efekty_parts = []
                    for col_idx in outcomes_cols:
                        if len(row) > col_idx and row[col_idx]:
                            efekty_parts.append(str(row[col_idx]))
                    efekty_val = " ".join(efekty_parts)
                    
                    unit_val = str(row[unit_col]) if unit_col != -1 and len(row) > unit_col and row[unit_col] else ""

                    # Match available_outcomes to this subject's degree level
                    available_outcomes = detailed_outcomes_by_level.get(current_poziom, {"W": [], "U": [], "K": []})
                    # Fallback: if no match by level and only one level exists, use that
                    if not any(available_outcomes[c] for c in ["W", "U", "K"]) and len(detailed_outcomes_by_level) == 1:
                        available_outcomes = list(detailed_outcomes_by_level.values())[0]

                    # Extract this subject's specific outcomes from its 'efekty' cell
                    subject_symbols = re.findall(r"\b[A-Z0-9_]+_[WUK]\d{1,2}\b", efekty_val)
                    subj_w = sorted(list(set([s for s in subject_symbols if "_W" in s])))
                    subj_u = sorted(list(set([s for s in subject_symbols if "_U" in s])))
                    subj_k = sorted(list(set([s for s in subject_symbols if "_K" in s])))

                    # Build symbol→verification lookup from available_outcomes
                    verif_lookup = {}
                    for cat in ["W", "U", "K"]:
                        for o in available_outcomes.get(cat, []):
                            if o.get("verification"):
                                verif_lookup[o["symbol"]] = o["verification"]
                    
                    # Pre-fill metody_weryfikacji from this subject's symbols
                    all_subj_symbols = subj_w + subj_u + subj_k
                    verif_texts = []
                    seen_verif = set()
                    for sym in all_subj_symbols:
                        vt = verif_lookup.get(sym, "")
                        if vt and vt not in seen_verif:
                            seen_verif.add(vt)
                            verif_texts.append(f"{sym}: {vt}")
                    metody_weryfikacji_val = "\n".join(verif_texts)

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
                        "metody_weryfikacji": metody_weryfikacji_val,
                        "literatura": "",
                        "wiedza": "",
                        "umiejetnosci": "",
                        "kompetencje": "",
                        "learning_outcomesW": ", ".join(subj_w),
                        "learning_outcomesU": ", ".join(subj_u),
                        "learning_outcomesK": ", ".join(subj_k),
                    }
                    subject_info.update(general_info)
                    subject_info.update(outcomes_info)
                    subject_info["available_outcomes"] = available_outcomes
                    if current_poziom:
                        subject_info["poziom"] = current_poziom
                    subjects.append(subject_info)

    if not subjects:
        import text_parser
        return text_parser.extract_subjects_from_text(text)

    return subjects
