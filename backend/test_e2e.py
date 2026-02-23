import requests
import os
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_full_flow():
    test_file_path = "../programs/ProgramGeo2021dś.docx"
    
    if not os.path.exists(test_file_path):
        print(f"Skipping test, file not found: {test_file_path}")
        return
        
    print("1. Testing /api/process-document...")
    with open(test_file_path, "rb") as f:
        response = requests.post(f"{BASE_URL}/process-document", files={"file": f})
        
    assert response.status_code == 200, f"Error processing file: {response.text}"
    data = response.json()
    print("Data processed successfully.")
    
    # Normally we extract subjects and select one, wait - the new endpoint returns a list of subjects!
    subjects = data if isinstance(data, list) else [data]
    subject = subjects[0] if subjects else {}
    print(f"Selecting subject: {subject.get('nazwa_przedmiotu', 'Unknown')}")
    print(f"Symbols W: {subject.get('learning_outcomesW')}")
    print(f"Symbols U: {subject.get('learning_outcomesU')}")
    print(f"Symbols K: {subject.get('learning_outcomesK')}")
    print(f"Ref Kierunkowe available: {len(subject.get('ref_kierunkowe', '')) > 0}")
    
    # Adding some test field
    subject["cel_przedmiotu"] = "To jest cel dodany podczas testu integracyjnego."
    
    print("2. Testing /api/generate-syllabus...")
    gen_response = requests.post(f"{BASE_URL}/generate-syllabus", json=subject)
    
    assert gen_response.status_code == 200, f"Error generating syllabus: {gen_response.text}"
    
    output_filename = "test_output.docx"
    with open(output_filename, "wb") as f:
        f.write(gen_response.content)
        
    print(f"Generated DOCX saved to {output_filename}, size: {os.path.getsize(output_filename)} bytes")
    assert os.path.getsize(output_filename) > 0, "Generated file is empty"
    
    print("ALL TESTS PASSED!")

if __name__ == "__main__":
    test_full_flow()
