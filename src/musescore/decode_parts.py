import base64
import json
import sys
import os


def decode_and_save_part(sheet_name, part_name, base64_data, output_dir):
    # Decode the Base64 data
    binary_data = base64.b64decode(base64_data)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create the output .mscz file for the part
    part_name = part_name.replace(" ", "_").lower()
    output_path = os.path.join(
        output_dir, f"{os.path.basename(sheet_name)}-{part_name}.mscz"
    )
    with open(output_path, "wb") as f:
        f.write(binary_data)

    print(f"MSCZ file has been saved as '{output_path}'")


def process_json_file(json_file_path, output_dir):
    """
    Parse JSON from MuseScore --score-parts and create MSCZ files for each part
    """
    # Check if file exists and is not empty
    if not os.path.exists(json_file_path):
        print(f"⚠️  JSON file not found: {json_file_path}")
        return
    
    if os.path.getsize(json_file_path) == 0:
        print(f"⚠️  JSON file is empty (MuseScore may not have extracted parts): {json_file_path}")
        return
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
    except json.JSONDecodeError as e:
        print(f"⚠️  Invalid JSON from MuseScore (skipping parts extraction): {e}")
        return
    except Exception as e:
        print(f"⚠️  Error reading JSON file: {e}")
        return
    
    if not data:
        print(f"⚠️  No parts found in JSON")
        return

    # Read the JSON file
    sheet_name = os.path.splitext(json_file_path)[0].split("-parts")[0]

    parts = data.get("parts", [])
    parts_bin = data.get("partsBin", [])

    if not parts or not parts_bin:
        print("Error: No parts or partsBin found in the JSON file.")
        return

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Process each part and save as .mscz
    for part_name, bin_data in zip(parts, parts_bin):
        decode_and_save_part(sheet_name, part_name, bin_data, output_dir)


if __name__ == "__main__":
    # Check if the JSON file path is provided as an argument
    if len(sys.argv) < 2:
        print("Usage: python script.py <json_file_path> [output_directory]")
        sys.exit(1)

    json_file_path = sys.argv[1]

    # Optional output directory argument, default to "output_mscz_parts"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output_mscz_parts"

    # Process the JSON file and decode parts
    print(f"Outputdir: {output_dir}")
    process_json_file(json_file_path, output_dir)
