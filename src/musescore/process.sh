#!/bin/bash
set -e  # Quitte le script en cas d'erreur

# --- CONFIGURATION ---
OUTPUT_DIR="output"
export QT_QPA_PLATFORM="offscreen"

# --- DÉTECTION DE MUSESCORE ---
if [ -f "/opt/musescore/AppRun" ]; then
    MUSESCORE="/opt/musescore/AppRun"
    echo "✓ MuseScore détecté (Docker): $MUSESCORE"
elif command -v mscore &> /dev/null; then
    MUSESCORE="mscore"
    echo "✓ MuseScore détecté (local): $(which mscore)"
elif command -v musescore &> /dev/null; then
    MUSESCORE="musescore"
    echo "✓ MuseScore détecté (local): $(which musescore)"
elif [ -f "./squashfs-root/AppRun" ]; then
    MUSESCORE="./squashfs-root/AppRun"
    echo "✓ MuseScore détecté (AppImage extrait): $MUSESCORE"
else
    echo "❌ Erreur: MuseScore non trouvé"
    exit 1
fi

# --- CONFIGURATION QT POUR MODE HEADLESS ---
# Force Qt to use offscreen platform (no display needed)
export QT_QPA_PLATFORM="offscreen"
export QT_LOGGING_RULES="*.debug=false;qt.qpa.*=false"
export QT_QPA_PLATFORMTHEME=""
export QML_DISABLE_DISK_CACHE=1
export QTWEBENGINE_DISABLE_SANDBOX=1

echo "✓ Qt configured for headless mode (offscreen)"

# --- VÉRIFICATION DES ARGUMENTS ---
if [ $# -eq 0 ]; then
    echo "❌ Erreur: Aucun fichier spécifié"
    echo "Usage: $0 fichier1.mscz fichier2.mscz ..."
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# --- TRAITEMENT DES FICHIERS ---
for file in "$@"; do
    if [[ ! "$file" == *.mscz ]] || [[ ! -f "$file" ]]; then
        echo "⚠️  Ignoré ou introuvable: $file"
        continue
    fi
    
    # Préparation des noms et dossiers
    base_name=$(basename "$file" .mscz)
    file_dir=$(dirname "$file")
    
    if [[ "$file_dir" != "." ]]; then
        output_dir="$OUTPUT_DIR/${file_dir}/${base_name}"
    else
        output_dir="$OUTPUT_DIR/${base_name}"
    fi
    
    mkdir -p "$output_dir"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📄 Processing: $file"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # 1. Génération des formats audio et données
    echo "🎵 Génération MP3..."
    "$MUSESCORE" -f -o "$output_dir/${base_name}.mp3" "$file"
    
    echo "🎹 Génération MIDI..."
    "$MUSESCORE" -f -o "$output_dir/${base_name}.mid" "$file"
    
    echo "📝 Génération MusicXML..."
    "$MUSESCORE" -f -o "$output_dir/${base_name}.musicxml" "$file"
    
    # 2. Extraction des parties (JSON)
    echo "📋 Extraction des parties..."
    "$MUSESCORE" -f "$file" --score-parts > "${base_name}-parts.json"
    
    # 3. Décodage des parties via Python
    echo "🎼 Génération des fichiers de parties individuelles..."
    if [ -f "src/musescore/decode_parts.py" ]; then
        python3 src/musescore/decode_parts.py "${base_name}-parts.json" "$output_dir"
    else
        echo "⚠️  decode_parts.py non trouvé, saut de l'étape."
    fi
    
    # 4. Conversion des parties MSCZ en PDF
    echo "📄 Conversion PDF des parties..."
    for mscz_part in "$output_dir"/*.mscz; do
        if [ -f "$mscz_part" ]; then
            part_name=$(basename "$mscz_part" .mscz)
            "$MUSESCORE" -f -o "$output_dir/${part_name}.pdf" "$mscz_part"
            rm "$mscz_part"  # Nettoyage
        fi
    done
    
    # 5. Finalisation
    echo "📦 Copie du fichier MSCZ original..."
    cp "$file" "$output_dir/"
    
    rm -f "${base_name}-parts.json"
    
    echo "✅ Terminé: $base_name"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Tous les fichiers ont été traités !"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"