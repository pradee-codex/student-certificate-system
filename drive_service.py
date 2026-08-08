import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# ==========================================
# Google Drive Folder ID
# ==========================================

FOLDER_ID = "1e8HPw_r_PPnEqjcgQbl3CaSebdLbENIz"


# ==========================================
# OAuth Client Secret
# ==========================================

CLIENT_SECRET_FILE = "credentials.json"


# ==========================================
# Google Drive Scope
# ==========================================

SCOPES = [
    "https://www.googleapis.com/auth/drive"
]


# ==========================================
# Create Google Drive Service
# ==========================================

def get_drive_service():

    creds = None

    # Load saved token
    if os.path.exists("token.pickle"):

        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # Check credentials
    if not creds or not creds.valid:

        # Refresh expired credentials
        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE,
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        # Save credentials
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    # Create Drive service
    service = build(
        "drive",
        "v3",
        credentials=creds
    )

    return service


# ==========================================
# Google Drive Service
# ==========================================

drive_service = get_drive_service()


# ==========================================
# Upload File To Google Drive
# ==========================================

def upload_to_drive(file_path, file_name):

    file_metadata = {
        "name": file_name,
        "parents": [FOLDER_ID]
    }

    media = MediaFileUpload(
        file_path,
        resumable=True
    )

    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    file_id = uploaded_file["id"]

    print("\n========================================")
    print("      GOOGLE DRIVE UPLOAD SUCCESS")
    print("========================================")
    print("File Name :", file_name)
    print("File ID   :", file_id)
    print("========================================\n")

    view_link = f"https://drive.google.com/file/d/{file_id}/view"

    download_link = (
        f"https://drive.google.com/uc?id={file_id}&export=download"
    )

    return {
        "id": file_id,
        "view_link": view_link,
        "download_link": download_link
    }