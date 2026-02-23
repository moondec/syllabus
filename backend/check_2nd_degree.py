from file_parser import parse_pdf
from data_extractor_v2 import extract_data_from_docx_v2

data_pdf = parse_pdf('../programs/1-st-2-st-lesnictwo-program.pdf')
subjects_pdf = extract_data_from_docx_v2(data_pdf.get("tables", []), data_pdf.get("content", ""), data_pdf.get("pages"))

print(f"Num subjects: {len(subjects_pdf)}")
for i, s in enumerate(subjects_pdf):
    name = s.get("nazwa_przedmiotu", "").lower()
    if "dyplom" in name or "magister" in name or "las" in name:
        print(f"Index {i}: {s.get('nazwa_przedmiotu', '')} (ECTS: {s.get('ects', '')}) - Sem {s.get('semestr', '')} - Poziom {s.get('poziom', '')}")

print("\nLast 10 subjects:")
for s in subjects_pdf[-10:]:
    print(f"{s.get('nazwa_przedmiotu', '')} (Sem {s.get('semestr', '')}, ECTS {s.get('ects', '')}, Poziom {s.get('poziom', '')})")
