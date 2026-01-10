#!/usr/bin/env python3
"""
Script pour afficher l'arborescence d'un dossier Google Drive.
Usage: python src/drive-api/list_tree.py [folder_id]
"""

import os
import sys

# Add drive-api to path
sys.path.insert(0, os.path.dirname(__file__))
from connector import DriveConnector


def list_folder_contents(service, folder_id='root'):
    """Liste le contenu d'un dossier Drive."""
    try:
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(
            q=query,
            pageSize=1000,
            fields="files(id, name, mimeType, parents)",
            orderBy="folder,name"
        ).execute()
        return results.get('files', [])
    except Exception as e:
        print(f"❌ Erreur lors de la récupération: {e}")
        return []


def print_tree(service, folder_id='root', prefix='', is_last=True, current_name='Drive'):
    """Affiche l'arborescence récursive d'un dossier."""
    # Symboles pour l'arborescence
    connector = '└── ' if is_last else '├── '
    
    # Afficher le dossier actuel
    if prefix == '':  # Racine
        print(f"📁 {current_name}")
    else:
        print(f"{prefix}{connector}{current_name}")
    
    # Récupérer les enfants
    items = list_folder_contents(service, folder_id)
    
    # Séparer dossiers et fichiers
    folders = [item for item in items if item['mimeType'] == 'application/vnd.google-apps.folder']
    files = [item for item in items if item['mimeType'] != 'application/vnd.google-apps.folder']
    
    # Nouvelle indentation
    new_prefix = prefix + ('    ' if is_last else '│   ')
    
    # Afficher les dossiers d'abord
    total_items = folders + files
    for i, item in enumerate(total_items):
        is_last_item = (i == len(total_items) - 1)
        
        if item in folders:
            # Récursion pour les sous-dossiers
            print_tree(service, item['id'], new_prefix, is_last_item, f"📁 {item['name']}")
        else:
            # Afficher les fichiers
            connector_file = '└── ' if is_last_item else '├── '
            icon = get_file_icon(item['name'], item['mimeType'])
            print(f"{new_prefix}{connector_file}{icon} {item['name']}")


def get_file_icon(name, mime_type):
    """Retourne une icône basée sur l'extension ou le type MIME."""
    ext = name.split('.')[-1].lower() if '.' in name else ''
    
    icons = {
        'pdf': '📄',
        'mp3': '🎵',
        'mscz': '🎼',
        'zip': '📦',
        'jpg': '🖼️',
        'jpeg': '🖼️',
        'png': '🖼️',
        'txt': '📝',
        'md': '📝',
    }
    
    # Google Apps types
    if 'google-apps.document' in mime_type:
        return '📝'
    elif 'google-apps.spreadsheet' in mime_type:
        return '📊'
    elif 'google-apps.presentation' in mime_type:
        return '📽️'
    
    return icons.get(ext, '📄')


def main():
    """Point d'entrée principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Affiche l\'arborescence d\'un dossier Google Drive'
    )
    parser.add_argument(
        'folder_id',
        nargs='?',
        default='root',
        help='ID du dossier Drive (défaut: root)'
    )
    parser.add_argument(
        '--name',
        default='My Drive',
        help='Nom à afficher pour la racine'
    )
    
    args = parser.parse_args()
    
    print("🔍 Connexion à Google Drive...")
    
    # Use DriveConnector for authentication
    drive_connector = DriveConnector()
    service = drive_connector.drive_service
    
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print_tree(service, args.folder_id, '', True, args.name)
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("\n✅ Arborescence affichée avec succès !")


if __name__ == '__main__':
    main()
