#!/usr/bin/env python3
"""
Upload fichiers vers Google Drive en respectant l'arborescence
Usage: python src/drive-api/upload_all.py [output_directory]
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Add drive-api to path
sys.path.insert(0, os.path.dirname(__file__))
from connector import DriveConnector


def upload_directory_structure(output_dir, root_folder_id):
    """
    Upload tous les fichiers depuis output/ en respectant l'arborescence
    
    Args:
        output_dir: Répertoire output/ à uploader
        root_folder_id: ID du dossier Drive racine
    """
    drive = DriveConnector()
    stats = {"uploaded": 0, "skipped": 0}
    
    # Parcourir récursivement output/
    for root, dirs, files in os.walk(output_dir):
        # Calculer le chemin relatif depuis output/
        rel_path = os.path.relpath(root, output_dir)
        
        if rel_path == ".":
            # Racine d'output
            current_folder_id = root_folder_id
        else:
            # Créer la structure de dossiers sur Drive
            path_parts = Path(rel_path).parts
            current_folder_id = root_folder_id
            
            for part in path_parts:
                # Créer ou récupérer le sous-dossier
                current_folder_id = drive.create_folder(part, current_folder_id)
        
        # Upload tous les fichiers du dossier courant
        for file in files:
            file_path = os.path.join(root, file)
            print(f"📤 Upload: {os.path.relpath(file_path, output_dir)}")
            
            try:
                drive.upload_file(file_path, current_folder_id, replace=True)
                stats["uploaded"] += 1
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
                stats["skipped"] += 1
    
    return stats


def main():
    # Vérifier DRIVE_FOLDER_ID
    root_folder_id = os.getenv("DRIVE_FOLDER_ID")
    if not root_folder_id:
        print("❌ Erreur: DRIVE_FOLDER_ID non défini dans .env")
        print("\nAjouter dans .env:")
        print("  DRIVE_FOLDER_ID='votre_folder_id'")
        sys.exit(1)
    
    # Déterminer le dossier output
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    
    if not os.path.isdir(output_dir):
        print(f"❌ Erreur: Dossier {output_dir} non trouvé")
        sys.exit(1)
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("☁️  Upload vers Google Drive")
    print(f"📁 Dossier: {output_dir}")
    print(f"🎯 Drive Root: {root_folder_id}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    # Upload
    stats = upload_directory_structure(output_dir, root_folder_id)
    
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ Upload terminé!")
    print(f"   📤 Fichiers uploadés: {stats['uploaded']}")
    if stats['skipped'] > 0:
        print(f"   ⚠️  Fichiers ignorés: {stats['skipped']}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


if __name__ == "__main__":
    main()
