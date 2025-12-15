# desktop/config/settings.py
import os

# Define the base directory for the desktop application
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Path to the SQLite database file
DB_PATH = os.path.join(BASE_DIR, "desktop.db")

# -----------------------------
# DV Server settings
# -----------------------------
DV_SERVER_BASE_URL = "http://127.0.0.1:8000"
API_V1_PREFIX = "/v1"

SYNC_BOOTSTRAP_ENDPOINT = f"{DV_SERVER_BASE_URL}{API_V1_PREFIX}/sync/bootstrap"
SYNC_PUSH_ENDPOINT = f"{DV_SERVER_BASE_URL}{API_V1_PREFIX}/sync/push"

# -----------------------------
# Logging settings
# -----------------------------
LOGGING_LEVEL = "DEBUG"
