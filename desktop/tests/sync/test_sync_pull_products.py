# desktop/tests/sync/test_sync_pull_products.py

"""
Responsibilities:
- Test sync pull products behavior.
"""

# desktop/tests/test_sync_pull_products.py

from desktop.core.sync_pull_service import pull_once

TEST_JWT = "COLE_AQUI_UM_JWT_VALIDO"


def main():
    count = pull_once(TEST_JWT)
    print("Registos sincronizados:", count)


if __name__ == "__main__":
    main()
