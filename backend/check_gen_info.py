from file_parser import parse_pdf
from data_extractor_v2 import extract_general_info

data_pdf = parse_pdf('../programs/1-st-2-st-lesnictwo-program.pdf')
tables = data_pdf.get("tables", [])
print(f"Number of tables: {len(tables)}")
if len(tables) > 0:
    for r in tables[0]:
        print(r)
info = extract_general_info(tables, data_pdf.get("content", ""))
print("General Info:", info)
