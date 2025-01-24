import sys

from dotenv import load_dotenv

from config import DRIVE_FOLDER_ID
from drive_connector import DriveConnector

load_dotenv()

if __name__ == "__main__":
    drive_connector = DriveConnector()
    drive_connector.upload_file(sys.argv[1], DRIVE_FOLDER_ID["PARTOS"])
