from file_parser import parse_pdf
import json

data_pdf = parse_pdf('../programs/1-st-2-st-lesnictwo-program.pdf')
tables = data_pdf.get("tables", [])

print("Pierwsze tabele:")
for i, table in enumerate(tables[:3]):
    print(f"\n--- Tabela {i} ---")
    for row in table:
        print(row)
