import file_parser
import plan_extractor
import sys
import json

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if file_path.endswith(".pdf"):
            parsed_data = file_parser.parse_pdf(file_path)
            if parsed_data and not parsed_data.get("error"):
                print("--- TABLES ---")
                print(json.dumps(parsed_data.get("tables"), indent=2, ensure_ascii=False))
                print("\n--- EXTRACTED DATA ---")
                extracted_data = plan_extractor.extract_data_from_plan_pdf(parsed_data.get("tables"))
                print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
            elif parsed_data and parsed_data.get("error"):
                print(f"Error parsing file: {parsed_data.get('error')}")
        else:
            print("Unsupported file format")
    else:
        print("Please provide a file path")
