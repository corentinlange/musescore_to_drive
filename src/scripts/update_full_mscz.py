import sys

from config import DRIVE_FOLDER_ID
from drive_connector import DriveConnector

if __name__ == "__main__":
    drive_connector = DriveConnector()

		file_path = sys.argv[1]
		folder_name = sys.argv[2]

    drive_connector.upload_file(sys.argv[1], DRIVE_FOLDER_ID["GITHUB"], replace=True)