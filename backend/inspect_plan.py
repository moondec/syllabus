import pdfplumber
import sys
import os

# Inspect the structure of a plan PDF
pdf_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'plans', 'is_i_st_s_2024_2025.pdf')

with pdfplumber.open(pdf_path) as pdf:
    # Extract text before first table
    for i, page in enumerate(pdf.pages[:3]):
        print(f"\n=== PAGE {i+1} TEXT (first 600 chars) ===")
        text = page.extract_text() or ""
        print(text[:600])
        
        tables = page.extract_tables()
        for ti, table in enumerate(tables):
            print(f"\n=== PAGE {i+1}, TABLE {ti+1} ({len(table)} rows) ===")
            for ri, row in enumerate(table[:5]):  # First 5 rows only
                print(f"  Row {ri} ({len(row)} cols): {row}")
            if len(table) > 5:
                print(f"  ... ({len(table) - 5} more rows)")
