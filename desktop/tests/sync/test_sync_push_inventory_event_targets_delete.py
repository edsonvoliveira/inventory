# desktop/tests/sync/test_sync_push_inventory_event_targets_delete.py

"""
Responsibilities:
- Test sync push inventory event targets delete behavior.
"""

# desktop/tests/test_sync_push_inventory_event_targets_delete.py

from desktop.core.http_client import post
from desktop.config.settings import SYNC_PUSH_ENDPOINT

TEST_JWT = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlNxVEg5QjRUS21LM3VJY3QiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2xzamF4ZXZ4emtuaXNld2FwcGRsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2ZGUyZjUxMy1jM2EzLTQxYmUtODc4NS1hZTZlNDE4MjFiM2IiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY2MDY1Njk4LCJpYXQiOjE3NjYwNjIwOTgsImVtYWlsIjoiYWRtaW5AZGVtby5wdCIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY2MDYyMDk4fV0sInNlc3Npb25faWQiOiIxY2QzMzMzMi1hMGVmLTQyY2YtOWZiZi01NzdjY2I2ZGUxYjYiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.ovT6kC6si7Ar5O_LToE2_N-KHpZPWaM-m0kaSajAPog"
TARGET_UUID = "e21b05b5-777c-472e-8a36-0881210ee03f"


def main():
    payload = {
        "items": [
            {
                "table_name": "inventory_event_targets",
                "operation": "delete",
                "record_uuid": TARGET_UUID,
                "payload": {}
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
