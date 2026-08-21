import os
import logging

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


logger = logging.getLogger(__name__)


# =========================================================
# GOOGLE DRIVE FOLDER ID
# =========================================================

FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "1e8HPw_r_PPnEqjcgQbl3CaSebdLbENIz")


# =========================================================
# GOOGLE DRIVE SCOPES
# =========================================================

SCOPES = [
    "https://www.googleapis.com/auth/drive"
]


# =========================================================
# SERVICE ACCOUNT KEY FILE
# =========================================================
#
# Single source of truth:
#
#   1. GOOGLE_SERVICE_ACCOUNT_FILE env var (custom path)
#   2. /etc/secrets/key.json   -> Render Secret File
#   3. ./key.json              -> local development
#

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SERVICE_ACCOUNT_FILE_CANDIDATES = [
    os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE"),
    "/etc/secrets/key.json",
    os.path.join(BASE_DIR, "key.json"),
]

_drive_service = None


def get_drive_service():

    global _drive_service

    if _drive_service is not None:
        return _drive_service


    # =====================================================
    # LOCATE KEY FILE
    # =====================================================

    key_file = next(
        (
            path
            for path in SERVICE_ACCOUNT_FILE_CANDIDATES
            if path and os.path.exists(path)
        ),
        None
    )

    if key_file is None:

        checked = [
            path
            for path in SERVICE_ACCOUNT_FILE_CANDIDATES
            if path
        ]

        raise FileNotFoundError(
            f"Google Drive service account key not found. "
            f"Checked: {checked}. Add a Render Secret File named "
            f"'key.json' or set GOOGLE_SERVICE_ACCOUNT_FILE."
        )


    # =====================================================
    # LOAD SERVICE ACCOUNT CREDENTIALS
    # =====================================================

    try:

        creds = service_account.Credentials.from_service_account_file(
            key_file,
            scopes=SCOPES
        )

    except Exception as e:

        raise Exception(
            f"Unable to load service account key {key_file}: {e}"
        )


    logger.info("Drive auth: using service account key %s", key_file)


    # =====================================================
    # BUILD AND CACHE DRIVE SERVICE
    # =====================================================

    _drive_service = build(
        "drive",
        "v3",
        credentials=creds
    )

    return _drive_service


def reset_drive_service():
    """Clear cached service so next call re-authenticates."""

    global _drive_service

    _drive_service = None


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
