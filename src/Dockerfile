FROM debian:bookworm-slim

# Metadata
LABEL org.opencontainers.image.source=https://github.com/corentinlange/musescore_to_drive
LABEL org.opencontainers.image.description="MuseScore processor with pre-installed dependencies"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget curl jq \
    python3 python3-pip \
    libjack-jackd2-0 libopengl0 libgl1-mesa-glx \
    libegl1-mesa libwayland-client0 \
    libxcb-xinerama0 libxcb-icccm4 libxcb-image0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY tools/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Download and extract MuseScore (auto-detect latest version)
RUN set -x && \
    echo "=== Step 1: Fetch GitHub release ===" && \
    LATEST_RELEASE=$(curl -sL -H "User-Agent: Docker-MuseScore-Builder" "https://api.github.com/repos/musescore/MuseScore/releases/latest") && \
    echo "API response received (${#LATEST_RELEASE} bytes)" && \
    \
    echo "=== Step 2: Extract version ===" && \
    VERSION=$(echo "$LATEST_RELEASE" | sed -n 's/.*"tag_name": *"\([^"]*\)".*/\1/p' | sed 's/^v//' | head -1) && \
    echo "VERSION=${VERSION}" && \
    \
    echo "=== Step 3: Extract AppImage URL ===" && \
    APPIMAGE_URL=$(echo "$LATEST_RELEASE" | grep "browser_download_url" | grep "x86_64.AppImage" | sed 's/.*: *"\([^"]*\)".*/\1/' | head -1) && \
    echo "APPIMAGE_URL=${APPIMAGE_URL}" && \
    \
    if [ -z "$APPIMAGE_URL" ]; then \
        echo "WARNING: AppImage not found in API response, using fallback"; \
        APPIMAGE_URL="https://github.com/musescore/MuseScore/releases/download/v4.4.4/MuseScore-Studio-4.4.4.241220200-x86_64.AppImage"; \
    fi && \
    \
    echo "=== Step 4: Download AppImage ===" && \
    wget -q --show-progress "$APPIMAGE_URL" -O /tmp/musescore.AppImage && \
    ls -lh /tmp/musescore.AppImage && \
    \
    echo "=== Step 5: Extract AppImage ===" && \
    chmod +x /tmp/musescore.AppImage && \
    cd /opt && /tmp/musescore.AppImage --appimage-extract && \
    mv squashfs-root musescore && \
    rm /tmp/musescore.AppImage && \
    \
    echo "=== Step 6: Verify installation ===" && \
    /opt/musescore/AppRun --version

# Environment variables
ENV PATH="/opt/musescore:$PATH"
ENV QT_QPA_PLATFORM=offscreen

WORKDIR /workspace
