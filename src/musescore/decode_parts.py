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
    # Read the JSON file
    sheet_name = os.path.splitext(json_file_path)[0].split("-parts")[0]

    with open(json_file_path, "r") as json_file:
        data = json.load(json_file)

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
