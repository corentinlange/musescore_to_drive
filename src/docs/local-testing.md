# 🧪 Test en Local - MuseScore to Drive

Ce guide explique comment tester les workflows **en local** avant de les exécuter dans GitHub Actions.

## Avantages du test local

- ⚡ **Rapidité** : Pas besoin de push pour tester
- 🐛 **Debugging** : Plus facile de débugger localement
- 💰 **Économie** : Pas de consommation de minutes GitHub Actions
- ✅ **Confiance** : Tester avant de commit

---

## Prérequis

### 1. MuseScore installé

Choisissez une option :

**Option A : Installation locale (recommandé)**
- **Linux** : `sudo apt install musescore3` ou télécharger depuis [musescore.org](https://musescore.org)
- **macOS** : `brew install musescore` ou télécharger depuis [musescore.org](https://musescore.org)
- **Windows** : Télécharger depuis [musescore.org](https://musescore.org) ou utiliser WSL

**Option B : AppImage (Linux uniquement)**
```bash
# Télécharger la dernière version
wget https://github.com/musescore/MuseScore/releases/download/v4.6.5/MuseScore-Studio-4.6.5.253511702-x86_64.AppImage

# Extraire
chmod +x MuseScore-Studio-4.6.5.253511702-x86_64.AppImage
./MuseScore-Studio-4.6.5.253511702-x86_64.AppImage --appimage-extract
# MuseScore sera disponible dans ./squashfs-root/AppRun
```

**Option C : Docker (tous OS)**
```bash
# Build l'image locale
docker build -t musescore-processor:local .

# Utiliser avec les scripts
docker run -v $(pwd):/workspace -w /workspace musescore-processor:local \
  ./scripts/process_musescore.sh test.mscz
```

### 2. Python avec dépendances

```bash
# Créer venv avec uv (rapide)
uv venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Installer dépendances
uv pip install -r src/tools/requirements.txt
```

### 3. Configuration des secrets

```bash
# Copier le template
cp .env.example .env

# Éditer .env avec vos vraies clés
nano .env  # ou votre éditeur préféré
```

Format du fichier `.env` :
```bash
GCP_SERVICE_ACCOUNT_KEY_B64='YOUR_BASE64_ENCODED_JSON_HERE'
```

Pour encoder votre JSON :
```bash
# Linux/macOS/WSL
cat service-account.json | base64 -w 0

# Windows PowerShell
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((Get-Content service-account.json -Raw)))
```

> ⚠️ **Important** : `.env` est dans `.gitignore` - ne le committez JAMAIS !

---

## Utilisation

### Test de conversion uniquement

```bash
# Convertir un seul fichier
./scripts/process_musescore.sh mon_fichier.mscz

# Convertir plusieurs fichiers
./scripts/process_musescore.sh *.mscz

# Convertir avec debug
bash -x ./scripts/process_musescore.sh test.mscz
```

**Résultat** : Fichiers générés dans `output/nom_fichier/`
- `nom_fichier.mp3` - Audio
- `nom_fichier.pdf` - Partition complète
- `partie1.pdf`, `partie2.pdf`, ... - Parties individuelles

### Test d'upload uniquement

```bash
# Upload vers Drive (nécessite .env configuré)
./scripts/upload_to_drive.sh
```

### Test complet (conversion + upload)

```bash
# Workflow complet
./scripts/process_musescore.sh *.mscz && ./scripts/upload_to_drive.sh
```

---

## Résolution de problèmes

### ❌ `MuseScore non trouvé`

**Solutions** :
1. Installer MuseScore localement (voir Prérequis)
2. Extraire l'AppImage : `./MuseScore-*.AppImage --appimage-extract`
3. Utiliser Docker : `docker build -t musescore-processor:local .`

### ❌ `GCP_SERVICE_ACCOUNT_KEY_B64 non défini`

**Solutions** :
1. Vérifier que `.env` existe : `ls -la .env`
2. Vérifier le format dans `.env` : `cat .env`
3. Le contenu doit être du **base64** (pas du JSON brut)
4. Encoder votre JSON : `cat service-account.json | base64 -w 0`

### ❌ Erreur Python `No module named 'google'`

**Solution** :
```bash
# Activer venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Installer dépendances
# Installer dépendances
pip install -r tools/requirements.txt
```

### ❌ Permission denied sur les scripts

**Solution** :
```bash
# Rendre les scripts exécutables
chmod +x scripts/*.sh
```

---

## Comparaison Local vs CI

| Aspect | Local | CI (GitHub Actions) |
|--------|-------|---------------------|
| **Secrets** | `.env` | GitHub Secrets |
| **MuseScore** | Installation locale ou AppImage | Docker pré-configuré |
| **Speed** | Instant | ~30s setup |
| **Debugging** | Facile (logs directs) | Difficile (via logs GitHub) |
| **Usage** | Développement | Production |

---

## Workflow recommandé

1. **Développer en local** :
   ```bash
   # Tester rapidement
   ./scripts/process_musescore.sh test.mscz
   ```

2. **Vérifier avant commit** :
   ```bash
   # Test complet
   ./scripts/process_musescore.sh *.mscz && ./scripts/upload_to_drive.sh
   ```

3. **Commit et push** :
   ```bash
   git add *.mscz
   git commit -m "feat: ajout nouvelle partition"
   git push
   ```

4. **Vérifier la CI** : GitHub Actions exécute automatiquement les mêmes scripts

---

## Scripts disponibles

| Script | Description | Usage |
|--------|-------------|-------|
| `process_musescore.sh` | Conversion MSCZ → PDF/MP3 | `./scripts/process_musescore.sh *.mscz` |
| `upload_to_drive.sh` | Upload vers Drive | `./scripts/upload_to_drive.sh` |

Les deux scripts utilisent **exactement la même logique** en local et en CI !
