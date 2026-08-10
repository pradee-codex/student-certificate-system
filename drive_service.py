import os
import json

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# =========================================================
# GOOGLE DRIVE FOLDER ID
# =========================================================

FOLDER_ID = "1e8HPw_r_PPnEqjcgQbl3CaSebdLbENIz"


# =========================================================
# GOOGLE DRIVE SCOPES
# =========================================================

SCOPES = [
    "https://www.googleapis.com/auth/drive"
]


# =========================================================
# TOKEN FILE
# =========================================================
#
# Render:
# /etc/secrets/token.json
#
# Local:
# token.json
#

TOKEN_FILE = os.getenv(
    "GOOGLE_TOKEN_FILE",
    "/etc/secrets/token.json"
)


# =========================================================
# GET GOOGLE DRIVE SERVICE
# =========================================================

def get_drive_service():

    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError(
            f"Google Drive token file not found: {TOKEN_FILE}"
        )

    try:

        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    except Exception as e:

        raise Exception(
            f"Unable to load Google Drive token: {e}"
        )


    # =====================================================
    # REFRESH TOKEN IF EXPIRED
    # =====================================================

    if creds.expired and creds.refresh_token:

        try:
            creds.refresh(Request())

        except Exception as e:

            raise Exception(
                f"Google Drive token refresh failed: {e}"
            )


    # =====================================================
    # CHECK CREDENTIALS
    # =====================================================

    if not creds.valid:

        raise Exception(
            "Google Drive credentials are invalid or expired."
        )


    # =====================================================
    # BUILD DRIVE SERVICE
    # =====================================================

    service = build(
        "drive",
        "v3",
        credentials=creds
    )

    return service


# =========================================================
# UPLOAD FILE TO GOOGLE DRIVE
# =========================================================

def upload_to_drive(file_path, file_name=None):

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"File not found: {file_path}"
        )


    # Use original filename if not provided
    if file_name is None:
        file_name = os.path.basename(file_path)


    # =====================================================
    # GET DRIVE SERVICE
    # =====================================================

    service = get_drive_service()


    # =====================================================
    # FILE METADATA
    # =====================================================

    file_metadata = {
        "name": file_name,
        "parents": [FOLDER_ID]
    }


    # =====================================================
    # FILE UPLOAD
    # =====================================================

    media = MediaFileUpload(
        file_path,
        resumable=True
    )


    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id,name,webViewLink"
    ).execute()


    # =====================================================
    # RETURN INFORMATION
    # =====================================================

    return {
        "id": uploaded_file.get("id"),
        "name": uploaded_file.get("name"),
        "url": uploaded_file.get("webViewLink")
    }