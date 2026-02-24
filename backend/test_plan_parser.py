"""Quick test of plan_parser against the sample PDF."""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

import file_parser
import plan_parser

# Test with stacjonarne plan
pdf_path = os.path.join(os.path.dirname(__file__), '..', 'plans', 'is_i_st_s_2024_2025.pdf')
print(f"Testing: {os.path.basename(pdf_path)}")

parsed = file_parser.parse_pdf(pdf_path)
result = plan_parser.extract_full_plan(parsed)

print(f"Metadata: {result['metadata']}")
print(f"Subjects found: {len(result['subjects'])}")

for s in result['subjects'][:5]:
    print(f"  {s['nazwa_przedmiotu'][:40]:<40} ECTS={s.get('ects','?'):>2}  numWS={s.get('numWS',''):>3}  numCS={s.get('numCS',''):>3}  numTS={s.get('numTS',''):>4}  sem={s.get('semestr','?')}")

print("\n---\n")

# Test with niestacjonarne plan
pdf_path2 = os.path.join(os.path.dirname(__file__), '..', 'plans', 'Plan studiów niestac. Leśnictwo I stopnia_01102025_0.pdf')
if os.path.exists(pdf_path2):
    print(f"Testing: {os.path.basename(pdf_path2)}")
    parsed2 = file_parser.parse_pdf(pdf_path2)
    result2 = plan_parser.extract_full_plan(parsed2)

    print(f"Metadata: {result2['metadata']}")
    print(f"Subjects found: {len(result2['subjects'])}")

    for s in result2['subjects'][:5]:
        print(f"  {s['nazwa_przedmiotu'][:40]:<40} ECTS={s.get('ects','?'):>2}  numWNS={s.get('numWNS',''):>3}  numCNS={s.get('numCNS',''):>3}  numTNS={s.get('numTNS',''):>4}  sem={s.get('semestr','?')}")
