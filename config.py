import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.getenv("MYSQL_CONFIG_FILE", os.path.join(BASE_DIR, "config.json"))

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, encoding="utf-8") as config_file:
        DB_CONFIG = json.load(config_file)
else:
    DB_CONFIG = {}


def _db_value(key, default=""):
    return str(os.getenv(key, DB_CONFIG.get(key, default))).strip()


def _json_value(key, default):
    raw = os.getenv(key)
    if raw is not None:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return default
    return DB_CONFIG.get(key, default)


class Config:
    SECRET_KEY = "student-certificate-system-secret-key-2026"
    MYSQL_HOST = _db_value("MYSQL_HOST")
    MYSQL_USER = _db_value("MYSQL_USER")
    MYSQL_PASSWORD = _db_value("MYSQL_PASSWORD")
    MYSQL_DB = _db_value("MYSQL_DB")
    MYSQL_PORT = int(_db_value("MYSQL_PORT", "3306"))

    DB_DDL_AUTO = _db_value("DB_DDL_AUTO", "none").lower() or "none"
    SEED_USERS = _json_value("SEED_USERS", [])
