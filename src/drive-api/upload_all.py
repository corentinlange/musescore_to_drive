#!/usr/bin/env python3
"""
Upload files to Google Drive (GitHubBot)

Executed automatically by GitHubBot via GitHub Actions.
Uploads all generated files while preserving directory structure.

Usage: python src/drive-api/upload_all.py [output_directory]
"""

import os
import sys
from pathlib import Path

# Load .env file (optional, for local use)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available in CI, variables passed directly
    pass

# Add drive-api to path
sys.path.insert(0, os.path.dirname(__file__))
from connector import DriveConnector


def upload_directory_structure(output_dir, root_folder_id):
    """
    Upload all files from output/ preserving directory structure
    
    Args:
        output_dir: Output directory to upload
        root_folder_id: Root Drive folder ID
    """
    drive = DriveConnector()
    stats = {"uploaded": 0, "skipped": 0}
    
    # Recursively walk through output/
    for root, dirs, files in os.walk(output_dir):
        # Calculate relative path from output/
        rel_path = os.path.relpath(root, output_dir)
        
        if rel_path == ".":
            # Output root
            current_folder_id = root_folder_id
        else:
            # Create folder structure on Drive
            path_parts = Path(rel_path).parts
            current_folder_id = root_folder_id
            
            for part in path_parts:
                # Create or get subfolder
                current_folder_id = drive.create_folder(part, current_folder_id)
        
        # Upload all files in current folder
        for file in files:
            file_path = os.path.join(root, file)
            print(f"📤 Upload: {os.path.relpath(file_path, output_dir)}")
            
            try:
                drive.upload_file(file_path, current_folder_id, replace=True)
                stats["uploaded"] += 1
            except Exception as e:
                print(f"   ❌ Error: {e}")
                stats["skipped"] += 1
    
    return stats


def main():
    # Verify DRIVE_FOLDER_ID
    root_folder_id = os.getenv("DRIVE_FOLDER_ID")
    if not root_folder_id:
        print("❌ Error: DRIVE_FOLDER_ID not defined in .env")
        print("\nAdd to .env:")
        print("  DRIVE_FOLDER_ID='your_folder_id'")
        sys.exit(1)
    
    # Determine output directory
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    
    if not os.path.isdir(output_dir):
        print(f"❌ Error: Directory {output_dir} not found")
        sys.exit(1)
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("☁️  Upload to Google Drive")
    print(f"📁 Directory: {output_dir}")
    print(f"🎯 Drive Root: {root_folder_id}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    # Upload
    stats = upload_directory_structure(output_dir, root_folder_id)
    
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ Upload completed!")
    print(f"   📤 Files uploaded: {stats['uploaded']}")
    if stats['skipped'] > 0:
        print(f"   ⚠️  Files skipped: {stats['skipped']}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


if __name__ == "__main__":
    main()
