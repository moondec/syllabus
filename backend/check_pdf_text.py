from file_parser import parse_pdf
data = parse_pdf('../programs/1-st-2-st-lesnictwo-program.pdf')
print("--- TEKST PDF ---")
print(data.get("text", "")[:4000])
