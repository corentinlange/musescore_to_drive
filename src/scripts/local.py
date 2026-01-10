import sys

from dotenv import load_dotenv

from config import DRIVE_FOLDERS_ID
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'drive-api'))
from connector import DriveConnector

load_dotenv()

if __name__ == "__main__":
    drive_connector = DriveConnector()
    drive_connector.upload_file(sys.argv[1], DRIVE_FOLDERS_ID["PARTOS"])
