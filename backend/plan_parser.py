import re
import logging

logger = logging.getLogger(__name__)

# Minimum number of valid subjects to consider a parse successful
MIN_SUBJECTS_THRESHOLD = 10


def extract_plan_metadata(text):
    """
    Extracts study mode (stacjonarne/niestacjonarne) and degree level
    from pre-table text in a plan PDF.
    Returns: {"tryb": "S" or "NS", "poziom": str}
    """
    metadata = {"tryb": "S", "poziom": ""}

    # Detect mode
    text_lower = text.lower()
    if "niestacjonarn" in text_lower:
        metadata["tryb"] = "NS"
    elif "stacjonarn" in text_lower:
        metadata["tryb"] = "S"

    # Detect degree level
    level_match = re.search(r"(?:studia|studiów)\s+(I+[°o]?|pierwszego stopnia|drugiego stopnia|II[°o]?)", text, re.IGNORECASE)
    if level_match:
        raw = level_match.group(1).strip()
        if "II" in raw or "drugiego" in raw.lower():
            metadata["poziom"] = "studia drugiego stopnia"
        else:
            metadata["poziom"] = "studia pierwszego stopnia"
    else:
        # Fallback: search for "I stopnia" / "II stopnia" pattern in title lines
        fallback = re.search(r"(I+)\s*stopnia", text, re.IGNORECASE)
        if fallback:
            raw = fallback.group(1).strip()
            if "II" in raw:
                metadata["poziom"] = "studia drugiego stopnia"
            else:
                metadata["poziom"] = "studia pierwszego stopnia"

    # Detect field of study
    kierunek_match = re.search(r"(?:kierunek|kierunku)[:\s]+([^\n]+)", text, re.IGNORECASE)
    if kierunek_match:
        raw_kierunek = kierunek_match.group(1).strip()
        # Remove common prefix artifacts like "studi\u00f3w:"
        raw_kierunek = re.sub(r"^studi\u00f3w[:\s]*", "", raw_kierunek, flags=re.IGNORECASE).strip()
        metadata["kierunek"] = raw_kierunek

    return metadata


def _is_header_row(row):
    """Check if a row is a table header (contains column number markers like '1 2 3 4...')."""
    row_text = " ".join([str(c) for c in row if c]).strip()
    # Header rows with column numbers: "1 2 3 4 5 6 7 8 9 10 11"
    if re.match(r"^[\d\s]+$", row_text) and len(row_text) > 5:
        return True
    # Rows with keywords like "Nazwa modułu", "ECTS", "Liczba godzin"
    row_lower = row_text.lower()
    if "nazwa modułu" in row_lower or "liczba godzin" in row_lower or "łącznie" in row_lower:
        return True
    if "wykł" in row_lower or "zajęcia dydaktyczne" in row_lower:
        return True
    return False


def _is_summary_row(name):
    """Check if a row is a summary/total row."""
    if not name:
        return True
    name_lower = name.lower().strip()
    skip_patterns = [
        "semestr łącznie", "łącznie", "razem na studiach", "semestr razem",
        "razem", "suma", "ogółem", "total"
    ]
    return any(p in name_lower for p in skip_patterns)


def _is_semester_marker(row):
    """Check if a row marks a new semester."""
    first_cell = str(row[0]).strip().lower() if row[0] else ""
    row_text = " ".join([str(c) for c in row if c]).strip().lower()
    if re.match(r"semestr\s+\d+", first_cell):
        return True
    if re.match(r"semestr\s+\d+", row_text) and sum(1 for c in row if c and str(c).strip()) <= 2:
        return True
    return False


def _parse_semester_number(row):
    """Extract semester number from a semester marker row."""
    row_text = " ".join([str(c) for c in row if c]).strip()
    match = re.search(r"semestr\s+(\d+)", row_text, re.IGNORECASE)
    return match.group(1) if match else ""


def _safe_int(val):
    """Parse an integer from a cell value, stripping any letter codes (L, P, T, A, etc.)."""
    if not val:
        return 0
    val = str(val).strip()
    if not val:
        return 0
    # Remove letter suffixes: "30A" -> "30", "15L" -> "15", "12P" -> "12"
    digits = re.sub(r"[^0-9]", "", val)
    return int(digits) if digits else 0


def _parse_exercise_type(val):
    """Extract exercise type codes from a cell (A, L, LK, P, T)."""
    if not val:
        return ""
    val = str(val).strip()
    # Find all type codes
    codes = re.findall(r"[A-Z]+", val)
    return ",".join(codes) if codes else ""


def _split_name(raw_name):
    """
    Split a subject name like 'Matematyka C1 / Mathematics C1' into PL and EN parts.
    Returns (name_pl, name_en).
    """
    if not raw_name:
        return "", ""
    # Remove leading number like "1. " or "12. "
    name = re.sub(r"^\d+\.\s*", "", raw_name).strip()
    # Remove newlines
    name = name.replace("\n", " ").strip()

    if " / " in name:
        parts = name.split(" / ", 1)
        return parts[0].strip(), parts[1].strip()
    return name, ""


def _auto_detect_columns(row, compressed_row):
    """Heuristic auto-detection of column roles based on cell content.
    
    Tries to identify Name, ECTS, Total, Wykład, Ćwiczenia, Inne,
    Konsultacje, PracaWłasna, and Jednostka columns by analyzing
    what each cell contains.
    
    Returns a dict of column assignments or None if detection fails.
    Uses the raw row (not compressed) for column indices.
    """
    if len(compressed_row) < 5:
        return None
    
    # Strategy: find the first cell with letters (name), then scan
    # subsequent cells for numeric patterns
    name_idx = None
    for i, cell in enumerate(row):
        val = str(cell).strip() if cell else ""
        # Name: has letters and is reasonably long, or is a numbered item like "1. Name"
        if re.search(r'[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]{2,}', val) and len(val) > 3:
            name_idx = i
            break
    
    if name_idx is None:
        return None
    
    # Scan cells after name for numeric values
    numeric_cols = []  # list of (col_index, int_value)
    text_cols = []     # list of (col_index, text_value) — for unit at the end
    
    for i in range(name_idx + 1, len(row)):
        val = str(row[i]).strip() if row[i] else ""
        digits = re.sub(r'[^0-9]', '', val)
        if digits and digits.isdigit():
            numeric_cols.append((i, int(digits)))
        elif val and re.search(r'[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]', val):
            text_cols.append((i, val))
    
    if len(numeric_cols) < 2:
        return None
    
    # First numeric should be ECTS (1-30), second should be Total hours
    ects_idx, ects_val = numeric_cols[0]
    if not (1 <= ects_val <= 30):
        return None
    
    total_idx = numeric_cols[1][0] if len(numeric_cols) > 1 else None
    
    # Remaining numeric columns: wykład, ćwiczenia, inne, konsultacje, praca_własna
    hour_cols = numeric_cols[2:]  # skip ECTS and Total
    
    wyklad_idx = hour_cols[0][0] if len(hour_cols) > 0 else None
    cwicz_idx = hour_cols[1][0] if len(hour_cols) > 1 else None
    inne_idx = hour_cols[2][0] if len(hour_cols) > 2 else None
    konsult_idx = hour_cols[3][0] if len(hour_cols) > 3 else None
    praca_wlasna_idx = hour_cols[4][0] if len(hour_cols) > 4 else None
    
    # Unit: last text column (typically department/institute)
    unit_idx = text_cols[-1][0] if text_cols else None
    
    return {
        "name_col": name_idx,
        "ects_col": ects_idx,
        "total_col": total_idx,
        "wyklad_col": wyklad_idx,
        "cwicz_col": cwicz_idx,
        "inne_col": inne_idx,
        "konsult_col": konsult_idx,
        "praca_wlasna_col": praca_wlasna_idx,
        "unit_col": unit_idx,
        "typ_col": None,
    }


def extract_plan_subjects(pages_data, metadata=None):
    """
    Extracts per-subject hour data from plan PDF tables.
    
    Args:
        pages_data: list of {"text": str, "tables": list} from file_parser.parse_pdf
        metadata: optional pre-computed metadata dict
    
    Returns: list of subject dicts with hour fields mapped to template tags.
    """
    if metadata is None:
        # Try to get metadata from first page text
        all_text = " ".join([p.get("text", "") for p in pages_data[:2]])
        metadata = extract_plan_metadata(all_text)

    # Use override_tryb if provided, otherwise use metadata
    tryb = metadata.get("tryb", "S")
    if metadata.get("override_tryb"):
        tryb = metadata["override_tryb"]

    subjects = []
    current_semester = ""
    past_header = False  # Track if we've seen the header rows

    for page_data in pages_data:
        for table in page_data.get("tables", []):
            if not table:
                continue

            num_cols = len(table[0]) if table else 0

            for row in table:
                if not row or len(row) < 3:
                    continue

                # Skip header rows
                if _is_header_row(row):
                    past_header = True
                    continue

                # Check for semester markers
                if _is_semester_marker(row):
                    current_semester = _parse_semester_number(row)
                    continue

                # Clean up and compress the row to handle empty joining columns from pdfplumber
                raw_row = [str(c) if c is not None else "" for c in row]
                compressed_row = [c.strip() for c in raw_row if c.strip()]
                num_compressed = len(compressed_row)

                # Determine column layout based on table width or compressed width
                name_col = None
                ects_col = None
                total_col = None
                wyklad_col = None
                cwicz_col = None
                typ_col = None
                inne_col = None
                konsult_col = None
                praca_wlasna_col = None
                unit_col = None
                
                # Check compressed row layout (for "OŚ I stopień" and similar)
                if num_compressed == 11 and compressed_row[0].split('.')[0].isdigit() and compressed_row[1].isdigit():
                    # 11-column compressed layout
                    # Format: Name, ECTS, Total, Wykład, Ćwiczenia, Inne, Konsultacje, Praca własna, Egz/Zal, Typ, Jednostka
                    name_col = "compressed:0"
                    ects_col = "compressed:1"
                    total_col = "compressed:2"
                    wyklad_col = "compressed:3"
                    cwicz_col = "compressed:4"
                    inne_col = "compressed:5"
                    konsult_col = "compressed:6"
                    praca_wlasna_col = "compressed:7"
                    typ_col = "compressed:9"
                    unit_col = "compressed:10"
                elif num_compressed == 10 and "fakultet" in compressed_row[0].lower():
                    # 10-col compressed for facultative blocks (missing some columns like formy_zaliczenia often)
                     name_col = "compressed:0"
                     ects_col = "compressed:1"
                     total_col = "compressed:2"
                     wyklad_col = "compressed:3"
                     cwicz_col = "compressed:4"
                     inne_col = "compressed:5"
                     konsult_col = "compressed:6"
                     praca_wlasna_col = "compressed:7"
                     typ_col = "compressed:8"
                     unit_col = "compressed:9"
                elif num_cols >= 17:
                    # 17-column layout (niestacjonarne-style, wider table)
                    name_col = 0
                    ects_col = 1
                    total_col = 2
                    wyklad_col = 3
                    cwicz_col = 6
                    typ_col = None  # Exercise type embedded in cwicz value
                    inne_col = 9
                    konsult_col = 12
                    praca_wlasna_col = 13
                    unit_col = 16
                elif num_cols >= 14:
                    # 14-column layout (stacjonarne/niestacjonarne, landscape)
                    # col0=nr, col1=name, col2=ECTS, col3=total, col4=wykł, col5=ćw,
                    # col6=typ, col7=inne1, col8=(empty), col9=konsult, col10=praca_własna,
                    # col11=forma, col12=typ_grupy, col13=jednostka
                    name_col = 1 if (row[0] and str(row[0]).strip().replace(".", "").isdigit()) else 0
                    if name_col == 1:
                        ects_col = 2
                        total_col = 3
                        wyklad_col = 4
                        cwicz_col = 5
                        typ_col = 6
                        inne_col = 7
                        konsult_col = 9
                        praca_wlasna_col = 10
                        unit_col = 13
                    else:
                        ects_col = 2
                        total_col = 3
                        wyklad_col = 4
                        cwicz_col = 5
                        typ_col = 6
                        inne_col = 7
                        konsult_col = 9
                        praca_wlasna_col = 10
                        unit_col = 13
                elif num_cols == 13:
                    # 13-column layout — II stopień portrait (vertical page)
                    # col0=nr, col1=name, col2=ECTS, col3=total, col4=wykł, col5=ćw,
                    # col6=typ_ćw, col7=inne1(empty), col8=konsult, col9=praca_własna,
                    # col10=forma, col11=typ_grupy, col12=jednostka
                    name_col = 1 if (row[0] and str(row[0]).strip().replace(".", "").isdigit()) else 0
                    if name_col == 1:
                        ects_col = 2
                        total_col = 3
                        wyklad_col = 4
                        cwicz_col = 5
                        typ_col = 6
                        inne_col = 7
                        konsult_col = 8
                        praca_wlasna_col = 9
                        unit_col = 12
                    else:
                        ects_col = 1
                        total_col = 2
                        wyklad_col = 3
                        cwicz_col = 4
                        typ_col = 5
                        inne_col = 6
                        konsult_col = 7
                        praca_wlasna_col = 8
                        unit_col = 11
                elif num_cols == 11:
                    # 11-column layout directly from DOCX tables
                    name_col = 0
                    ects_col = 1
                    total_col = 2
                    wyklad_col = 3
                    cwicz_col = 4
                    inne_col = 5
                    konsult_col = 6
                    praca_wlasna_col = 7
                    typ_col = 8
                    unit_col = 10
                elif num_cols == 10:
                    # 10-column layout (e.g. English-language plans like Geoinformation)
                    # col0=Name, col1=ECTS, col2=Total, col3=Lectures, col4=PractClasses,
                    # col5=Others, col6=ContactHours, col7=ESW/SelfWork, col8=Assessment, col9=Unit
                    name_col = 0
                    ects_col = 1
                    total_col = 2
                    wyklad_col = 3
                    cwicz_col = 4
                    inne_col = 5
                    konsult_col = 6
                    praca_wlasna_col = 7
                    typ_col = None
                    unit_col = 9
                else:
                    # Unknown column count — try auto-detection based on content
                    detected = _auto_detect_columns(raw_row, compressed_row)
                    if detected:
                        name_col = detected["name_col"]
                        ects_col = detected["ects_col"]
                        total_col = detected["total_col"]
                        wyklad_col = detected["wyklad_col"]
                        cwicz_col = detected["cwicz_col"]
                        inne_col = detected["inne_col"]
                        konsult_col = detected["konsult_col"]
                        praca_wlasna_col = detected["praca_wlasna_col"]
                        unit_col = detected["unit_col"]
                        typ_col = detected["typ_col"]
                    else:
                        continue  # Truly unrecognizable row
                    
                def get_val(col_idx):
                    if col_idx is None:
                        return ""
                    if isinstance(col_idx, str) and col_idx.startswith("compressed:"):
                        idx = int(col_idx.split(":")[1])
                        return compressed_row[idx] if idx < len(compressed_row) else ""
                    return str(row[col_idx]).strip() if col_idx < len(row) and row[col_idx] else ""

                # Get subject name
                raw_name = get_val(name_col)


                # Must have at least ECTS to be a valid subject row
                ects_val = get_val(ects_col)
                if not ects_val or not ects_val.isdigit():
                    continue

                # Parse hours
                total_hours = _safe_int(get_val(total_col))
                wyklad_hours = _safe_int(get_val(wyklad_col))
                cwicz_hours = _safe_int(get_val(cwicz_col))
                inne_hours = _safe_int(get_val(inne_col))
                konsult_hours = _safe_int(get_val(konsult_col))
                selfwork_hours = _safe_int(get_val(praca_wlasna_col))

                # Unit
                unit_val = get_val(unit_col)

                def _get_subject_names(full_name):
                    """Splits combined subject names into a list of separate subject strings."""
                    # Use regex to find markers like "1.3.1. ", "2.2A. ", "2. Fakultet"
                    markers = list(re.finditer(r"(\d+[\.\w]+[\.\s]+)", full_name))
                    if len(markers) <= 1:
                        return [full_name]
                    
                    # Shared prefix check
                    prefix = ""
                    if markers[0].start() > 0:
                        prefix = full_name[:markers[0].start()].strip()
                    
                    results = []
                    for i in range(len(markers)):
                        start_idx = markers[i].start()
                        end_idx = markers[i+1].start() if i+1 < len(markers) else len(full_name)
                        item = full_name[start_idx:end_idx].strip()
                        if prefix:
                            results.append(f"{prefix} {item}".strip())
                        else:
                            results.append(item)
                    return results

                # Get all individual subjects from this row
                raw_names = _get_subject_names(raw_name)

                for name_entry in raw_names:
                    if not name_entry or _is_summary_row(name_entry):
                        continue
                    if name_entry.replace(".", "").strip().isdigit():
                        continue
                    
                    name_pl, name_en = _split_name(name_entry)

                    # Build subject dict
                    subject = {
                        "nazwa_przedmiotu": name_pl,
                        "nazwa_angielska": name_en,
                        "ects": ects_val,
                        "semestr": current_semester,
                        "jednostka": unit_val,
                    }

                    # Map hours to template tags
                    if tryb == "NS":
                        subject["numTNS"] = str(total_hours) if total_hours else ""
                        subject["numWNS"] = str(wyklad_hours) if wyklad_hours else ""
                        subject["numCNS"] = str(cwicz_hours) if cwicz_hours else ""
                        subject["numInNS"] = str(inne_hours) if inne_hours else ""
                        subject["numKNS"] = str(konsult_hours) if konsult_hours else ""
                        subject["numPwNS"] = str(selfwork_hours) if selfwork_hours else ""
                    else:
                        subject["numTS"] = str(total_hours) if total_hours else ""
                        subject["numWS"] = str(wyklad_hours) if wyklad_hours else ""
                        subject["numCS"] = str(cwicz_hours) if cwicz_hours else ""
                        subject["numInS"] = str(inne_hours) if inne_hours else ""
                        subject["numKS"] = str(konsult_hours) if konsult_hours else ""
                        subject["numPwS"] = str(selfwork_hours) if selfwork_hours else ""

                    subjects.append(subject)

    return subjects


def extract_full_plan(parsed_pdf, override_tryb=None, file_path=None):
    """
    Main entry point: takes the output of file_parser.parse_pdf() and returns
    a dict with metadata and subjects.
    
    If file_path is provided and the initial parse yields fewer than
    MIN_SUBJECTS_THRESHOLD subjects, the PDF will be re-parsed with
    adjusted pdfplumber settings (snap_tolerance=6) which merges
    narrow phantom columns, normalizing diverse layouts to ~11 cols.
    """
    pages = parsed_pdf.get("pages")
    if pages is None:
        pages = [{"text": parsed_pdf.get("content", ""), "tables": parsed_pdf.get("tables", [])}]
    text = parsed_pdf.get("content", "")

    metadata = extract_plan_metadata(text)
    if override_tryb:
        metadata["override_tryb"] = override_tryb

    # Phase 1: try with default-parsed data
    subjects = extract_plan_subjects(pages, metadata)
    
    # Phase 2: if too few subjects found and we have a file path, try adaptive reparsing
    if len(subjects) < MIN_SUBJECTS_THRESHOLD and file_path:
        import file_parser
        
        adaptive_settings = [
            # snap_tolerance=6 merges narrow phantom columns (17→11, 33→11)
            {"snap_x_tolerance": 6, "snap_y_tolerance": 6},
            # Higher snap for very noisy PDFs
            {"snap_x_tolerance": 10, "snap_y_tolerance": 10},
            # Even more aggressive merging
            {"snap_x_tolerance": 15, "snap_y_tolerance": 15},
        ]
        
        best_subjects = subjects
        
        for settings in adaptive_settings:
            try:
                reparsed = file_parser.parse_pdf_with_settings(file_path, table_settings=settings)
                if reparsed.get("error"):
                    continue
                
                reparsed_pages = reparsed.get("pages")
                if reparsed_pages is None:
                    reparsed_pages = [{"text": reparsed.get("content", ""), "tables": reparsed.get("tables", [])}]
                
                candidate = extract_plan_subjects(reparsed_pages, metadata)
                
                logger.info(
                    f"Adaptive reparse with {settings}: found {len(candidate)} subjects "
                    f"(previous best: {len(best_subjects)})"
                )
                
                if len(candidate) > len(best_subjects):
                    best_subjects = candidate
                
                # Early stop if we found enough subjects
                if len(best_subjects) >= MIN_SUBJECTS_THRESHOLD:
                    break
                    
            except Exception as e:
                logger.warning(f"Adaptive reparse failed with {settings}: {e}")
                continue
        
        subjects = best_subjects

    return {
        "metadata": metadata,
        "subjects": subjects
    }
