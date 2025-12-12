# desktop/config/settings.py
import os

# Define the base directory for the desktop application
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Path to the SQLite database file
DB_PATH = os.path.join(BASE_DIR, "desktop.db")



# Server synchronization settings
SYNC_URL = "https://example.com/sync"  # Endpoint do servidor para sincronização

# Authentication settings
AUTH_URL = "https://example.com/auth"  # Endpoint de autenticação

# Logging settings
LOGGING_LEVEL = "DEBUG"
