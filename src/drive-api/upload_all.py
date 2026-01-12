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


def upload_with_versioning(output_dir, root_folder_id):
    """
    Upload files with versioning support - archives old .mscz files before uploading new versions
    
    For each folder (e.g., 'song_name/'):
    1. Check if folder exists on Drive
    2. If exists: archive old .mscz file to 'old/' subfolder with timestamp
    3. Clean folder (preserve 'old/' subfolder)
    4. Upload new files
    
    Args:
        output_dir: Output directory to upload
        root_folder_id: Root Drive folder ID
    """
    from datetime import datetime
    
    drive = DriveConnector()
    stats = {"uploaded": 0, "skipped": 0, "archived": 0}
    
    # Walk through output directory
    for root, dirs, files in os.walk(output_dir):
        rel_path = os.path.relpath(root, output_dir)
        
        if rel_path == ".":
            # Skip root directory - we only version individual song folders
            continue
        
        # Get folder name (e.g., "bien_cordialement")
        path_parts = Path(rel_path).parts
        if len(path_parts) > 1:
            # Skip nested folders (like en_construction/song_name)
            continue
        
        folder_name = path_parts[0]
        
        print(f"\n📁 Processing folder: {folder_name}")
        
        # Check if folder exists on Drive
        existing_folders = drive.list_folder(root_folder_id)
        folder_id = None
        for folder in existing_folders:
            if folder.get("name") == folder_name and folder.get("mimeType") == "application/vnd.google-apps.folder":
                folder_id = folder["id"]
                break
        
        if folder_id:
            print(f"   ✓ Folder exists, checking for versioning...")
            
            # Look for .mscz file with folder name
            mscz_filename = f"{folder_name}.mscz"
            existing_mscz = drive.find_file_in_folder(folder_id, mscz_filename)
            
            if existing_mscz:
                print(f"   📦 Archiving old version: {mscz_filename}")
                
                # Get modification date
                metadata = drive.get_file_metadata(existing_mscz["id"])
                # Parse ISO format: 2026-01-12T17:30:00.000Z
                mod_time = datetime.fromisoformat(metadata["modifiedTime"].replace('Z', '+00:00'))
                date_str = mod_time.strftime("%Y-%m-%d")
                
                # Create/get 'old' subfolder
                old_folder_id = drive.create_folder("old", folder_id)
                
                # Rename file with timestamp
                base_name = folder_name
                archived_name = f"{base_name}_{date_str}.mscz"
                drive.rename_file(existing_mscz["id"], archived_name)
                
                # Move to 'old' folder
                drive.move_file(existing_mscz["id"], old_folder_id)
                stats["archived"] += 1
                print(f"   ✓ Archived as: old/{archived_name}")
            
            # Clean folder contents (preserve 'old' subfolder)
            print(f"   🧹 Cleaning folder (preserving 'old/')...")
            drive.delete_folder_contents(folder_id, preserve_folders=["old"])
        else:
            # Create new folder
            print(f"   ✓ Creating new folder...")
            folder_id = drive.create_folder(folder_name, root_folder_id)
        
        # Upload all files in this folder
        print(f"   📤 Uploading files...")
        for file in files:
            file_path = os.path.join(root, file)
            print(f"      → {file}")
            
            try:
                drive.upload_file(file_path, folder_id, replace=False)
                stats["uploaded"] += 1
            except Exception as e:
                print(f"         ❌ Error: {e}")
                stats["skipped"] += 1
        
        print(f"   ✅ Completed: {folder_name}")
    
    return stats


def main():
    # Verify DRIVE_ROOT_FOLDER_ID
    root_folder_id = os.getenv("DRIVE_ROOT_FOLDER_ID")
    if not root_folder_id:
        print("❌ Error: DRIVE_ROOT_FOLDER_ID not defined in .env")
        print("\nAdd to .env:")
        print("  DRIVE_ROOT_FOLDER_ID='your_folder_id'")
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
