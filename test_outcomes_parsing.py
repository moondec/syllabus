import docx
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from data_extractor_v2 import extract_detailed_outcomes

def test_outcomes():
    file_path = 'programs/ProgramGeo2021dś.docx'
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    doc = docx.Document(file_path)
    tables_data = []
    for table in doc.tables:
        t_data = []
        for row in table.rows:
            t_data.append([cell.text.strip() for cell in row.cells])
        tables_data.append(t_data)

    outcomes = extract_detailed_outcomes(tables_data)
    
    print("--- PARSING RESULTS ---")
    for cat in ["W", "U", "K"]:
        print(f"Category {cat}: {len(outcomes[cat])} items")
        if outcomes[cat]:
            print(f"  First item: {outcomes[cat][0]['symbol']} -> {outcomes[cat][0]['description'][:50]}...")
            print(f"  Last item:  {outcomes[cat][-1]['symbol']} -> {outcomes[cat][-1]['description'][:50]}...")
        print("-" * 20)

if __name__ == "__main__":
    test_outcomes()
