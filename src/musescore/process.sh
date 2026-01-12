#!/bin/bash
set -e  # Exit on error

# Script de conversion MSCZ → PDF/MP3
# Usage: ./src/musescore/process.sh fichier1.mscz fichier2.mscz ...

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
    
    # Extraire le nom de base et le chemin relatif
    base_name=$(basename "$file" .mscz)
    
    # Détecter si le fichier est dans un sous-dossier
    file_dir=$(dirname "$file")
    
    # Si le fichier est dans un sous-dossier, préserver la structure
    if [[ "$file_dir" != "." ]]; then
        # Créer la structure output/chemin_relatif/nom_fichier/
        output_dir="$OUTPUT_DIR/${file_dir}/${base_name}"
    else
        # Fichier à la racine : output/nom_fichier/
        output_dir="$OUTPUT_DIR/${base_name}"
    fi
    
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
    
    
    # Generate individual parts MSCZ
    echo "🎼 Génération des parties individuelles..."
    if [ -f "src/musescore/decode_parts.py" ]; then
        python3 src/musescore/decode_parts.py "${base_name}-parts.json" "$output_dir"
    else
        echo "⚠️  decode_parts.py non trouvé, parties non générées"
    fi
    
    # Convert all part MSCZ files to PDF (but not the original yet)
    echo "📄 Conversion PDF..."
    for mscz_file in "$output_dir"/*.mscz; do
        if [ -f "$mscz_file" ]; then
            mscz_file_name=$(basename "$mscz_file" .mscz)
            "$MUSESCORE" -o "$output_dir/${mscz_file_name}.pdf" "$mscz_file"
            # Delete the part MSCZ file after PDF conversion
            rm "$mscz_file"
        fi
    done
    
    # Copy original MSCZ file AFTER cleaning up part files
    echo "📦 Copie du fichier MSCZ original..."
    cp "$file" "$output_dir/"
    
    # Clean up temporary JSON file
    rm -f "${base_name}-parts.json"
    
    echo "✅ Traité: $file"
    echo "   → Sortie: $output_dir"
    echo "   → Fichiers: $(ls -1 "$output_dir" | wc -l) fichiers générés"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Conversion terminée !"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
