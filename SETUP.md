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

### 2. Create Google Service Account

#### A. Enable Google Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. **Create new project** (e.g., "musescore-to-drive")
3. **APIs & Services** → **Library**
4. Search **"Google Drive API"**
5. Click **Enable**

#### B. Create Service Account

1. **IAM & Admin** → **Service Accounts**
2. **Create Service Account**
   - Name: `musescore-uploader`
   - Description: "Uploads MuseScore files to Drive"
   - Role: (leave empty)
3. Click **Done**
4. In the list, click on created service account
5. **Keys** → **Add Key** → **Create new key** → **JSON**
6. **Download JSON file** (e.g., `service-account.json`)
   - Warning: Never commit this file

### 3. Create Google Drive Folder

1. Go to [Google Drive](https://drive.google.com)
2. **Create new folder** (e.g., "MuseScore Sheets")
3. **Right-click folder** → **Share**
4. **Add service account email**:
   - Found in downloaded JSON → `client_email` field
   - Example: `musescore-uploader@my-project.iam.gserviceaccount.com`
   - Role: **Editor**
   - Uncheck "Notify people"
5. **Copy folder ID** from URL:
   ```
   https://drive.google.com/drive/folders/1AbC2DeF3GhI4JkL5MnO
                                          ^^^^^^^^^^^^^^^^^
                                          This is the folder ID
   ```

### 4. Encode Key to Base64

Convert JSON to base64 for GitHub secrets.

#### Option A: Online (Quick)

1. Go to https://www.base64encode.org/
2. Paste **entire content** of `service-account.json`
3. Click "Encode"
4. Copy result (very long string)

#### Option B: Command Line

**Git Bash (Windows) / Linux / macOS:**
```bash
cat service-account.json | base64 -w 0
```

**PowerShell (Windows):**
```powershell
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((Get-Content service-account.json -Raw)))
```

### 5. Configure GitHub Secrets

1. Your fork → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**:
   - Name: `GCP_SERVICE_ACCOUNT_KEY_B64`
   - Value: [Paste base64 from step 4]
   - Click "Add secret"

3. **New repository secret**:
   - Name: `DRIVE_FOLDER_ID`
   - Value: [Folder ID from step 3]
   - Click "Add secret"

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
1. Service account has access to Drive folder?
   - Check folder sharing settings
2. `DRIVE_FOLDER_ID` secret correct?
   - Compare with folder URL
3. `GCP_SERVICE_ACCOUNT_KEY_B64` valid?
   - Try re-encoding

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
