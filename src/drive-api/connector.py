import os
import base64
import json
import io

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

class DriveConnector:
    def __init__(self):
        # Récupération du token utilisateur depuis le secret GitHub
        # On s'attend à ce que le secret soit le contenu brut du fichier token.json
        token_data = os.getenv("GDRIVE_TOKEN")
        
        if not token_data:
            raise Exception("Erreur : Le secret GDRIVE_TOKEN est vide ou manquant.")

        # Chargement des informations du token
        try:
            # Si tu l'as encodé en base64 dans ton YAML (recommandé), on décode
            # Sinon, on charge le JSON directement
            try:
                decoded_token = base64.b64decode(token_data).decode("utf-8")
                token_info = json.loads(decoded_token)
            except:
                token_info = json.loads(token_data)
                
            credentials = Credentials.from_authorized_user_info(token_info, scopes=SCOPES)
        except Exception as e:
            raise Exception(f"Erreur lors du chargement du token : {str(e)}")

        # Construction du service (agira en ton nom)
        self.drive_service = build("drive", "v3", credentials=credentials)

    def create_folder(self, folder_name, parent_folder_id=None):
        """Create a folder in Google Drive and return its ID. Returns existing folder if found."""
        # Check if folder already exists
        existing_folders = self.list_folder(parent_folder_id)
        for folder in existing_folders:
            if folder.get("mimeType") == "application/vnd.google-apps.folder" and folder.get("name") == folder_name:
                # Folder already exists, return its ID
                return folder["id"]
        
        # Create new folder if not found
        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_folder_id] if parent_folder_id else [],
            "description": "Dossier créé par le Bot GitHub"
        }
        created_folder = self.drive_service.files().create(body=folder_metadata, fields="id").execute()
        return created_folder["id"]

    def upload_file(self, file_path, parent_folder_id=None, replace=False):
        """Upload a file directly to the specified parent folder."""
        file_name = os.path.basename(file_path)
        
        # Check if file already exists and delete if replace=True
        if replace and parent_folder_id:
            existing_files = self.list_folder(parent_folder_id)
            for existing_file in existing_files:
                if existing_file.get("name") == file_name and existing_file.get("mimeType") != "application/vnd.google-apps.folder":
                    self.delete_files(existing_file["id"])
        
        # Prepare file metadata
        file_metadata = {
            "name": file_name,
            "description": "Fichier uploadé par le Bot GitHub"
        }
        if parent_folder_id:
            file_metadata["parents"] = [parent_folder_id]

        # Determine MIME type
        mime_type = "application/octet-stream"
        if file_path.endswith(".mscz"):
            mime_type = "application/x-musescore"
        elif file_path.endswith(".pdf"):
            mime_type = "application/pdf"
        elif file_path.endswith(".mp3"):
            mime_type = "audio/mpeg"
            
        media = MediaFileUpload(file_path, mimetype=mime_type)
        uploaded_file = self.drive_service.files().create(
            body=file_metadata, 
            media_body=media,
            fields="id"
        ).execute()
        
        print(f"   ✅ Uploaded: {file_name}")

    def list_folder(self, parent_folder_id=None):
        query = f"'{parent_folder_id}' in parents and trashed=false" if parent_folder_id else None
        results = self.drive_service.files().list(
            q=query,
            pageSize=1000,
            fields="nextPageToken, files(id, name, mimeType)"
        ).execute()
        return results.get("files", [])

    def delete_files(self, file_or_folder_id):
        self.drive_service.files().delete(fileId=file_or_folder_id).execute()