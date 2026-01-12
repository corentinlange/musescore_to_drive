# MuseScore to Drive - Setup Guide

Complete guide to fork and configure this project.

---

## Two Usage Modes

### Mode 1: CI Only (Recommended - 10 min)
- No local installation required
- Everything runs in GitHub Actions
- Just add .mscz files and push

### Mode 2: Local Testing (Advanced - 30 min)
- Test before pushing
- Requires Python + MuseScore locally
- See [complete guide](src/docs/local-testing.md)

---

## CI Setup (10 minutes)

### 1. Fork the Repository

1. Click **Fork** (top right)
2. GitHub creates your personal copy
3. No need to clone locally

### 2. Create Google OAuth 2.0 Credentials

> **Why OAuth 2.0?** GitHubBot uploads files to **your personal Google Drive** acting as you. Service Accounts cannot access personal Drive folders directly.

#### A. Enable Google Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. **Create new project** (e.g., "musescore-to-drive")
3. Select your project from the dropdown
4. **APIs & Services** → **Library**
5. Search **"Google Drive API"**
6. Click **Enable**

#### B. Configure OAuth Consent Screen

1. **APIs & Services** → **OAuth consent screen**
2. Select **External** (unless you have a Google Workspace)
3. Click **Create**
4. Fill in required fields:
   - **App name**: `MuseScore to Drive`
   - **User support email**: Your email
   - **Developer contact**: Your email
5. Click **Save and Continue**
6. **Scopes**: Click **Add or Remove Scopes**
   - Search and select: `https://www.googleapis.com/auth/drive`
   - Click **Update** → **Save and Continue**
7. **Test users**: Click **Add Users**
   - Add your Google email
   - Click **Save and Continue**
8. Click **Back to Dashboard**

#### C. Create OAuth 2.0 Client ID

1. **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Application type: **Desktop app**
4. Name: `MuseScore Desktop Client`
5. Click **Create**
6. **Download JSON** (click download icon) → Save as `credentials.json`
   - ⚠️ **Warning**: Never commit this file to Git

### 3. Generate User Token (OAuth 2.0 Authentication)

You need to authenticate once to generate a `token.json` file that allows GitHubBot to upload files as you.

#### A. Install Python Dependencies (One-time)

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

#### B. Run Authentication Script

Create a file `generate_token.py`:

```python
#!/usr/bin/env python3
"""Generate OAuth 2.0 token for Google Drive access"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    creds = None
    
    # Check if token already exists
    if os.path.exists('token.json'):
        print("⚠️  token.json already exists. Delete it first if you want to regenerate.")
        return
    
    if not os.path.exists('credentials.json'):
        print("❌ Error: credentials.json not found")
        print("   Download it from Google Cloud Console (OAuth 2.0 Client)")
        return
    
    # Run OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    # Save token
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    
    print("\n✅ token.json created successfully!")
    print("   This file contains your OAuth 2.0 access token")
    print("   ⚠️  Keep it secret - never commit to Git")

if __name__ == '__main__':
    main()
```

Run the script:

```bash
python generate_token.py
```

This will:
1. Open your browser
2. Ask you to sign in to Google
3. Show permissions request → Click **Allow**
4. Generate `token.json` file

> **Important**: The `token.json` contains refresh tokens, so it won't expire and GitHubBot can keep using it.

### 4. Get Your Drive Folder ID

1. Go to [Google Drive](https://drive.google.com)
2. **Create or open** the folder where you want files uploaded
   - Example: "MuseScore Sheets"
3. **Copy folder ID** from URL:
   ```
   https://drive.google.com/drive/folders/1AbC2DeF3GhI4JkL5MnO
                                          ^^^^^^^^^^^^^^^^^
                                          This is the folder ID
   ```

> **Note**: No need to share this folder - it's already yours, and GitHubBot will act as you.

### 5. Encode Token to Base64

Convert `token.json` to base64 for GitHub secrets.

#### Option A: Command Line (Recommended)

**Git Bash (Windows) / Linux / macOS:**
```bash
cat token.json | base64 -w 0
```

**PowerShell (Windows):**
```powershell
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((Get-Content token.json -Raw)))
```

#### Option B: Online Tool

1. Go to https://www.base64encode.org/
2. Paste **entire content** of `token.json`
3. Click "Encode"
4. Copy result (very long string)

### 6. Configure GitHub Secrets

1. Go to your fork on GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

#### Secret 1: GDRIVE_TOKEN

- **Name**: `GDRIVE_TOKEN`
- **Value**: Paste the base64-encoded string from step 5
- Click **Add secret**

#### Secret 2: DRIVE_FOLDER_ID

- **Name**: `DRIVE_FOLDER_ID`
- **Value**: Paste the folder ID from step 4
- Click **Add secret**

> ✅ **You're done!** GitHubBot can now upload to your Google Drive as you.

### 6. Build Docker Image (Optional but Recommended)

For faster workflows (~5s instead of ~70s):

1. Your fork → **Actions**
2. If prompted, **Enable GitHub Actions**
3. **Actions** tab → **"Build and Push Docker Image"**
4. **Run workflow**
5. Wait ~5 minutes (first time)
6. Once complete:
   - GitHub → **Packages** (top right)
   - Click `musescore-processor`
   - **Package settings** → **Change visibility** → **Public**

---

## Test: Add Your First Sheet

### Via GitHub Interface (No Git)

1. Your fork → Click **Add file** → **Upload files**
2. Drag and drop your `.mscz` file
3. Commit message: "Add my first song"
4. Click **Commit changes**
5. **Actions** → "Update modified musescore on drive" starts automatically
6. Wait 1-2 minutes
7. **Check Google Drive** → your folder contains:
   - Original `.mscz` file
   - PDF
   - MP3
   - Individual parts (if applicable)

### Via Git (Alternative)

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/musescore_to_drive.git
cd musescore_to_drive

# Add .mscz file
# (create with MuseScore or copy existing file)

# Commit and push
git add my_song.mscz
git commit -m "Add my first song"
git push

# Go to GitHub → Actions to see workflow
```

---

## Daily Usage

It's simple:

1. **Add/modify .mscz file** (via GitHub or Git)
2. **Push to `main` branch**
3. **Done!** GitHub Actions handles the rest

The workflow automatically:
- Detects modified `.mscz` files
- Converts to PDF and MP3
- Extracts individual parts
- Uploads everything to Drive folder

---

## Advanced Configuration

### Change Drive Folder

To upload to different folder:
1. Settings → Secrets → `DRIVE_FOLDER_ID`
2. Edit → Enter new ID

### Rebuild Docker Image

- Automatic: Every Sunday at midnight
- Manual: Actions → "Build and Push Docker Image" → Run workflow

### Test Locally Before Push

See [local testing guide](src/docs/local-testing.md).

---

## Troubleshooting

### Workflow Fails with "Permission Denied"

**Solution**: Enable write permissions for GitHub Actions
1. Settings → Actions → General
2. Workflow permissions → **Read and write permissions**

### Nothing Appears on Drive

**Checks**:
1. `GDRIVE_TOKEN` secret valid?
   - Verify you completed OAuth 2.0 flow successfully
   - Check if `token.json` was encoded correctly to base64
   - Try regenerating token with `generate_token.py`
2. `DRIVE_FOLDER_ID` secret correct?
   - Compare with folder URL
   - Make sure it's the folder ID, not the full URL
3. OAuth 2.0 permissions granted?
   - Check if you clicked "Allow" during authentication
   - Verify scope `https://www.googleapis.com/auth/drive` is included

### Workflow Slow (~70s Setup)

**Solution**: Build Docker image (see step 6 above)

### Error "Container Image Not Found"

**Solutions**:
1. Build Docker image (step 6)
2. Or edit `.github/workflows/process_musescore.yml`:
   ```yaml
   # Comment this section:
   # container:
   #   image: ghcr.io/...
   ```

---

## Documentation

- [Architecture and features](README.md)
- [Local testing (advanced)](src/docs/local-testing.md)
- [Docker](src/docs/docker.md)

---

## Support

Having issues?
1. Check [existing issues](https://github.com/corentinlange/musescore_to_drive/issues)
2. Create new issue with:
   - Problem description
   - GitHub Actions logs
   - Screenshots if relevant
