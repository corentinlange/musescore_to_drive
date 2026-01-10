#!/bin/bash
set -e  # Exit on error

# Script de conversion MSCZ → PDF/MP3
# Usage: ./scripts/process_musescore.sh fichier1.mscz fichier2.mscz ...

# Configuration
OUTPUT_DIR="output"
QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-offscreen}"
export QT_QPA_PLATFORM

# Détecter MuseScore
if [ -f "/opt/musescore/AppRun" ]; then
    # CI/Docker environment
    MUSESCORE="/opt/musescore/AppRun"
    echo "✓ MuseScore détecté (Docker): $MUSESCORE"
elif command -v mscore &> /dev/null; then
    # Local installation (Linux/macOS)
    MUSESCORE="mscore"
    echo "✓ MuseScore détecté (local): $(which mscore)"
elif command -v musescore &> /dev/null; then
    # Alternative command name
    MUSESCORE="musescore"
    echo "✓ MuseScore détecté (local): $(which musescore)"
elif [ -f "./squashfs-root/AppRun" ]; then
    # Extracted AppImage in current directory
    MUSESCORE="./squashfs-root/AppRun"
    echo "✓ MuseScore détecté (AppImage extrait): $MUSESCORE"
else
    echo "❌ Erreur: MuseScore non trouvé"
    echo "Solutions:"
    echo "  - Installer MuseScore localement"
    echo "  - Extraire l'AppImage: ./MuseScore-*.AppImage --appimage-extract"
    echo "  - Utiliser Docker: docker run -v \$(pwd):/workspace musescore-processor"
    exit 1
fi

# Vérifier qu'il y a des fichiers à traiter
if [ $# -eq 0 ]; then
    echo "❌ Erreur: Aucun fichier spécifié"
    echo "Usage: $0 fichier1.mscz fichier2.mscz ..."
    exit 1
fi

# Créer le dossier de sortie
mkdir -p "$OUTPUT_DIR"

# Traiter chaque fichier
for file in "$@"; do
    if [[ ! "$file" == *.mscz ]]; then
        echo "⚠️  Ignoré (non .mscz): $file"
        continue
    fi
    
    if [[ ! -f "$file" ]]; then
        echo "⚠️  Fichier introuvable: $file"
        continue
    fi
    
    base_name=$(basename "$file" .mscz)
    output_dir="$OUTPUT_DIR/${base_name}"
    mkdir -p "$output_dir"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📄 Processing: $file"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Générer MP3
    echo "🎵 Génération MP3..."
    "$MUSESCORE" -o "$output_dir/${base_name}.mp3" "$file"
    
    # Générer parties (JSON)
    echo "📋 Extract parts..."
    "$MUSESCORE" "$file" --score-parts > "${base_name}-parts.json"
    
    # Générer MSCZ des parties
    echo "🎼 Génération des parties individuelles..."
    if [ -f "src/tools/decode_json_parts.py" ]; then
        python3 src/tools/decode_json_parts.py "${base_name}-parts.json" "$output_dir"
    else
        echo "⚠️  decode_json_parts.py non trouvé, parties non générées"
    fi
    
    # Copier le fichier original
    cp "$file" "$output_dir"
    
    # Convertir toutes les parties MSCZ en PDF
    echo "📄 Conversion PDF..."
    for mscz_file in "$output_dir"/*.mscz; do
        if [ -f "$mscz_file" ]; then
            mscz_file_name=$(basename "$mscz_file" .mscz)
            "$MUSESCORE" -o "$output_dir/${mscz_file_name}.pdf" "$mscz_file"
            rm "$mscz_file"
        fi
    done
    
    # Nettoyer le fichier JSON temporaire
    rm -f "${base_name}-parts.json"
    
    echo "✅ Traité: $file"
    echo "   → Sortie: $output_dir"
    echo "   → Fichiers: $(ls -1 "$output_dir" | wc -l) fichiers générés"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Conversion terminée !"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
