# desktop/tests/sync/test_sync_push_inventory_event_targets_insert.py

"""
Responsibilities:
- Test sync push inventory event targets insert behavior.
"""

# desktop/tests/test_sync_push_inventory_event_targets_insert.py

import uuid
from desktop.core.http_client import post
from desktop.config.settings import SYNC_PUSH_ENDPOINT

TEST_JWT = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlNxVEg5QjRUS21LM3VJY3QiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2xzamF4ZXZ4emtuaXNld2FwcGRsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2ZGUyZjUxMy1jM2EzLTQxYmUtODc4NS1hZTZlNDE4MjFiM2IiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY2MDY1Njk4LCJpYXQiOjE3NjYwNjIwOTgsImVtYWlsIjoiYWRtaW5AZGVtby5wdCIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY2MDYyMDk4fV0sInNlc3Npb25faWQiOiIxY2QzMzMzMi1hMGVmLTQyY2YtOWZiZi01NzdjY2I2ZGUxYjYiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.ovT6kC6si7Ar5O_LToE2_N-KHpZPWaM-m0kaSajAPog"
TARGET_UUID = str(uuid.uuid4())

# ⚠️ estes UUIDs DEVEM existir no Supabase
EVENT_UUID = "e894a192-394a-4d60-b1f2-b0043137a6d9"
PRODUCT_UUID = "27e37a95-50fb-4470-b036-080532795a22"

def main():
    payload = {
        "items": [
            {
                "table_name": "inventory_event_targets",
                "operation": "insert",
                "record_uuid": TARGET_UUID,
                "payload": {
                    "event_uuid": EVENT_UUID,
                    "product_uuid": PRODUCT_UUID,
                    "expected_qty": 100
                }
            }
        ]
    }

    print("Enviando payload:", payload)

    response = post(
        SYNC_PUSH_ENDPOINT,
        TEST_JWT,
        payload
    )

    print("Resposta do DV Server:", response)


if __name__ == "__main__":
    main()
