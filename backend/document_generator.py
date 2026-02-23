import os
from docxtpl import DocxTemplate

def generate_docx(subject_data, template_path=None):
    """
    Generates a .docx file from a template and a single subject's data.
    """
    if template_path is None:
        template_path = os.path.join(os.path.dirname(__file__), "..", "template.docx")
        if not os.path.exists(template_path):
             template_path = os.path.join(os.path.dirname(__file__), "..", "template_fixed.docx")
        
    try:
        doc = DocxTemplate(template_path)
        
        # Map internal keys to template tags
        context = subject_data.copy()
        context["name"] = subject_data.get("nazwa_przedmiotu", "")
        context["name_en"] = subject_data.get("nazwa_angielska", "")
        context["field_of_study"] = subject_data.get("kierunek", "")
        context["level"] = subject_data.get("poziom", "")
        context["profile"] = subject_data.get("profil", "")
        context["semester"] = subject_data.get("semestr", "")
        context["content"] = subject_data.get("tresci", "")
        context["zakres"] = subject_data.get("efekty", "") # Usually holds the full range of outcomes
        
        # Ensure learning outcomes are mapped if not already
        context["learning_outcomesW"] = subject_data.get("learning_outcomesW", "")
        context["learning_outcomesU"] = subject_data.get("learning_outcomesU", "")
        context["learning_outcomesK"] = subject_data.get("learning_outcomesK", "")
        
        # Additional mappings for all tags identified in template.docx by check_tags.py
        context["ects"] = subject_data.get("ects", "")
        context["kierownik"] = subject_data.get("kierownik", "")
        context["cel_przedmiotu"] = subject_data.get("cel_przedmiotu", "")
        context["metody_dydaktyczne"] = subject_data.get("metody_dydaktyczne", "")
        context["metody_weryfikacji"] = subject_data.get("metody_weryfikacji", "")
        context["unit"] = subject_data.get("jednostka", "")
        context["wiedza"] = subject_data.get("wiedza", "")
        context["kompetencje"] = subject_data.get("kompetencje", "")
        context["formy_zaliczenia"] = subject_data.get("formy_zaliczenia", "")
        context["literatura"] = subject_data.get("literatura", "")
        context["umiejetnosci"] = subject_data.get("umiejetnosci", "")
        
        doc.render(context)
        
        # Sanitize the name for the output path
        sanitized_name = "".join(c for c in subject_data.get('nazwa_przedmiotu', 'syllabus') if c.isalnum() or c in (' ', '_')).rstrip()
        output_path = f"{sanitized_name.replace(' ', '_')}.docx"
        doc.save(output_path)
        return {"path": output_path}
    except Exception as e:
        return {"error": str(e)}
