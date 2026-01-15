# mobile/config/settings.py

"""
Responsibilities:
- Define configuration constants.
- Read environment-driven settings.
"""

# mobile/config/settings.py
import os

# Define the base directory for the mobile application
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Define the path to the SQLite database file
DB_PATH = os.path.join(BASE_DIR, "data", "db", "mobile.db")
