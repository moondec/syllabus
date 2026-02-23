import file_parser
import data_extractor_v2
import sys
import json

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if file_path.endswith(".docx"):
            parsed_data = file_parser.parse_docx(file_path)
            if parsed_data and not parsed_data.get("error"):
                extracted_data = data_extractor_v2.extract_data_from_docx_v2(parsed_data.get("tables"), parsed_data.get("content"))
                print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
            elif parsed_data and parsed_data.get("error"):
                print(f"Error parsing file: {parsed_data.get('error')}")
        else:
            print("Unsupported file format")
    else:
        print("Please provide a file path")
