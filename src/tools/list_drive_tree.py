#!/usr/bin/env python3
"""
Script pour afficher l'arborescence d'un dossier Google Drive.
Usage: python src/tools/list_drive_tree.py [folder_id]
"""

import os
import sys
import base64
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account


def get_service_account():
    """Récupère les credentials du service account depuis l'environnement."""
    # Debug
    debug = '--debug' in sys.argv
    
    # Essayer SERVICE_ACCOUNT (déjà décodé par le script bash)
    json_str = os.getenv('SERVICE_ACCOUNT')
    if json_str:
        if debug:
            print(f"🔍 Debug: SERVICE_ACCOUNT trouvé ({len(json_str)} caractères)")
        try:
            creds = json.loads(json_str)
            if debug:
                print(f"✅ Debug: JSON parsé avec succès")
                print(f"   - Type: {creds.get('type')}")
                print(f"   - Project: {creds.get('project_id')}")
                print(f"   - Email: {creds.get('client_email')}")
            return creds
        except Exception as e:
            print(f"❌ Erreur parsing SERVICE_ACCOUNT JSON: {e}")
            if debug:
                print(f"   Contenu: {json_str[:100]}...")
            sys.exit(1)
    
    # Fallback: GCP_SERVICE_ACCOUNT_KEY_B64 (base64)
    b64_key = os.getenv('GCP_SERVICE_ACCOUNT_KEY_B64')
    if b64_key:
        if debug:
            print(f"🔍 Debug: GCP_SERVICE_ACCOUNT_KEY_B64 trouvé ({len(b64_key)} caractères)")
        try:
            json_str = base64.b64decode(b64_key).decode('utf-8')
            creds = json.loads(json_str)
            if debug:
                print(f"✅ Debug: Base64 décodé et JSON parsé")
            return creds
        except Exception as e:
            print(f"❌ Erreur décodage base64: {e}")
            if debug:
                print(f"   Contenu base64: {b64_key[:50]}...")
            sys.exit(1)
    
    print("❌ Erreur: GCP_SERVICE_ACCOUNT_KEY_B64 ou SERVICE_ACCOUNT non défini")
    print("\nConfigurer dans .env:")
    print("  GCP_SERVICE_ACCOUNT_KEY_B64='<votre_json_base64>'")
    print("\nPour débugger:")
    print("  ./src/scripts/list_drive.sh --debug")
    sys.exit(1)


def build_drive_service():
    """Crée un service Google Drive authentifié."""
    creds_info = get_service_account()
    credentials = service_account.Credentials.from_service_account_info(
        creds_info, scopes=['https://www.googleapis.com/auth/drive']
    )
    return build('drive', 'v3', credentials=credentials)


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
    service = build_drive_service()
    
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print_tree(service, args.folder_id, '', True, args.name)
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("\n✅ Arborescence affichée avec succès !")


if __name__ == '__main__':
    main()
