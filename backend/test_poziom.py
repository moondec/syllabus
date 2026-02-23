import re
from file_parser import parse_pdf
data = parse_pdf('../programs/1-st-2-st-lesnictwo-program.pdf')
text = data.get("content", "")
matches = list(re.finditer(r"(?i)poziom.*", text))
print("Found 'poziom':")
for m in matches:
    print(m.group(0))
