import os
import json
import keyring
import httpx
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Default PCSS configuration
DEFAULT_BASE_URL = "https://llm.hpc.pcss.pl/v1"
DEFAULT_MODEL = "bielik_11b"
_cached_api_key = None  # In-memory cache for the session

def get_api_key(provided_key: Optional[str] = None) -> Optional[str]:
    """
    Retrieves the API key. Priorities:
    1. Check in-memory cache
    2. Key provided directly from frontend
    3. Key stored in system keyring
    4. Key from environment variable PCSS_API_KEY
    """
    global _cached_api_key
    if _cached_api_key:
        return _cached_api_key

    if provided_key:
        _cached_api_key = provided_key
        return provided_key
        
    try:
        # Try keyring first (service: pcss_llm_app, username: api_key)
        key = keyring.get_password("pcss_llm_app", "api_key")
        if key:
            _cached_api_key = key
            return key
    except Exception as e:
        print(f"Keyring error: {e}")
        
    # Fallback to env var
    key = os.environ.get("PCSS_API_KEY")
    if key:
        _cached_api_key = key
    return key

def create_prompt(field_type: str, subject_name: str, context: Dict[str, Any], language: str = "pl") -> tuple[str, str]:
    """
    Returns (system_prompt, user_prompt) tailored for the requested syllabus field.
    Supports 'pl' (Polish) and 'en' (English) output languages.
    """
    # Extract relevant context info
    tresci = context.get("tresci", "")
    kierunek = context.get("kierunek", "")
    poziom = context.get("poziom", "")
    
    if language == "en":
        base_system = (
            "You are an experienced academic instructor and expert in writing course syllabi. "
            "Your task is to professionally formulate content for selected sections of a syllabus. "
            "Write concisely, in an academic style, in English. Return only the generated text, "
            "without any additional comments or greetings."
        )
    else:
        base_system = (
            "Jesteś doświadczonym nauczycielem akademickim i ekspertem od pisania sylabusów (kart przedmiotów). "
            "Twoim zadaniem jest pomóc w profesjonalnym sformułowaniu treści do wybranych sekcji sylabusa. "
            "Pisz zwięźle, akademickim stylem, w języku polskim. Zwracaj sam wygenerowany tekst, bez owijania "
            "go w dodatkowe komentarze czy przywitania."
        )
    
    if field_type == "cel_przedmiotu":
        sys_prompt = base_system
        if language == "en":
            user_prompt = (
                f"Write the 'Course Objectives' for the course '{subject_name}' (field of study: {kierunek}, level: {poziom}).\n"
                f"Course content (topics): {tresci}\n\n"
                "Formulate 2-4 concise objectives as bullet points (e.g. 'O1. To familiarize students with...')."
            )
        else:
            user_prompt = (
                f"Napisz 'Cel przedmiotu' dla kursu '{subject_name}' (kierunek: {kierunek}, poziom: {poziom}).\n"
                f"Treści programowe (zagadnienia): {tresci}\n\n"
                "Sformułuj 2-4 zwięzłe cele w punktach lub równoważnikach zdań (np. 'C1. Zapoznanie studentów z...')."
            )
    
    elif field_type == "metody_dydaktyczne":
        sys_prompt = base_system
        if language == "en":
            user_prompt = (
                f"Propose 'Teaching Methods' for the course '{subject_name}'.\n"
                f"Course content: {tresci}\n\n"
                "List traditional and activating methods as bullet points (e.g. 'informational lecture', 'laboratory exercises', 'project-based method')."
            )
        else:
            user_prompt = (
                f"Zaproponuj 'Metody dydaktyczne' (sposób prowadzenia zajęć) dla przedmiotu '{subject_name}'.\n"
                f"Treści programowe: {tresci}\n\n"
                "Wymień klasyczne i aktywizujące metody w formie krótkich punktów (np. 'wykład informacyjny', 'ćwiczenia laboratoryjne', 'metoda projektowa')."
            )
    
    elif field_type in ["wiedza", "umiejetnosci", "kompetencje"]:
        # Context specifically passed for outcomes
        symbols_info = context.get("symbols_info", [])
        
        if language == "en":
            category_map = {
                "wiedza": "KNOWLEDGE (the graduate knows and understands)",
                "umiejetnosci": "SKILLS (the graduate is able to)",
                "kompetencje": "SOCIAL COMPETENCES (the graduate is ready to)"
            }
        else:
            category_map = {
                "wiedza": "WIEDZA (absolwent zna i rozumie)",
                "umiejetnosci": "UMIEJĘTNOŚCI (absolwent potrafi)",
                "kompetencje": "KOMPETENCJE SPOŁECZNE (absolwent jest gotów do)"
            }
        category_name = category_map[field_type]
        
        symbols_text = "\n".join([f"- {s.get('symbol', 'N/A')}: {s.get('description', '')}" for s in symbols_info])
        
        sys_prompt = (
            f"{base_system} Remember that the text should fit the category: {category_name}."
            if language == "en" else
            f"{base_system} Pamiętaj, aby tekst pasował do kategorii: {category_name}."
        )
        if language == "en":
            user_prompt = (
                f"Write descriptive learning outcomes for the course '{subject_name}' in the category '{category_name}'.\n"
                f"Course content: {tresci}\n\n"
                "The following directional learning outcomes were selected as a basis:\n"
                f"{symbols_text}\n\n"
                "Rephrase the text based on these directional outcomes so that it sounds specific to this course and is ready for insertion into the syllabus. "
                "Use appropriate operational verbs (for knowledge: defines, explains; for skills: designs, calculates; for competences: cooperates, recognizes, etc.)."
            )
        else:
            user_prompt = (
                f"Napisz opisowe efekty uczenia się dla przedmiotu '{subject_name}' w kategorii '{category_name}'.\n"
                f"Treści programowe: {tresci}\n\n"
                "Dla tego przedmiotu wybrano następujące kierunkowe efekty uczenia się jako bazę:\n"
                f"{symbols_text}\n\n"
                "Zredaguj tekst na podstawie tych efektów kierunkowych tak, aby brzmiał specyficznie dla tego przedmiotu i był gotowy do wstawienia do sylabusa."
                "Używaj odpowiednich czasowników operacyjnych (dla wiedzy: definiuje, objaśnia; dla umiejętności: projektuje, oblicza; dla kompetencji: współpracuje, dostrzega itp.)."
            )
        
    else:
        sys_prompt = base_system
        if language == "en":
            user_prompt = f"Generate appropriate content for the section '{field_type}' in the syllabus for the course '{subject_name}'."
        else:
            user_prompt = f"Wygeneruj odpowiednią treść dla sekcji '{field_type}' w sylabusie przedmiotu '{subject_name}'."
        
    return sys_prompt, user_prompt

def generate_content(
    subject_name: str, 
    field_type: str, 
    context: Dict[str, Any], 
    provider_config: Optional[Dict[str, str]] = None,
    language: str = "pl"
) -> Dict[str, Any]:
    """
    Calls the LLM API to generate content for a specific syllabus field.
    """
    config = provider_config or {}
    base_url = config.get("endpointUrl", DEFAULT_BASE_URL).strip() or DEFAULT_BASE_URL
    model = config.get("model", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    api_key = get_api_key(config.get("apiKey", "").strip())
    
    if not api_key:
        return {
            "error": "Brak klucza API do modelu LLM. Skonfiguruj klucz w ustawieniach na froncie lub w systemowym pęku kluczy jako 'pcss_llm_app' (user 'api_key')."
        }
        
    try:
        http_client = httpx.Client()
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=http_client
        )
        
        sys_prompt, user_prompt = create_prompt(field_type, subject_name, context, language)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3, # Low temp for deterministic, professional output
            max_tokens=800
        )
        
        generated_text = response.choices[0].message.content.strip()
        
        # Clean up common wrapping quotes or markdown if the model hallucinated them despite instructions
        if generated_text.startswith("```"):
            lines = generated_text.split('\n')
            if lines[0].startswith("```"): lines = lines[1:]
            if lines[-1].startswith("```"): lines = lines[:-1]
            generated_text = "\n".join(lines).strip()
            
        return {"generated_text": generated_text}
        
    except Exception as e:
        error_msg = str(e)
        if "Unauthorized" in error_msg or "401" in error_msg:
            return {"error": "Błąd autoryzacji: Nieprawidłowy klucz API."}
        elif "Connection" in error_msg or "Timeout" in error_msg:
            return {"error": f"Błąd połączenia z API LLM ({base_url}). Sprawdź swoje połączenie z siecią lub VPN (jeśli wymagany dla PCSS). Szczegóły: {error_msg}"}
        else:
            return {"error": f"Wystąpił błąd podczas generowania tekstu: {error_msg}"}

