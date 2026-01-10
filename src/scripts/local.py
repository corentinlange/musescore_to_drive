# DEPRECATED - Use upload_all.py instead
#
# This script is kept for backward compatibility
# New code should use: python src/drive-api/upload_all.py

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'drive-api'))

# Redirect to upload_all
print("⚠️  This script is deprecated. Use: python src/drive-api/upload_all.py")
print("Redirecting...")

from upload_all import main
main()
