from file_parser import parse_docx, parse_pdf
from data_extractor_v2 import extract_data_from_docx_v2

data_docx = parse_docx('../programs/ProgramGeo2021dś.docx')
subjects_docx = extract_data_from_docx_v2(data_docx.get("tables", []), data_docx.get("content", ""))

data_pdf = parse_pdf('../programs/1-st-2-st-lesnictwo-program.pdf')
subjects_pdf = extract_data_from_docx_v2(data_pdf.get("tables", []), data_pdf.get("content", ""))

import json
print("Docx Subjects:", json.dumps(subjects_docx, indent=2, ensure_ascii=False))
print("PDF Subjects:", json.dumps(subjects_pdf, indent=2, ensure_ascii=False))

