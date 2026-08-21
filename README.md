# Student Certificate System

A Flask web application for managing student certificates with roles for
Admin, HOD, Tutor, and Student. Certificates are uploaded to Google Drive.

---

## 1. Prerequisites

- Python 3.11+
- MySQL 8+ running locally (for local development)
- A Google Cloud project

---

## 2. Google Cloud Setup (one time)

### 2.1 Enable the Google Drive API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Select (or create) your project
3. Navigate to **APIs & Services → Library**
4. Search for **Google Drive API** → click **Enable**

### 2.2 Create a Service Account and Key

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → Service account**
3. Give it a name (e.g. `certificate-uploader`) → **Create and Continue**
   (skip the optional role/user steps) → **Done**
4. Open the newly created service account → **Keys** tab
5. Click **Add Key → Create new key**
6. Choose **JSON** → **Create**

A `key.json` file downloads automatically. This is the only credential
file the application needs.

> Keep this file secret. Never commit it to git (it is already in `.gitignore`).

### 2.3 Share your Google Drive folder with the service account

The service account is a "robot user" — it can only touch files shared
with it:

1. Open your certificates folder in Google Drive
   (the folder ID in the URL is what `FOLDER_ID` uses)
2. Right-click the folder → **Share**
3. Share it with the service account email
   (e.g. `certificate-uploader@your-project.iam.gserviceaccount.com`)
4. Give it the **Editor** role

Without this step, uploads fail with a 403/404 error.

---

## 3. Run Locally

### 3.1 Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3.2 Configure MySQL

Create the database and update credentials in `config.py`:

```python
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "<your-password>"
MYSQL_DB = "student_certificate_system"
```

### 3.3 Place the service account key

Copy the downloaded key file into the project root as:

```
key.json
```

(The app checks `/etc/secrets/key.json` first — used on Render — then
falls back to `./key.json` for local development.)

### 3.4 Start the app

```bash
python app.py
```

Open http://localhost:5000

---

## 4. Deploy on Render

### 4.1 Push the code

Make sure `key.json`, `token.json`, and `credentials.json` are NOT pushed
(they are gitignored).

### 4.2 Create the Render service

1. Go to https://dashboard.render.com → **New → Web Service**
2. Connect your Git repository
3. Render auto-detects `nixpacks.toml`:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn --bind 0.0.0.0:$PORT app:app`

### 4.3 Add the service account key as a Secret File

1. In your service → **Environment** tab
2. Scroll to **Secret Files** → **Add Secret File**
3. Filename: `key.json`  ← exact, case-sensitive
4. Contents: paste the entire contents of your local `key.json`
5. Save — Render redeploys automatically

The file mounts at `/etc/secrets/key.json`, which the app checks by default.
No environment variables are required for Drive access.

Optional environment variables:

| Variable | Purpose |
|---|---|
| `GOOGLE_SERVICE_ACCOUNT_FILE` | Override the key file path |
| `GOOGLE_DRIVE_FOLDER_ID` | Override the Drive folder ID |

### 4.4 Database on Render

`config.py` points to localhost MySQL, which does not exist on Render.
Use a hosted MySQL (e.g. Render MySQL, PlanetScale, Railway) and make the
values in `config.py` read from environment variables, or point them at
your hosted instance before deploying.

### 4.5 Verify the deployment

Watch the deploy logs. You should see either:

```
Drive service account key FOUND at: /etc/secrets/key.json
```

or a warning listing the paths that were checked if the file is missing.

Then upload a certificate — it should appear in the shared Drive folder.

---

## 5. Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `service account key not found` | Secret file missing or misnamed | Filename must be exactly `key.json`; redeploy after saving |
| `Unable to load service account key` | Malformed JSON | Re-paste the full file contents |
| 403 / 404 on upload | Folder not shared with service account | Share the Drive folder as Editor (step 2.3) |
| `Drive API has not been used in project` | API not enabled | Enable Google Drive API (step 2.1) |
