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
# OAuth Client Secret JSON
# ==========================================
CLIENT_SECRET_FILE = "client_secret_646188540103-ukffg4im0q7pr68jh63n82h37a638o7c.apps.googleusercontent.com.json"

# ==========================================
# Google Drive Scope
# ==========================================
SCOPES = ["https://www.googleapis.com/auth/drive"]


def get_drive_service():

    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE,
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build(
        "drive",
        "v3",
        credentials=creds
    )

    return service


drive_service = get_drive_service()


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

    print("\n========== GOOGLE DRIVE ==========")
    print("Uploaded Successfully")
    print("File ID :", file_id)
    print("File Name :", file_name)
    print("=================================\n")

    view_link = f"https://drive.google.com/file/d/{file_id}/view"
    download_link = f"https://drive.google.com/uc?id={file_id}"

    return {
        "id": file_id,
        "view_link": view_link,
        "download_link": download_link
    }