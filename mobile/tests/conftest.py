from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
USER_ENV = REPO_ROOT / "backend" / ".user_test"

if USER_ENV.exists():
    load_dotenv(USER_ENV, override=True)
