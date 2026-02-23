from file_parser import parse_docx, parse_pdf
import json

data_docx = parse_docx('../programs/ProgramGeo2021dś.docx')
tables = data_docx.get("tables", [])
headers = [" | ".join(t[0]) for t in tables if t]
print("--- Docx headers ---")
for h in headers:
    print(h)

data_pdf = parse_pdf('../programs/1-st-2-st-lesnictwo-program.pdf')
pdf_tables = data_pdf.get("tables", [])
pdf_headers = [" | ".join(t[0]) for t in pdf_tables if t]
print("\n--- PDF headers ---")
for h in pdf_headers:
    print(h)

