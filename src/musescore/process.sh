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

# --- GESTION DU WRAPPER GRAPHIQUE (XVFB) ---
# Nécessaire pour éviter l'Exit Code 40 sur serveur
RUNNER=""
if command -v xvfb-run &> /dev/null; then
    RUNNER="xvfb-run --auto-servernum"
    echo "✓ Serveur graphique virtuel (xvfb) prêt."
else
    echo "⚠️  xvfb-run non trouvé, exécution directe (peut échouer sur serveur sans écran)."
fi

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
    $RUNNER "$MUSESCORE" -o "$output_dir/${base_name}.mp3" "$file"
    
    echo "🎹 Génération MIDI..."
    $RUNNER "$MUSESCORE" -o "$output_dir/${base_name}.mid" "$file"
    
    echo "📝 Génération MusicXML..."
    $RUNNER "$MUSESCORE" -o "$output_dir/${base_name}.musicxml" "$file"
    
    # 2. Extraction des parties (JSON)
    echo "📋 Extraction des parties..."
    $RUNNER "$MUSESCORE" "$file" --score-parts > "${base_name}-parts.json"
    
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
            $RUNNER "$MUSESCORE" -o "$output_dir/${part_name}.pdf" "$mscz_part"
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