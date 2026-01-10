import os
import base64
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "service_account.json"


class DriveConnector:

    def __init__(self):
        base64_string = os.getenv("SERVICE_ACCOUNT")
        decoded_bytes = base64.b64decode(base64_string)
        json_str = decoded_bytes.decode("utf-8")
        service_account_info = json.loads(json_str)

        with open(SERVICE_ACCOUNT_FILE, "w") as f:
            json.dump(service_account_info, f, indent=4)

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )

        self.drive_service = build("drive", "v3", credentials=credentials)

    def create_folder(self, folder_name, parent_folder_id=None):
        """Create a folder in Google Drive and return its ID."""
        folder_metadata = {
            "name": f"{folder_name}",
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_folder_id] if parent_folder_id else [],
        }

        created_folder = (
            self.drive_service.files()
            .create(body=folder_metadata, fields="id")
            .execute()
        )

        print(f'Created Folder ID: {created_folder["id"]}')
        return created_folder["id"]

    def upload_file(self, file_path, parent_folder_id=None, replace=False):
        folders = self.list_folder(parent_folder_id)
        folder_name = os.path.basename(file_path).split(".")[0].split("-")[0]
        file_name = os.path.basename(file_path)
        file_metadata = {}
        for folder_file in folders:
            if folder_file["mimeType"] == "application/vnd.google-apps.folder":
                if folder_file["name"] == folder_name:
                    files_in_folder = self.list_folder(folder_file["id"])
                    for file_in_folder in files_in_folder:
                        if file_in_folder["name"] == file_name and replace:
                            self.delete_files(file_in_folder["id"])

                    file_metadata = {
                        "name": file_name,
                        "parents": [folder_file["id"]],
                    }
                    break

        if not file_metadata:
            print("No folder corresponding to partition, creating one...")
            new_folder_id = self.create_folder(folder_name, parent_folder_id)
            print(f"FILE PATH: {file_path}")
            file_metadata = {
                "name": file_name,
                "parents": [new_folder_id],
            }

        mime_type = "application/octet-stream"
        if file_path.endswith(".mscz"):
            mime_type = "application/x-musescore"  # Spécifier un type MIME pour les fichiers MuseScore, s'il en existe un
        media = MediaFileUpload(file_path, mimetype=mime_type)

        media = (
            self.drive_service.files()
            .create(body=file_metadata, media_body=media)
            .execute()
        )
        print(f"Uploaded {file_name} to {file_metadata['parents']}")

    def list_folder(self, parent_folder_id=None, delete=False):
        """List folders and files in Google Drive."""
        results = (
            self.drive_service.files()
            .list(
                q=(
                    f"'{parent_folder_id}' in parents and trashed=false"
                    if parent_folder_id
                    else None
                ),
                pageSize=1000,
                fields="nextPageToken, files(id, name, mimeType)",
            )
            .execute()
        )
        items = results.get("files", [])
        return items

    def delete_files(self, file_or_folder_id):
        """Delete a file or folder in Google Drive by ID."""
        try:
            self.drive_service.files().delete(fileId=file_or_folder_id).execute()
            print(f"Successfully deleted file/folder with ID: {file_or_folder_id}")
        except Exception as e:
            print(f"Error deleting file/folder with ID: {file_or_folder_id}")
            print(f"Error details: {str(e)}")

    def download_file(file_id, destination_path):
        """Download a file from Google Drive by its ID."""
        request = self.drive_service.files().get_media(fileId=file_id)
        fh = io.FileIO(destination_path, mode="wb")

        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
