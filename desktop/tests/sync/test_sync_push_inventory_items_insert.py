# desktop/tests/sync/test_sync_push_inventory_items_insert.py

"""
Responsibilities:
- Test sync push inventory items insert behavior.
"""

# desktop/tests/test_sync_push_inventory_items_insert.py

from desktop.core.http_client import post
from desktop.config.settings import SYNC_PUSH_ENDPOINT
import uuid

TEST_UUID = str(uuid.uuid4())

TEST_JWT = "token_goes_here"


def main():
    payload = {
        "items": [
            {
                "table_name": "inventory_items",
                "operation": "insert",
                "record_uuid": TEST_UUID,
                "payload": {
                    "zone_id": 1,
                    "product_id": 1,
                    "qty_counted": 10,
                    "device_timestamp": "2025-12-15T14:30:00Z",
                    "source": "desktop"
                }
            }
        ]
    }

    response = post(
        SYNC_PUSH_ENDPOINT,
        TEST_JWT,   # JWT sempre em segundo
        payload     # JSON sempre em terceiro
    )

    print(response)


if __name__ == "__main__":
    main()
