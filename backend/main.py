import os
import uuid
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import shutil
import file_parser
import data_extractor_v2
import plan_extractor
import document_generator
import data_merger

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Zezwol wszystkie; w produkcji powinnismy sprecyzowac do http://localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/process-document")
async def process_document(file: UploadFile = File(None), url: Optional[str] = Form(None)):
    if file:
        file_location = f"temp_{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        parsed_data = None
        if file.filename.endswith(".docx"):
            parsed_data = file_parser.parse_docx(file_location)
        elif file.filename.endswith(".pdf"):
            parsed_data = file_parser.parse_pdf(file_location)
        else:
            os.remove(file_location)
            return JSONResponse(content={"error": "Unsupported file format"}, status_code=400)

        os.remove(file_location)

        if not parsed_data or parsed_data.get("error"):
            return JSONResponse(content={"error": parsed_data.get("error") if parsed_data else "Failed to parse document"}, status_code=500)

        tables = parsed_data.get("tables", [])
        text_content = parsed_data.get("content", "")
        pages_content = parsed_data.get("pages", None)
        
        # Używamy uniwersalnego ekstraktora z Phase 3 (obsługującego V2 Tables + Text Fallback)
        subject_data = data_extractor_v2.extract_data_from_docx_v2(tables, text_content, pages_content)

        if subject_data and isinstance(subject_data, dict) and "error" in subject_data:
            return JSONResponse(content=subject_data, status_code=500)
        
        # Nawet gdyby nie znaleziono żadnej tabeli (tables = []),
        # parser tekstowy uruchomiłby się na text_content we wnetrzu extract_data_from_docx_v2.
        return JSONResponse(content=subject_data, status_code=200)

    elif url:
        return JSONResponse(content={"message": "URL processed successfully", "url": url}, status_code=200)
    else:
        return JSONResponse(content={"error": "No file or URL provided"}, status_code=400)

# In-memory store for generated files (file_id -> {path, filename})
_generated_files = {}

@app.post("/api/generate-syllabus")
async def generate_syllabus(data: dict):
    # Pass all incoming form fields dynamically
    result = document_generator.generate_docx(data)
    if "error" in result:
        return JSONResponse(content=result, status_code=500)
    
    file_path = result.get("path")
    if file_path and os.path.exists(file_path):
        # Sanitize filename - only safe chars for URL path
        raw_name = data.get("nazwa_przedmiotu", "sylabus")
        clean_name = "".join(c for c in raw_name if c.isalnum() or c in (' ', '_', '-')).strip()
        clean_name = "_".join(clean_name.split())  # spaces -> underscores for URL safety
        if not clean_name:
            clean_name = "sylabus"
        download_filename = f"{clean_name[:120]}.docx"
        
        # Store file info and return a download URL with filename in path
        file_id = str(uuid.uuid4())
        _generated_files[file_id] = {"path": os.path.abspath(file_path), "filename": download_filename}
        
        return JSONResponse(content={
            "download_url": f"/api/download/{file_id}/{download_filename}",
            "filename": download_filename
        })
    else:
        return JSONResponse(content={"error": "File not found"}, status_code=404)

@app.get("/api/download/{file_id}/{filename}")
async def download_file(file_id: str, filename: str):
    file_info = _generated_files.pop(file_id, None)
    if not file_info or not os.path.exists(file_info["path"]):
        return JSONResponse(content={"error": "File not found or expired"}, status_code=404)
    
    return FileResponse(
        path=file_info["path"],
        filename=file_info["filename"],
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    )

@app.get("/api/get-all-subjects")
async def get_all_subjects():
    programs_subjects = []
    script_dir = os.path.dirname(__file__)
    
    # Process programs
    programs_path = os.path.join(script_dir, "..", "programs")
    if os.path.exists(programs_path):
        for filename in os.listdir(programs_path):
            file_path = os.path.join(programs_path, filename)
            if filename.endswith(".docx"):
                parsed_data = file_parser.parse_docx(file_path)
                if parsed_data and not parsed_data.get("error"):
                    subjects = data_extractor_v2.extract_data_from_docx_v2(parsed_data.get("tables"), parsed_data.get("content"))
                    programs_subjects.extend(subjects)
            elif filename.endswith(".pdf"):
                # I need to implement the pdf extractor for programs
                pass

    plans_subjects = []
    # Process plans
    plans_path = os.path.join(script_dir, "..", "plans")
    if os.path.exists(plans_path):
        for filename in os.listdir(plans_path):
            file_path = os.path.join(plans_path, filename)
            if filename.endswith(".pdf"):
                parsed_data = file_parser.parse_pdf(file_path)
                if parsed_data and not parsed_data.get("error"):
                    subjects = plan_extractor.extract_data_from_plan_pdf(parsed_data.get("tables"))
                    plans_subjects.extend(subjects)

    merged_subjects = data_merger.merge_subjects(programs_subjects, plans_subjects)
    return merged_subjects