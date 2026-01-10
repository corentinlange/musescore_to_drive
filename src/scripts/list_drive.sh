#!/bin/bash
# Script wrapper pour lister l'arborescence Google Drive
# Usage: ./src/scripts/list_drive.sh [folder_id] [--name "Nom du dossier"]

set -e

# Debug mode si --debug
DEBUG=false
if [[ "$*" == *"--debug"* ]]; then
    DEBUG=true
fi

$DEBUG && echo "🔍 Debug: Chargement de .env..."

# Charger .env si présent
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    $DEBUG && echo "✅ .env chargé"
else
    $DEBUG && echo "⚠️  .env non trouvé"
fi

$DEBUG && echo "🔍 Debug: Vérification des variables d'environnement..."

# Vérifier que la clé existe
if [ -z "$GCP_SERVICE_ACCOUNT_KEY_B64" ]; then
    echo "❌ Erreur: GCP_SERVICE_ACCOUNT_KEY_B64 non défini"
    echo ""
    echo "Solutions:"
    echo "  1. Vérifier que .env existe: ls -la .env"
    echo "  2. Vérifier le contenu: cat .env"
    echo "  3. La variable doit commencer par: GCP_SERVICE_ACCOUNT_KEY_B64='...'"
    exit 1
fi

$DEBUG && echo "✅ GCP_SERVICE_ACCOUNT_KEY_B64 trouvé (${#GCP_SERVICE_ACCOUNT_KEY_B64} caractères)"

# Décoder base64 (compatible Linux et Git Bash Windows)
$DEBUG && echo "🔍 Debug: Décodage base64..."
if command -v base64 &> /dev/null; then
    # Linux/macOS/Git Bash
    export SERVICE_ACCOUNT=$(echo "$GCP_SERVICE_ACCOUNT_KEY_B64" | base64 -d 2>/dev/null || echo "$GCP_SERVICE_ACCOUNT_KEY_B64" | base64 --decode)
else
    # Fallback PowerShell (si appelé depuis PowerShell)
    export SERVICE_ACCOUNT=$(powershell -Command "[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('$GCP_SERVICE_ACCOUNT_KEY_B64'))")
fi

$DEBUG && echo "✅ Base64 décodé (${#SERVICE_ACCOUNT} caractères)"
$DEBUG && echo ""

# Exécuter le script Python
$DEBUG && echo "🚀 Lancement du script Python..."
python src/tools/list_drive_tree.py "$@"
