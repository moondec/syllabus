import os
import json
import keyring
import httpx
import re
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

def create_prompt(field_type: str, subject_name: str, context: Dict[str, Any], language: str = "pl", field_value: str = "") -> tuple[str, str]:
    """
    Returns (system_prompt, user_prompt) tailored for the requested syllabus field.
    Supports 'pl' (Polish) and 'en' (English) output languages.
    Incorporates existing field_value for context-aware generation.
    """
    # Extract relevant context info
    tresci = context.get("tresci", "")
    kierunek = context.get("kierunek", "")
    poziom = context.get("poziom", "")
    cel = context.get("cel_przedmiotu", "")
    
    if language == "en":
        base_system = (
            "You are a professional academic editor. "
            "ABSOLUTE BAN on using Markdown formatting. "
            "DO NOT use characters like asterisks (*), hashes (#), or underscores (_). "
            "To create lists, use ONLY numbers (e.g., '1.', '2.'). "
            "DO NOT use dashes (-) or asterisks (*) for bullet points. "
            "DO NOT break lines inside a paragraph (no hard returns mid-sentence). "
            "Separate paragraphs with two blank lines. "
            "Your task is to write concise, academic text, ready to be pasted as plain, unformatted text."
        )
    else:
        base_system = (
            "Jesteś profesjonalnym edytorem akademickim. "
            "ABSOLUTNY ZAKAZ używania języka Markdown. "
            "NIE WOLNO używać znaków takich jak gwiazdki (*), krzyżyki (#), podkreślniki (_). "
            "Do tworzenia list używaj WYŁĄCZNIE cyfr (np. '1.', '2.'). "
            "NIE używaj myślników (-) ani gwiazdek (*) do podpunktów. "
            "NIE WOLNO łamać tekstu wewnątrz akapitu (np. twardym enterem w połowie zdania). "
            "Akapity oddzielaj od siebie dwiema pustymi liniami. "
            "Twoim zadaniem jest sformułowanie tekstu zwięzłego, naukowego, gotowego do wklejenia w systemie jako lity, niesformatowany tekst (plain text)."
        )
    
    context_prefix = ""
    if field_value:
        if language == "en":
            context_prefix = f"The user has already provided some initial ideas or instructions for this field: '{field_value}'. Please incorporate, develop, and expand upon them smoothly in your text.\n\n"
        else:
            context_prefix = f"Użytkownik podał już wstępne pomysły, fragmenty tekstu lub polecenia dla tego pola: '{field_value}'. Płynnie rozwiń i wpleć te sugestie w generowany tekst.\n\n"

    if field_type == "cel_przedmiotu":
        sys_prompt = base_system
        if language == "en":
            user_prompt = (
                f"{context_prefix}Write the 'Course Objectives' for the course '{subject_name}' (field of study: {kierunek}, level: {poziom}).\n"
                f"Course content (topics): {tresci}\n\n"
                "Formulate 2-4 concise objectives as a numbered list (1., 2.)."
            )
        else:
            user_prompt = (
                f"{context_prefix}Napisz 'Cel przedmiotu' dla kursu '{subject_name}' (kierunek: {kierunek}, poziom: {poziom}).\n"
                f"Treści programowe (zagadnienia): {tresci}\n\n"
                "Sformułuj 2-4 zwięzłe cele w formie numerowanej listy (1., 2.)."
            )
    
    elif field_type == "metody_dydaktyczne":
        sys_prompt = base_system
        if language == "en":
            user_prompt = (
                f"{context_prefix}Propose 'Teaching Methods' for the course '{subject_name}'.\n"
                f"Course content: {tresci}\n\n"
                "List traditional and activating methods as a numbered list (1., 2.)."
            )
        else:
            user_prompt = (
                f"{context_prefix}Zaproponuj 'Metody dydaktyczne' (sposób prowadzenia zajęć) dla przedmiotu '{subject_name}'.\n"
                f"Treści programowe: {tresci}\n\n"
                "Wymień klasyczne i aktywizujące metody w formie numerowanej listy (1., 2.)."
            )

    elif field_type == "metody_weryfikacji":
        sys_prompt = base_system
        if language == "en":
            user_prompt = (
                f"{context_prefix}Propose 'Verification Methods' (how student performance is assessed) for the course '{subject_name}'.\n"
                f"Objectives: {cel}\n"
                f"Content: {tresci}\n\n"
                "List appropriate methods (e.g., written exam, project) as a numbered list (1., 2.)."
            )
        else:
            user_prompt = (
                f"{context_prefix}Zaproponuj 'Metody weryfikacji' (sposób sprawdzania efektów uczenia się) dla przedmiotu '{subject_name}'.\n"
                f"Cele przedmiotu: {cel}\n"
                f"Treści programowe: {tresci}\n\n"
                "Wymień odpowiednie metody w formie numerowanej listy (1., 2.)."
            )

    elif field_type == "tresci":
        sys_prompt = base_system
        if language == "en":
            user_prompt = (
                f"{context_prefix}Write 'Course Content' (list of topics) for the course '{subject_name}' (field of study: {kierunek}).\n\n"
                "List the main topics or modules of the course as a numbered list (1., 2.)."
            )
        else:
            user_prompt = (
                f"{context_prefix}Napisz 'Treści programowe' (listę zagadnień) dla przedmiotu '{subject_name}' (kierunek: {kierunek}).\n\n"
                "Wymień główne bloki tematyczne lub punkty programu zajęć w formie numerowanej listy (1., 2.)."
            )

    elif field_type == "nazwa_angielska":
        sys_prompt = "You are a professional academic translator."
        if language == "pl":
            # Translate PL Subject Name to English
            user_prompt = f"{context_prefix}Translate the Polish academic course name '{subject_name}' into professional English. Return ONLY the translated name as plain text. Do not use quotes."
        else:
            # English Mode: nazwa_angielska is where we put the Polish translation
            user_prompt = f"{context_prefix}Translate the English academic course name '{subject_name}' into professional Polish. Return ONLY the translated name as plain text. Do not use quotes."
    
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
                f"{context_prefix}Write descriptive learning outcomes for the course '{subject_name}' in the category '{category_name}'.\n"
                f"Course content: {tresci}\n"
                "The following directional learning outcomes were selected as a basis:\n"
                f"{symbols_text}\n\n"
                "Rephrase into specific course outcomes. Use ONLY plain text. You may use paragraphs or numbered lists."
            )
        else:
            user_prompt = (
                f"{context_prefix}Napisz opisowe efekty uczenia się dla przedmiotu '{subject_name}' w kategorii '{category_name}'.\n"
                f"Treści programowe: {tresci}\n"
                "Dla tego przedmiotu wybrano następujące kierunkowe efekty uczenia się jako bazę:\n"
                f"{symbols_text}\n\n"
                "Zredaguj tekst specyficzny dla przedmiotu. Możesz używać akapitów i numerowanych list."
            )
        
    else:
        sys_prompt = base_system
        if language == "en":
            user_prompt = f"{context_prefix}Generate appropriate content for the section '{field_type}' in the syllabus for the course '{subject_name}'. Return only plain text."
        else:
            user_prompt = f"{context_prefix}Wygeneruj odpowiednią treść dla sekcji '{field_type}' w sylabusie przedmiotu '{subject_name}'. Zwróć wyłącznie czysty tekst."
        
    return sys_prompt, user_prompt


def generate_content(
    subject_name: str, 
    field_type: str, 
    context: Dict[str, Any], 
    provider_config: Optional[Dict[str, str]] = None,
    language: str = "pl",
    field_value: str = ""
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
        
        sys_prompt, user_prompt = create_prompt(field_type, subject_name, context, language, field_value)
        
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
        
        # Clean up common wrapping quotes or markdown block tags if hallucinated
        if generated_text.startswith("```"):
            lines = generated_text.split('\n')
            if lines[0].startswith("```"): lines = lines[1:]
            if lines[-1].startswith("```"): lines = lines[:-1]
            generated_text = "\n".join(lines).strip()
            
        # Remove literal "nowa linia", "new line" etc.
        generated_text = generated_text.replace('nowa linia', '').replace('new line', '')

        # Remove markdown bold/italic tags
        generated_text = re.sub(r'\*\*(.*?)\*\*', r'\1', generated_text)
        generated_text = re.sub(r'\*(.*?)\*', r'\1', generated_text)
        generated_text = re.sub(r'__(.*?)__', r'\1', generated_text)
        generated_text = re.sub(r'_(.*?)_', r'\1', generated_text)
        
        # Remove headers hashes
        generated_text = re.sub(r'^#+\s*', '', generated_text, flags=re.MULTILINE)

        # Convert remaining dash or asterisk bullet points to simple numbers or strip them 
        # Since we asked for numbered lists, if they still use `-` or `*`, let's just make sure they look clean
        # But to completely avoid markdown parsing logic in docxtpl, let's replace leading `- ` with nothing or a dot
        # A safer approach is to remove leading `- ` or `* ` and rely on the content
        generated_text = re.sub(r'^[-*]\s+', '', generated_text, flags=re.MULTILINE)
        
        # Finally, prevent single newline breaks within sentences (hard wrapping). 
        # We replace single newlines with spaces, but keep double newlines (paragraphs)
        # However, we must not join numbered list items. A numbered list usually starts with "1." on a new line.
        # Let's split by double newline first, then process each block.
        blocks = generated_text.split('\n\n')
        processed_blocks = []
        for block in blocks:
            # If the block looks like a numbered list (has lines starting with numbers), 
            # we keep the newlines that start with numbers, but join the rest.
            lines = block.split('\n')
            new_lines = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Starts with number e.g. "1." or "A."
                if re.match(r'^\d+[\.\)]', line):
                    new_lines.append(line)
                else:
                    if new_lines:
                        # Append to the previous line with a space
                        new_lines[-1] += " " + line
                    else:
                        new_lines.append(line)
            processed_blocks.append('\n'.join(new_lines))

        generated_text = "\n\n".join(processed_blocks)

        return {"generated_text": generated_text.strip()}

        
    except Exception as e:
        error_msg = str(e)
        if "Unauthorized" in error_msg or "401" in error_msg:
            return {"error": "Błąd autoryzacji: Nieprawidłowy klucz API."}
        elif "Connection" in error_msg or "Timeout" in error_msg:
            return {"error": f"Błąd połączenia z API LLM ({base_url}). Sprawdź swoje połączenie z siecią lub VPN (jeśli wymagany dla PCSS). Szczegóły: {error_msg}"}
        else:
            return {"error": f"Wystąpił błąd podczas generowania tekstu: {error_msg}"}

