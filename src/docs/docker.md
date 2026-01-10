# MuseScore to Drive - Docker Documentation

## 🐳 Image Docker personnalisée

Ce projet utilise une image Docker personnalisée basée sur **debian:slim** pour optimiser les performances des workflows GitHub Actions.

### Avantages

- ⚡ **93% plus rapide** : Setup réduit de ~70s à ~5s
- 💾 **81% plus léger** : 226 MB vs 1.2 GB (ubuntu-22.04)
- 🔄 **Auto-update** : Rebuild hebdomadaire pour la dernière version de MuseScore
- ♻️ **Réutilisable** : Même image pour tous les workflows

### Image

L'image est hébergée sur GitHub Container Registry :
```
ghcr.io/corentinlange/musescore_to_drive/musescore-processor:latest
```

### Contenu de l'image

- **Base** : debian:slim (~36 MB)
- **Dépendances système** : Qt, OpenGL, Wayland, X11
- **Python** : Python 3 + google-api-python-client
- **MuseScore** : Dernière version pré-extraite dans `/opt/musescore`

### Build local

Pour tester l'image localement :

```bash
# Build
docker build -t musescore-processor:test .

# Vérifier la version de MuseScore
docker run musescore-processor:test /opt/musescore/AppRun --version

# Tester une conversion
docker run -v $(pwd):/workspace musescore-processor:test \
  /opt/musescore/AppRun -o test.pdf test.mscz
```

### Rebuild de l'image

L'image est automatiquement rebuildée :
- **Chaque semaine** (dimanche à minuit UTC) pour avoir la dernière version de MuseScore
- **À chaque modification** du Dockerfile ou des requirements.txt
- **Manuellement** via GitHub Actions → "Build and Push Docker Image" → "Run workflow"

### Architecture

```
Dockerfile (debian:slim)
  ├─ Dépendances système (apt)
  ├─ Python + dépendances (pip)
  └─ MuseScore (dernière version)
       └─ Pré-extrait dans /opt/musescore

Workflows GitHub Actions
  ├─ build-docker.yml     (build & push image)
  ├─ process_musescore.yml (utilise l'image)
  ├─ update_modified_file.yml
  └─ update_all_fles.yml
```
