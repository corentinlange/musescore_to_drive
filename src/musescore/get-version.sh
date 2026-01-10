#!/bin/bash
# Fetch the latest MuseScore AppImage URL from GitHub releases

set -e

# GitHub API endpoint for latest release
API_URL="https://api.github.com/repos/musescore/MuseScore/releases/latest"

# Fetch latest release info
RELEASE_JSON=$(curl -s "$API_URL")

# Try jq first, fallback to grep/sed if jq not available
if command -v jq &> /dev/null; then
  APPIMAGE_URL=$(echo "$RELEASE_JSON" | \
    jq -r '.assets[] | select(.name | contains("x86_64.AppImage") and (contains("x86_64.AppImage.zsync") | not)) | .browser_download_url' | \
    head -1)
else
  # Fallback: use grep and sed
  APPIMAGE_URL=$(echo "$RELEASE_JSON" | \
    grep -o '"browser_download_url":[[:space:]]*"[^"]*x86_64\.AppImage"' | \
    grep -v 'zsync' | \
    sed 's/.*"browser_download_url":[[:space:]]*"\([^"]*\)".*/\1/' | \
    head -1)
fi

if [ -z "$APPIMAGE_URL" ]; then
  echo "Error: Could not fetch latest MuseScore AppImage URL" >&2
  exit 1
fi

echo "$APPIMAGE_URL"
