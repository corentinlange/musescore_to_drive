FROM debian:bookworm-slim

# Métadonnées
LABEL org.opencontainers.image.source=https://github.com/corentinlange/musescore_to_drive
LABEL org.opencontainers.image.description="MuseScore processor with pre-installed dependencies"

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    wget curl jq \
    python3 python3-pip \
    libjack-jackd2-0 libopengl0 libgl1-mesa-glx \
    libegl1-mesa libwayland-client0 \
    libxcb-xinerama0 libxcb-icccm4 libxcb-image0 \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY tools/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Téléchargement et extraction de MuseScore (dernière version)
RUN LATEST_RELEASE=$(curl -s https://api.github.com/repos/musescore/MuseScore/releases/latest) && \
    VERSION=$(echo "$LATEST_RELEASE" | jq -r '.tag_name' | sed 's/^v//') && \
    APPIMAGE_URL=$(echo "$LATEST_RELEASE" | jq -r '.assets[] | select(.name | contains("x86_64.AppImage")) | .browser_download_url' | head -1) && \
    echo "Téléchargement de MuseScore Studio v$VERSION" && \
    echo "URL: $APPIMAGE_URL" && \
    wget "$APPIMAGE_URL" -O /tmp/musescore.AppImage && \
    chmod +x /tmp/musescore.AppImage && \
    cd /opt && /tmp/musescore.AppImage --appimage-extract && \
    mv squashfs-root musescore && \
    rm /tmp/musescore.AppImage

# Configuration des variables d'environnement
ENV PATH="/opt/musescore:$PATH"
ENV QT_QPA_PLATFORM=offscreen

WORKDIR /workspace
