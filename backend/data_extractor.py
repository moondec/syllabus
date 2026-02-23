def extract_subject_data_from_docx(table):
    """
    Extracts subject data from a table from a DOCX file.
    The table is expected to have a specific header.
    """
    subjects = []
    header = [h.strip() for h in table[0]]
    
    # Find the column indices for the required data
    try:
        name_col = header.index("Nazwa przedmiotu")
        hours_col = header.index("Liczba godzin")
        ects_col = header.index("ECTS")
        outcomes_col = header.index("Odniesienie do kierunkowych efektów uczenia się")
    except ValueError as e:
        # Try another header format
        try:
            name_col = header.index("Nazwa przedmiotu")
            # In some docx, the hours are not in a column, but we can try to find it.
            # For now, let's assume it's not there if the first try fails.
            hours_col = -1 
            ects_col = header.index("ECTS")
            outcomes_col = header.index("Odniesienie do kierunkowych efektów uczenia się")
        except ValueError as e2:
            return {"error": f"Header column not found: {e} and {e2}"}


    # Iterate over the rows, skipping the header
    for row in table[1:]:
        # Basic check if the row is not empty and has enough columns
        if len(row) > max(name_col, ects_col, outcomes_col):
            subject_name = row[name_col]
            hours = row[hours_col] if hours_col != -1 else "N/A"
            ects = row[ects_col]
            learning_outcomes = row[outcomes_col]
            
            subjects.append({
                "name": subject_name,
                "hours": hours,
                "ects": ects,
                "learning_outcomes": learning_outcomes,
            })
        
    return subjects

def find_header_and_column_indices(row):
    """
    Identifies if a row is a header and returns the column indices for the required data.
    Returns a dictionary with indices or None if it's not a header.
    """
    row_text = " ".join(filter(None, row)).lower()
    header_keywords = ["nazwa przedmiotu", "ects"]

    if all(keyword in row_text for keyword in header_keywords):
        header = [h.strip().lower().replace('\n', ' ') if h else '' for h in row]
        indices = {}
        try:
            indices['name_col'] = [i for i, h in enumerate(header) if "nazwa przedmiotu" in h][0]
            indices['ects_col'] = header.index("ects")
            indices['outcomes_col'] = [i for i, h in enumerate(header) if "efektów" in h][0]
            # The "Liczba godzin" is not in the main table for PDFs, so I will have to find it elsewhere.
            # For now, I will set it to -1
            indices['hours_col'] = -1


            return indices
        except (ValueError, IndexError):
            return None
    return None

def extract_subject_data_from_pdf(tables):
    """
    Extracts subject data from a list of tables from a PDF file.
    """
    subjects = []
    header_indices = None
    
    for table in tables:
        for row in table:
            # Clean up the row from None values
            row = [cell.replace('\n', ' ') if cell else '' for cell in row]

            if header_indices is None:
                header_indices = find_header_and_column_indices(row)
                if header_indices is not None:
                    # Skip the header row itself
                    continue
            
            if header_indices and len(row) > max(header_indices.values()):
                subject_name = row[header_indices['name_col']]
                ects = row[header_indices['ects_col']]
                learning_outcomes = row[header_indices['outcomes_col']]
                
                # The hours are not in the table, so we set it to "N/A"
                hours = "N/A"

                # A simple check to see if it's a subject row
                if ects.isdigit():
                    subjects.append({
                        "name": subject_name,
                        "hours": hours,
                        "ects": ects,
                        "learning_outcomes": learning_outcomes,
                    })
                
    if not subjects:
        return {"error": "Could not extract any subject data. The table format might be unexpected."}
        
    return subjects
