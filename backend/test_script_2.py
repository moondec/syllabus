from file_parser import parse_docx, parse_pdf
import json

data_docx = parse_docx('../programs/ProgramGeo2021dś.docx')
tables = data_docx.get("tables", [])
print(f"Num tables DOCX: {len(tables)}")
if tables:
    for i, row in enumerate(tables[0][:5]):
        print(f"R{i}: {row}")

data_pdf = parse_pdf('../programs/1-st-2-st-lesnictwo-program.pdf')
pdf_tables = data_pdf.get("tables", [])
print(f"\nNum tables PDF: {len(pdf_tables)}")
if pdf_tables:
    for i, row in enumerate(pdf_tables[0][:5]):
        print(f"R{i}: {row}")
