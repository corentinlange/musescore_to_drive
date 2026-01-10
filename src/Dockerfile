# Base image
FROM ubuntu:22.04

# Metadata
LABEL maintainer="MuseScore to Drive"
LABEL description="MuseScore processor for automated PDF and MP3 conversion"

# Install system dependencies (same as working GitHub Actions workflow)
RUN apt-get update && apt-get install -y \
    wget curl jq \
    python3 python3-pip \
    libjack-jackd2-0 libopengl0 libgl1-mesa-glx libegl1-mesa \
    libwayland-client0 libxcb-xinerama0 libxcb-icccm4 libxcb-image0 \
    libasound2 libnss3 libglib2.0-0 libxcb-cursor0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY tools/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# MuseScore AppImage URL (can be overridden at build time)
# Default: stable version 4.5.1 (tested and verified)
# To use latest: docker build --build-arg MUSESCORE_URL=$(./src/scripts/get-musescore-url.sh) -t musescore-processor ./src
ARG MUSESCORE_URL=https://cdn.jsdelivr.net/musescore/v4.5.1/MuseScore-Studio-4.5.1.250800846-x86_64.AppImage

# Download and extract MuseScore AppImage
RUN echo "Downloading MuseScore from: ${MUSESCORE_URL}" && \
    wget -q --show-progress "${MUSESCORE_URL}" -O /tmp/MuseScore.AppImage && \
    chmod +x /tmp/MuseScore.AppImage && \
    cd /opt && /tmp/MuseScore.AppImage --appimage-extract && \
    mv squashfs-root musescore && \
    rm /tmp/MuseScore.AppImage && \
    echo "MuseScore installed successfully"

# Environment variables
ENV PATH="/opt/musescore:$PATH"
ENV QT_QPA_PLATFORM=offscreen

WORKDIR /workspace
