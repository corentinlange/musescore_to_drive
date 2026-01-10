#!/usr/bin/env python3
"""
DEPRECATED - Use upload_all.py instead

Legacy single-file upload script.
New projects should use: python src/drive-api/upload_all.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from connector import DriveConnector

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python upload.py <file_path> <parent_folder_id>")
        sys.exit(1)
    
    print("⚠️  This script is deprecated. Use upload_all.py for better features.")
    
    drive = DriveConnector()
    drive.upload_file(sys.argv[1], sys.argv[2], replace=True)
