#!/bin/bash
set -e  # Exit on error

# Script d'Upload to Google Drive
# Usage: ./scripts/upload_to_drive.sh

# Configuration
OUTPUT_DIR="output"

# Charger .env si présent (mode local)
if [ -f ".env" ]; then
    echo "📋 Loading .env..."
    export $(grep -v '^#' .env | xargs)
fi

# Vérifier que GCP_SERVICE_ACCOUNT_KEY_B64 est défini
if [ -z "$GCP_SERVICE_ACCOUNT_KEY_B64" ]; then
    echo "❌ Error: GCP_SERVICE_ACCOUNT_KEY_B64 non défini"
    echo ""
    echo "Solutions:"
    echo "  1. Mode local: Créer un fichier .env avec:"
    echo "     GCP_SERVICE_ACCOUNT_KEY_B64='<votre_json_encodé_en_base64>'"
    echo ""
    echo "  2. Mode CI: Définir le secret GitHub GCP_SERVICE_ACCOUNT_KEY_B64"
    echo ""
    echo "  3. Définir manuellement:"
    echo "     export GCP_SERVICE_ACCOUNT_KEY_B64='<base64>'"
    echo ""
    echo "  Pour encoder votre JSON en base64:"
    echo "     cat service-account.json | base64 -w 0"
    exit 1
fi

# Décoder le base64 et exporter comme SERVICE_ACCOUNT pour les scripts Python
export SERVICE_ACCOUNT=$(echo "$GCP_SERVICE_ACCOUNT_KEY_B64" | base64 -d)

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "☁️  Upload to Google Drive"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Vérifier que le script d'upload existe
if [ ! -f "src/tools/upload_to_drive.py" ]; then
    echo "❌ Error: src/tools/upload_to_drive.py non trouvé"
    exit 1
fi

# Compter le nombre de fichiers traités
total_uploaded=0

# Traiter tous les fichiers MSCZ
for mscz_file in *.mscz; do
    if [ ! -f "$mscz_file" ]; then
        echo "⚠️  Aucun fichier .mscz trouvé dans le répertoire courant"
        break
    fi
    
    base_name=$(basename "$mscz_file" .mscz)
    output_dir="$OUTPUT_DIR/${base_name}"
    
    if [ ! -d "$output_dir" ] || [ -z "$(ls -A "$output_dir" 2>/dev/null)" ]; then
        echo "⚠️  Empty or missing folder: $output_dir"
        continue
    fi
    
    echo ""
    echo "📤 Upload: $base_name"
    
    # Upload le fichier MSCZ original
    echo "   → $mscz_file"
    python3 src/tools/upload_to_drive.py "$mscz_file" "$base_name"
    ((total_uploaded++))
    
    # Upload tous les fichiers générés
    for output_file in "$output_dir"/*; do
        if [ -f "$output_file" ]; then
            echo "   → $(basename "$output_file")"
            python3 src/tools/upload_to_drive.py "$output_file" "$base_name"
            ((total_uploaded++))
        fi
    done
    
    echo "✅ Upload terminé: $base_name"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Upload terminé ! ($total_uploaded fichiers uploadés)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
