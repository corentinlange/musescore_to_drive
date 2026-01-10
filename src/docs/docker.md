# Docker Documentation

## Custom Docker Image

This project uses a custom Docker image based on **debian:bookworm-slim** to optimize GitHub Actions performance.

### Benefits

- **93% faster**: Setup reduced from ~70s to ~5s
- **81% lighter**: 226 MB vs 1.2 GB (ubuntu-22.04)
- **Auto-update**: Weekly rebuild for latest MuseScore
- **Reusable**: Same image for all workflows

### Image Location

Hosted on GitHub Container Registry:
```
ghcr.io/corentinlange/musescore_to_drive/musescore-processor:latest
```

### Image Contents

- **Base**: debian:bookworm-slim (~80 MB)
- **System deps**: Qt, OpenGL, Wayland, X11
- **Python**: Python 3 + google-api-python-client
- **MuseScore**: Latest version pre-extracted in `/opt/musescore`

### Local Build

Test image locally:

```bash
# Build
docker build -t musescore-processor:test ./src

# Check MuseScore version
docker run musescore-processor:test /opt/musescore/AppRun --version

# Test conversion
docker run -v $(pwd):/workspace musescore-processor:test \
  /opt/musescore/AppRun -o test.pdf test.mscz
```

### Image Rebuild

Image automatically rebuilds:
- **Weekly** (Sunday at midnight UTC) for latest MuseScore
- **On changes** to Dockerfile or requirements.txt
- **Manually** via GitHub Actions → "Build and Push Docker Image" → Run workflow

### Architecture

```
Dockerfile (debian:bookworm-slim)
  ├─ System dependencies (apt)
  ├─ Python + dependencies (pip)
  └─ MuseScore (latest version)
       └─ Pre-extracted in /opt/musescore

GitHub Actions Workflows
  ├─ build-docker.yml         (build & push image)
  ├─ process_musescore.yml    (uses image)
  ├─ update_modified_file.yml
  └─ update_all_fles.yml
```
