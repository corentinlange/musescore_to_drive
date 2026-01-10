import sys

from config import DRIVE_FOLDERS_ID
from drive_connector import DriveConnector

if __name__ == "__main__":
    drive_connector = DriveConnector()
    drive_connector.upload_file(sys.argv[1], DRIVE_FOLDERS_ID["PARTOS"], replace=True)
