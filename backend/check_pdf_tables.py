from file_parser import parse_pdf
data = parse_pdf('../programs/1-st-2-st-lesnictwo-program.pdf')
tables = data.get("tables", [])
for i, table in enumerate(tables):
    if len(table) > 0 and len(table[0]) > 0:
        header_text = str(table[0])[:150].replace('\n', ' ')
        print(f"Table {i}, rows: {len(table)}, header logic: {header_text}")
