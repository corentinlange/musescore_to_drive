# Local Testing Guide

Guide for testing scripts locally before pushing to CI.

---

## Prerequisites

### 1. MuseScore Installed

**Option A: Local installation (recommended)**
- Linux: `sudo apt install musescore3` or download from musescore.org
- macOS: Download from musescore.org
- Windows: Download from musescore.org

**Option B: Docker**
```bash
docker build -t musescore-processor:local ./src
```

**Option C: AppImage (Linux)**
```bash
wget https://github.com/musescore/MuseScore/releases/download/v4.4.4/MuseScore-Studio-4.4.4.241220200-x86_64.AppImage
chmod +x MuseScore-*.AppImage
./MuseScore-*.AppImage --appimage-extract
```

### 2. Python Environment

Create virtual environment:

```bash
# With uv (recommended)
uv venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -r src/tools/requirements.txt
```

### 3. Configure Secrets

```bash
# Copy template
cp .env.example .env

# Edit .env with your keys
nano .env
```

`.env` format:
```bash
GCP_SERVICE_ACCOUNT_KEY_B64='YOUR_BASE64_ENCODED_JSON_HERE'
DRIVE_FOLDER_ID='YOUR_DRIVE_FOLDER_ID_HERE'
```

Encode your JSON:
```bash
# Linux/macOS/WSL
cat service-account.json | base64 -w 0

# Windows PowerShell
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((Get-Content service-account.json -Raw)))
```

> Important: `.env` is in `.gitignore` - never commit it

---

## Usage

### Quick Test

```bash
# With venv activated
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Test conversion
./src/scripts/process_musescore.sh test.mscz

# Check output
ls output/test/

# Test upload
./src/scripts/upload_to_drive.sh
```

### Available Scripts

| Script | Description | Example |
|--------|-------------|---------|
| `process_musescore.sh` | Convert MSCZ to PDF/MP3 | `./src/scripts/process_musescore.sh *.mscz` |
| `upload_to_drive.sh` | Upload to Drive | `./src/scripts/upload_to_drive.sh` |
| `list_drive.sh` | Display Drive tree | `./src/scripts/list_drive.sh [folder_id]` |

### Conversion Details

**process_musescore.sh** performs:
1. MP3 generation
2. Individual parts extraction
3. PDF generation

Output in `output/<filename>/` directory.

### Upload Details

**upload_to_drive.sh** performs:
1. Load `.env` config
2. Decode base64 service account
3. Upload all files from `output/` folders

---

## Troubleshooting

### MuseScore Not Found

**Solutions**:
1. Install MuseScore: `sudo apt install musescore3`
2. Extract AppImage: `./MuseScore-*.AppImage --appimage-extract`
3. Use Docker: `docker build -t musescore-processor:local ./src`

### GCP_SERVICE_ACCOUNT_KEY_B64 Not Defined

**Solutions**:
1. Check `.env` exists: `ls -la .env`
2. Check content: `cat .env`
3. Content must be base64 (not raw JSON)
4. Encode JSON: `cat service-account.json | base64 -w 0`

### Python Module Error

```bash
# Activate venv
source .venv/bin/activate

# Install dependencies
pip install -r src/tools/requirements.txt
```

### Permission Denied on Scripts

```bash
chmod +x src/scripts/*.sh
```

---

## Development Workflow

Recommended workflow:

```bash
# 1. Edit/create in MuseScore
# 2. Save .mscz at project root

# 3. Test locally
source .venv/bin/activate
./src/scripts/process_musescore.sh my_song.mscz

# 4. Check output
ls output/my_song/

# 5. Test upload (optional)
./src/scripts/upload_to_drive.sh

# 6. If OK, commit and push
git add my_song.mscz
git commit -m "Add new song"
git push
```

---

## Comparison: Local vs CI

| Aspect | Local | CI |
|--------|-------|-----|
| **Speed** | Instant | 1-2 min |
| **Setup** | Python + MuseScore | Docker image |
| **Secrets** | `.env` file | GitHub Secrets |
| **Output** | `output/` folder | Uploaded to Drive |
| **Use case** | Quick testing | Production |

---

## Debug Mode

Use `--debug` flag for detailed output:

```bash
./src/scripts/list_drive.sh --debug
```

Displays:
- .env loading
- Environment variables
- Base64 decoding
- API calls

---

## Tips

**Tip 1**: Test conversion before upload
```bash
./src/scripts/process_musescore.sh file.mscz
# Check output/file/ folder
# Only then: ./src/scripts/upload_to_drive.sh
```

**Tip 2**: Use Docker for exact CI environment
```bash
docker build -t musescore-processor:local ./src
docker run -v $(pwd):/workspace musescore-processor:local \
  ./src/scripts/process_musescore.sh test.mscz
```

**Tip 3**: List Drive to verify uploads
```bash
./src/scripts/list_drive.sh
```
