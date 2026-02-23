from file_parser import parse_pdf
from data_extractor_v2 import extract_data_from_docx_v2
import sys

# Load PDF
data_pdf = parse_pdf('../programs/1-st-2-st-lesnictwo-program.pdf')
subjects_pdf = extract_data_from_docx_v2(data_pdf.get("tables", []), data_pdf.get("content", ""))
print(f"Num subjects found in PDF: {len(subjects_pdf)}")
