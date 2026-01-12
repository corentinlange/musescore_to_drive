#!/bin/bash
set -e

# Upload to Google Drive Script
# Executed automatically by GitHubBot via GitHub Actions when .mscz files are modified
# Usage: ./scripts/upload_to_drive.sh

# Configuration
OUTPUT_DIR="output"

# Load .env if present (local mode)
if [ -f ".env" ]; then
    echo "📋 Loading .env..."
    export $(grep -v '^#' .env | xargs)
fi

# Verify GCP_SERVICE_ACCOUNT_KEY_B64 is defined
if [ -z "$GCP_SERVICE_ACCOUNT_KEY_B64" ]; then
    echo "❌ Error: GCP_SERVICE_ACCOUNT_KEY_B64 not defined"
    echo ""
    echo "Solutions:"
    echo "  1. Local mode: Create .env file with:"
    echo "     GCP_SERVICE_ACCOUNT_KEY_B64='<your_json_base64_encoded>'"
    echo ""
    echo "  2. CI mode: Set GitHub secret GCP_SERVICE_ACCOUNT_KEY_B64"
    echo ""
    echo "  3. Manual:"
    echo "     export GCP_SERVICE_ACCOUNT_KEY_B64='<base64>'"
    echo ""
    echo "  To encode your JSON to base64:"
    echo "     cat service-account.json | base64 -w 0"
    exit 1
fi

# Decode base64 and export as SERVICE_ACCOUNT for Python scripts
export SERVICE_ACCOUNT=$(echo "$GCP_SERVICE_ACCOUNT_KEY_B64" | base64 -d)

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "☁️  Upload to Google Drive"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verify upload script exists
if [ ! -f "src/tools/upload_to_drive.py" ]; then
    echo "❌ Error: src/tools/upload_to_drive.py not found"
    exit 1
fi

total_uploaded=0

# Process all MSCZ files and upload to Drive
for mscz_file in *.mscz; do
    if [ ! -f "$mscz_file" ]; then
        echo "⚠️  No .mscz files found in current directory"
        break
    fi
    
    base_name=$(basename "$mscz_file" .mscz)
    output_dir="$OUTPUT_DIR/${base_name}"
    
    if [ ! -d "$output_dir" ] || [ -z "$(ls -A "$output_dir" 2>/dev/null)" ]; then
        echo "⚠️  Empty or missing folder: $output_dir"
        continue
    fi
    
    echo ""
    echo "📤 Upload: $base_name"
    
    # Upload original MSCZ file
    echo "   → $mscz_file"
    python3 src/tools/upload_to_drive.py "$mscz_file" "$base_name"
    ((total_uploaded++))
    
    # Upload all generated files
    for output_file in "$output_dir"/*; do
        if [ -f "$output_file" ]; then
            echo "   → $(basename "$output_file")"
            python3 src/tools/upload_to_drive.py "$output_file" "$base_name"
            ((total_uploaded++))
        fi
    done
    
    echo "✅ Upload completed: $base_name"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Upload completed! ($total_uploaded files uploaded)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
