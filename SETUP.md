# 🎼 MuseScore to Drive - Setup Guide

Ce guide explique comment **forker et configurer** ce projet pour votre propre utilisation.

---

## 🎯 Deux modes d'utilisation

### Mode 1 : **CI uniquement** (recommandé - 10 min) ✨
- ✅ Aucune installation locale nécessaire
- ✅ Tout se passe dans GitHub Actions
- → **Ajoutez vos .mscz, push, c'est tout !**

### Mode 2 : **Test local** (avancé - 30 min)
- Pour tester avant de push
- Nécessite Python + MuseScore en local
- → [Guide complet](src/docs/local-testing.md)

---

## 🚀 Setup Mode CI (10 minutes)

### 1️⃣ Forker le projet

1. Cliquez sur **"Fork"** en haut à droite de ce repo
2. GitHub va créer votre copie personnelle
3. Vous n'avez **pas besoin de cloner** le repo en local

### 2️⃣ Créer un Service Account Google

#### Étape A : Activer Google Drive API

1. Aller sur [Google Cloud Console](https://console.cloud.google.com)
2. **Créer un nouveau projet** (ex: "musescore-to-drive")
3. **APIs & Services** → **Library**
4. Rechercher **"Google Drive API"**
5. Cliquer **"Enable"**

#### Étape B : Créer le Service Account

1. **IAM & Admin** → **Service Accounts**
2. **Create Service Account**
   - Name: `musescore-uploader`
   - Description: "Uploads MuseScore files to Drive"
   - Role: (laisser vide)
3. Cliquer **"Done"**
4. Dans la liste, cliquer sur le service account créé
5. **Keys** → **Add Key** → **Create new key** → **JSON**
6. **Télécharger le fichier JSON** (ex: `service-account.json`)
   - ⚠️ **Ne jamais committer ce fichier !**

### 3️⃣ Créer un dossier Google Drive

1. Aller sur [Google Drive](https://drive.google.com)
2. **Créer un nouveau dossier** (ex: "Partitions MuseScore")
3. **Clic droit sur le dossier** → **Partager**
4. **Ajouter l'email du service account** :
   - Trouvé dans le JSON téléchargé → champ `client_email`
   - Exemple : `musescore-uploader@mon-projet.iam.gserviceaccount.com`
   - Rôle : **Éditeur**
   - Décocher "Notify people"
5. **Copier l'ID du dossier** depuis l'URL :
   ```
   https://drive.google.com/drive/folders/1AbC2DeF3GhI4JkL5MnO
                                          ^^^^^^^^^^^^^^^^^
                                          C'est l'ID du dossier
   ```

### 4️⃣ Encoder la clé en base64

Vous devez convertir le JSON en base64 pour les secrets GitHub.

#### Option A : En ligne (rapide)

1. Aller sur https://www.base64encode.org/
2. Coller **tout le contenu** du fichier `service-account.json`
3. Cliquer "Encode"
4. Copier le résultat (très longue chaîne)

#### Option B : Ligne de commande

**Git Bash (Windows) / Linux / macOS :**
```bash
cat service-account.json | base64 -w 0
```

**PowerShell (Windows) :**
```powershell
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((Get-Content service-account.json -Raw)))
```

### 5️⃣ Configurer les secrets GitHub

1. Votre fork → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** :
   - Name: `GCP_SERVICE_ACCOUNT_KEY_B64`
   - Value: [Coller le base64 de l'étape 4]
   - Cliquer "Add secret"

3. **New repository secret** :
   - Name: `DRIVE_FOLDER_ID`
   - Value: [ID du dossier Drive de l'étape 3]
   - Cliquer "Add secret"

### 6️⃣ (Optionnel mais recommandé) Builder l'image Docker

Pour des workflows plus rapides (~5s au lieu de ~70s) :

1. Votre fork → **Actions**
2. Si demandé, **Enable GitHub Actions**
3. Onglet **Actions** → **"Build and Push Docker Image"**
4. **Run workflow**
5. Attendre ~5 minutes (première fois)
6. Une fois terminé :
   - GitHub → **Packages** (en haut à droite de la page)
   - Cliquer sur `musescore-processor`
   - **Package settings** → **Change visibility** → **Public**

---

## ✅ Test : Ajouter votre première partition

### Via l'interface GitHub (sans git)

1. Votre fork → Cliquer **"Add file"** → **"Upload files"**
2. Glisser-déposer votre fichier `.mscz`
3. Commit message : "feat: add my first song"
4. Cliquer **"Commit changes"**
5. **Actions** → Le workflow "Update modified musescore on drive" démarre automatiquement
6. Attendre 1-2 minutes
7. **Vérifier sur Google Drive** → votre dossier contient :
   - Le fichier `.mscz` original
   - Le PDF
   - Le MP3
   - Les parties individuelles (si applicable)

### Via Git (si vous préférez)

```bash
# 1. Cloner votre fork
git clone https://github.com/VOTRE_USERNAME/musescore_to_drive.git
cd musescore_to_drive

# 2. Ajouter un fichier .mscz
# (créer avec MuseScore ou copier un fichier existant)

# 3. Commit et push
git add mon_morceau.mscz
git commit -m "feat: add my first song"
git push

# 4. Aller sur GitHub → Actions pour voir le workflow
```

---

## 🎯 Utilisation quotidienne

**C'est simple !**

1. **Ajouter/modifier un fichier `.mscz`** (via GitHub ou Git)
2. **Push sur la branche `main`**
3. **C'est tout !** GitHub Actions s'occupe du reste

Le workflow va automatiquement :
- ✅ Détecter les fichiers `.mscz` modifiés
- ✅ Les convertir en PDF et MP3
- ✅ Extraire les parties individuelles
- ✅ Tout uploader dans votre dossier Drive

---

## 🛠️ (Optionnel) Configuration avancée

### Changer le dossier Drive

Pour uploader dans un autre dossier :
1. Settings → Secrets → `DRIVE_FOLDER_ID`
2. Edit → Mettre le nouvel ID

### Rebuild l'image Docker

- Automatique : Chaque dimanche à minuit
- Manuel : Actions → "Build and Push Docker Image" → Run workflow

### Tester en local avant push

Si vous voulez tester les conversions en local avant de push, consultez le [guide de test local](src/docs/local-testing.md).

---

## 🆘 Dépannage

### Le workflow échoue avec "Permission denied"

**Solution** : Activer les permissions d'écriture pour GitHub Actions
1. Settings → Actions → General
2. Workflow permissions → **Read and write permissions**

### Rien n'apparaît sur Drive

**Vérifications** :
1. ✅ Le service account a-t-il accès au dossier Drive ?
   - Vérifier les partages du dossier
2. ✅ Le secret `DRIVE_FOLDER_ID` est-il correct ?
   - Comparer avec l'URL du dossier
3. ✅ Le secret `GCP_SERVICE_ACCOUNT_KEY_B64` est-il valide ?
   - Tester de le re-encoder

### Le workflow est lent (~70s de setup)

**Solution** : Builder l'image Docker (voir étape 6 ci-dessus)

### Erreur "Container image not found"

**Solutions** :
1. Builder l'image Docker (étape 6)
2. Ou modifier `.github/workflows/process_musescore.yml` :
   ```yaml
   # Commenter cette ligne :
   # container:
   #   image: ghcr.io/...
   ```

---

## 📚 Documentation complète

- [Architecture et fonctionnalités](README.md)
- [Test en local (avancé)](src/docs/local-testing.md)
- [Docker](src/docs/docker.md)

---

## 🤝 Support

**Problème ?**
1. Vérifier les [issues existantes](https://github.com/corentinlange/musescore_to_drive/issues)
2. Créer une nouvelle issue avec :
   - Description du problème
   - Copie des logs GitHub Actions
   - Capture d'écran si pertinent

---

## 📝 Astuce pro

**Workflow optimal** :
1. Composez dans MuseScore
2. Sauvegardez le `.mscz` dans votre repo local
3. `git add *.mscz && git commit -m "update scores" && git push`
4. 2 minutes plus tard → tout est sur Drive, prêt à partager ! 🎉
