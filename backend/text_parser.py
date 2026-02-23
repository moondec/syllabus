import re

def extract_general_info_from_text(text):
    """Fallback extractor for general information from the document text."""
    info = {}
    
    # Przykładowe patterny, które można dostroić
    field_match = re.search(r"Nazwa kierunku studiów:\s*(.*?)(?=\n)", text, re.IGNORECASE)
    info["kierunek"] = field_match.group(1).strip() if field_match else ""

    level_match = re.search(r"Poziom kształcenia:\s*(.*?)(?=\n)", text, re.IGNORECASE)
    info["poziom"] = level_match.group(1).strip() if level_match else ""
    
    profile_match = re.search(r"Profil kształcenia:\s*(.*?)(?=\n)", text, re.IGNORECASE)
    info["profil"] = profile_match.group(1).strip() if profile_match else ""

    return info

def extract_subjects_from_text(text):
    """
    Fallback extractor for list of subjects.
    This relies heavily on the specific formatting of the provided documents.
    It attempts to find subject blocks by looking for numbered lists or specific keywords.
    """
    subjects = []
    
    general_info = extract_general_info_from_text(text)

    # Bardzo naiwne podejście: podział tekstu na bloki za pomocą słowa kluczowego, 
    # np. nazwa przedmiotu lub semestr, i szukanie powiązanych z nim danych
    # W rzeczywistości, napisanie uniwersalnego parsera regex dla programu studiów
    # wymagałoby dużej liczby reguł. Przygotowałem uproszczoną bazę do rozwoju.
    
    # Przykład: szukamy struktury powtarzającej się (np. "1. Matematyka")
    # Z racji braku standardu, musimy improwizować lub założyć, 
    # że użytkownik przynajmniej otrzyma puste szablony do wypełnienia jeśli wszystko zawiedzie.
    
    # Poniżej znajduje się zalążek logiki, którą można dostosowywać:
    lines = text.split('\n')
    current_subject = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Potencjalny nowy przedmiot (np. 1. Wstęp do...)
        match_name = re.match(r'^(\d+)\.\s+([A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż\s\-]+)$', line)
        
        # Jeśli znajdziemy ECTS w linijce obok
        match_ects = re.search(r'ECTS:\s*(\d+)', line, re.IGNORECASE)
        match_sem = re.search(r'Semestr:\s*(\d+)', line, re.IGNORECASE)

        if match_name:
            if current_subject and current_subject.get('nazwa_przedmiotu'):
                subjects.append(current_subject)
            
            current_subject = {
                "nazwa_przedmiotu": match_name.group(2).strip(),
                "nazwa_angielska": "",
                "semestr": "",
                "ects": "",
                "tresci": "",
                "efekty": "",
                "jednostka": ""
            }
            current_subject.update(general_info)
            
        elif current_subject:
            if match_ects and not current_subject.get("ects"):
                current_subject["ects"] = match_ects.group(1)
            elif match_sem and not current_subject.get("semestr"):
                current_subject["semestr"] = match_sem.group(1)
            # Tutaj można by dodawać resztę mapowań (np szukanie "Treści: ...")

    # Dodaj ostatni subject do listy
    if current_subject and current_subject.get('nazwa_przedmiotu'):
        subjects.append(current_subject)

    # Jeśli parser tekstowy całkowicie zawiedzie i nie znajdzie nic, zwrocimy chociaz "puste formy"
    # z wypelnionym ogólnym INFO o kierunku
    if not subjects:
        empty_subject = {
            "nazwa_przedmiotu": "",
            "nazwa_angielska": "",
            "semestr": "",
            "ects": "",
            "tresci": "",
            "efekty": "",
            "jednostka": ""
        }
        empty_subject.update(general_info)
        subjects.append(empty_subject)

    return subjects
