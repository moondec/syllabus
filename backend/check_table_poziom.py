import re
from file_parser import parse_pdf
data = parse_pdf('../programs/1-st-2-st-lesnictwo-program.pdf')

for i, t in enumerate(data.get("tables", [])):
    for r in t:
        for c in r:
            if c and "Poziom kształcenia:" in str(c):
                print(f"Table {i} contains Poziom: {c}")
