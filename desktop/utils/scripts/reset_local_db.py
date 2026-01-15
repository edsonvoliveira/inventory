from __future__ import annotations

from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    db_path = repo_root / "desktop" / "inventory.db"

    if db_path.exists():
        db_path.unlink()
        print(f"Removido: {db_path}")
    else:
        print(f"Nada para remover: {db_path}")


if __name__ == "__main__":
    main()
