# mobile/tests/test_e2e_headless.py

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from utils.scripts.mobile_push_smoke import main


def _has_env(name: str) -> bool:
    return bool(os.getenv(name, "").strip())


def run() -> None:
    required = ["DV_SERVER_BASE_URL", "E2E_JWT_TOKEN", "E2E_COMPANY_SERVER_ID"]
    missing = [name for name in required if not _has_env(name)]
    if missing:
        print(f"SKIP: faltam envs {', '.join(missing)}")
        return

    main()


if __name__ == "__main__":
    run()
