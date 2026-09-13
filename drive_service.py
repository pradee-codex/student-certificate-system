import os

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

TOKEN_FILE = os.getenv(
    "GOOGLE_TOKEN_FILE",
    "token.json"
)


# =========================================================
# COLLEGE DOMAIN
# =========================================================

COLLEGE_DOMAIN = "sritcbe.ac.in"


# =========================================================
# GET GOOGLE DRIVE SERVICE
# =========================================================

def get_drive_service():

    # -----------------------------------------------------
    # CHECK TOKEN FILE
    # -----------------------------------------------------

    if not os.path.exists(TOKEN_FILE):

        raise FileNotFoundError(
            f"""
Google Drive token file not found.

Expected location:
{TOKEN_FILE}

Local:
Create token.json by running:
py create_token.py

Render:
Add token.json as a Secret File at:
/etc/secrets/token.json
"""
        )

    # -----------------------------------------------------
    # LOAD CREDENTIALS
    # -----------------------------------------------------

    try:

        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    except Exception as e:

        raise Exception(
            f"Unable to load Google Drive credentials: {e}"
        )

    # -----------------------------------------------------
    # REFRESH TOKEN IF EXPIRED
    # -----------------------------------------------------

    if creds.expired:

        if creds.refresh_token:

            try:

                creds.refresh(Request())

            except Exception as e:

                raise Exception(
                    f"Google Drive token refresh failed: {e}"
                )

        else:

            raise Exception(
                """
Google Drive token has expired and no refresh token
is available.

Run:

py create_token.py

again and authorize Google Drive.
"""
            )

    # -----------------------------------------------------
    # CHECK CREDENTIALS
    # -----------------------------------------------------

    if not creds.valid:

        raise Exception(
            "Google Drive credentials are invalid."
        )

    # -----------------------------------------------------
    # BUILD GOOGLE DRIVE SERVICE
    # -----------------------------------------------------

    try:

        service = build(
            "drive",
            "v3",
            credentials=creds
        )

    except Exception as e:

        raise Exception(
            f"Unable to connect to Google Drive: {e}"
        )

    return service


# =========================================================
# UPLOAD FILE TO GOOGLE DRIVE
# =========================================================

def upload_to_drive(file_path, file_name=None):

    # -----------------------------------------------------
    # CHECK LOCAL FILE
    # -----------------------------------------------------

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    # -----------------------------------------------------
    # FILE NAME
    # -----------------------------------------------------

    if file_name is None:

        file_name = os.path.basename(file_path)

    # -----------------------------------------------------
    # GET GOOGLE DRIVE SERVICE
    # -----------------------------------------------------

    service = get_drive_service()

    # -----------------------------------------------------
    # GOOGLE DRIVE FILE METADATA
    # -----------------------------------------------------

    file_metadata = {
        "name": file_name,
        "parents": [FOLDER_ID]
    }

    # -----------------------------------------------------
    # MEDIA FILE
    # -----------------------------------------------------

    media = MediaFileUpload(
        file_path,
        resumable=True
    )

    # -----------------------------------------------------
    # UPLOAD FILE
    # -----------------------------------------------------

    try:

        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id,name,webViewLink"
        ).execute()

    except Exception as e:

        raise Exception(
            f"Google Drive upload failed: {e}"
        )

    # -----------------------------------------------------
    # GET FILE ID
    # -----------------------------------------------------

    file_id = uploaded_file.get("id")

    if not file_id:

        raise Exception(
            "Google Drive uploaded file ID not found."
        )

    # =====================================================
    # GIVE COLLEGE DOMAIN VIEW ACCESS
    # =====================================================

    try:

        permission = {
            "type": "domain",
            "role": "reader",
            "domain": COLLEGE_DOMAIN
        }

        service.permissions().create(
            fileId=file_id,
            body=permission,
            fields="id"
        ).execute()

        print(
            f"College domain access granted: {COLLEGE_DOMAIN}"
        )

    except Exception as e:

        raise Exception(
            f"Unable to give college domain access: {e}"
        )

    # -----------------------------------------------------
    # GET WEB VIEW LINK
    # -----------------------------------------------------

    file_url = uploaded_file.get("webViewLink")

    if not file_url:

        file_url = (
            f"https://drive.google.com/file/d/{file_id}/view"
        )

    # -----------------------------------------------------
    # LOG SUCCESS
    # -----------------------------------------------------

    print(
        f"Certificate uploaded to Google Drive successfully: "
        f"{file_name}"
    )

    print(
        f"Google Drive File ID: {file_id}"
    )

    print(
        f"Google Drive URL: {file_url}"
    )

    # -----------------------------------------------------
    # RETURN FILE INFORMATION
    # -----------------------------------------------------

    return {
        "id": file_id,
        "name": uploaded_file.get("name"),
        "url": file_url
    }