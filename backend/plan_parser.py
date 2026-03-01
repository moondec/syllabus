import re


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
                    # 14-column layout (stacjonarne-style)
                    name_col = 1 if (row[0] and str(row[0]).strip().replace(".", "").isdigit()) else 0
                    if name_col == 1:
                        # Row starts with number: col0=nr, col1=name
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
                        # Row starts with name directly (continuation)
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
                    continue  # Unknown format
                    
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


def extract_full_plan(parsed_pdf, override_tryb=None):
    """
    Main entry point: takes the output of file_parser.parse_pdf() and returns
    a dict with metadata and subjects.
    """
    pages = parsed_pdf.get("pages", [])
    text = parsed_pdf.get("content", "")

    metadata = extract_plan_metadata(text)
    if override_tryb:
        metadata["override_tryb"] = override_tryb
        
    subjects = extract_plan_subjects(pages, metadata)

    return {
        "metadata": metadata,
        "subjects": subjects
    }
