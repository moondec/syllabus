from docx import Document

document = Document()
table = document.add_table(rows=0, cols=2)

fields = [
    ('Nazwa przedmiotu', '{{ nazwa_przedmiotu }}'),
    ('Nazwa angielska', '{{ nazwa_angielska }}'),
    ('Kierunek studiów', '{{ kierunek }}'),
    ('Poziom kształcenia', '{{ poziom }}'),
    ('Profil', '{{ profil }}'),
    ('Forma studiów', '{{ forma }}'),
    ('Semestr', '{{ semestr }}'),
    ('Przechodzi przez jednostkę', '{{ jednostka }}'),
    ('Punkty ECTS', '{{ ects }}'),
    ('Treści programowe', '{{ tresci }}'),
    ('Efekty uczenia się', '{{ efekty }}')
]

for label, tag in fields:
    row_cells = table.add_row().cells
    row_cells[0].text = label
    row_cells[1].text = tag

document.save('simple_template.docx')
