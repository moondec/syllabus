import file_parser
import sys
import json

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if file_path.endswith(".docx"):
            data = file_parser.parse_docx(file_path)
            if data and not data.get("error"):
                print("--- CONTENT ---")
                print(data.get("content"))
                print("\n--- TABLES ---")
                print(json.dumps(data.get("tables"), indent=2, ensure_ascii=False))
            elif data and data.get("error"):
                print(f"Error: {data.get('error')}")
        elif file_path.endswith(".pdf"):
            data = file_parser.parse_pdf(file_path)
            if data and not data.get("error"):
                print("--- CONTENT ---")
                print(data.get("content"))
                print("\n--- TABLES ---")
                print(json.dumps(data.get("tables"), indent=2, ensure_ascii=False))
            elif data and data.get("error"):
                print(f"Error: {data.get('error')}")
        else:
            print("Unsupported file format")
    else:
        print("Please provide a file path")
