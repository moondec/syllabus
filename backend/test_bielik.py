import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_ai_generate():
    print("Testowanie endpointu /api/ai-generate...")
    
    payload = {
        "subject_name": "Inżynieria Oprogramowania",
        "field_type": "cel_przedmiotu",
        "context_info": {
            "kierunek": "Informatyka",
            "poziom": "Studia I stopnia",
            "tresci": "Cykl życia oprogramowania. Metodyki zwinne (Agile, Scrum). Zbieranie wymagań. Wzorce projektowe. Testowanie oprogramowania."
        },
        "provider_config": {
            "endpointUrl": "https://llm.hpc.pcss.pl/v1",
            "model": "bielik_11b",
            "apiKey": "" # Should fallback to keyring
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ai-generate", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("SUKCES! Otrzymano odpowiedź z modelu:")
            print("-" * 50)
            print(data.get("generated_text", ""))
            print("-" * 50)
        else:
            print(f"BŁĄD (HTTP {response.status_code}):")
            print(response.text)
            
    except Exception as e:
        print(f"BŁĄD POŁĄCZENIA: {e}")

if __name__ == "__main__":
    test_ai_generate()
