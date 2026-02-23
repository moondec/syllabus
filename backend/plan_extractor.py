import re

def extract_data_from_plan_pdf(tables):
    """
    Extracts subject data from a list of tables from a plan PDF file.
    """
    subjects = []
    for table in tables:
        for row in table:
            # Heuristic to identify a subject row
            if len(row) > 16 and row[1] and row[1].isdigit():
                subject_name = row[0]

                # Filter out summary rows and rows with no name
                if not subject_name or "semestr łącznie" in subject_name.lower() or "razem na studiach" in subject_name.lower() or "semestr razem" in subject_name.lower() or not re.search('[a-zA-Z]', subject_name) or subject_name.isdigit():
                    continue

                ects = row[1]
                unit = row[16]
                
                hours_wyklad = 0
                if row[3] and row[3].isdigit():
                    hours_wyklad = int(row[3])

                hours_cwiczenia = 0
                # The classes hours are in columns 6, 7, 8, 9, 10, 11
                for i in range(6, 12):
                    if len(row) > i and row[i] and isinstance(row[i], str) and row[i].replace('L', '').replace('P', '').replace('T', '').isdigit():
                        hours_cwiczenia += int(row[i].replace('L', '').replace('P', '').replace('T', ''))
                        break

                subjects.append({
                    "name": subject_name,
                    "ects": ects,
                    "hours_lecture": hours_wyklad,
                    "hours_classes": hours_cwiczenia,
                    "unit": unit,
                })

    return subjects
