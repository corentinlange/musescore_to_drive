# Structure du projet - src/

## 📁 Structure actuelle

```
src/
├── drive-api/              # 🌐 API Google Drive
│   ├── connector.py        # Bibliothèque DriveConnector (connexion, upload, delete, etc.)
│   ├── config.py           # Configuration Drive (folders IDs)
│   ├── upload.py           # Commande: Upload vers Drive
│   └── list_tree.py        # Commande: Afficher arborescence Drive
│
├── musescore/              # 🎵 MuseScore processing
│   ├── process.sh          # Script principal: MSCZ → PDF/MP3
│   ├── decode_parts.py     # Décode JSON parts → MSCZ individuels
│   └── get-version.sh      # Récupère dernière version MuseScore
│
├── scripts/                # 📜 Scripts utilitaires (legacy)
│   ├── upload_to_drive.sh  # Wrapper bash upload
│   ├── list_drive.sh       # Wrapper bash list
│   ├── local.py            # Test local
│   └── update_full_mscz.py # Update complet
│
├── docs/                   # 📚 Documentation
│   ├── SETUP.md
│   └── local-testing.md
│
└── Dockerfile              # 🐳 Image Docker
```

## 🎯 Usage

### MuseScore Processing

```bash
# Convertir MSCZ → PDF/MP3
docker run --rm -v ${PWD}:/workspace -w /workspace \
  musescore-processor:stable \
  bash ./src/musescore/process.sh fichier.mscz

# Récupérer latest version
./src/musescore/get-version.sh
```

### Google Drive API

```python
# Upload fichier
python src/drive-api/upload.py fichier.pdf

# Afficher arborescence
python src/drive-api/list_tree.py [folder_id]
```

## 🔄 Migration

- ✅ `src/tools/decode_json_parts.py` → `src/musescore/decode_parts.py`
- ✅ `src/scripts/drive_connector.py` → `src/drive-api/connector.py`
- ✅ `src/tools/list_drive_tree.py` → `src/drive-api/list_tree.py`
- ✅ `src/tools/upload_to_drive.py` → `src/drive-api/upload.py`
- ✅ `src/scripts/process_musescore.sh` → `src/musescore/process.sh`
- ✅ `src/scripts/get-musescore-url.sh` → `src/musescore/get-version.sh`

## 📝 Prochaines étapes (optionnel)

- Nettoyer `src/scripts/` et `src/tools/` (déprécier ou supprimer anciens fichiers)
- Ajouter `__init__.py` dans `drive-api` pour en faire un package Python propre
