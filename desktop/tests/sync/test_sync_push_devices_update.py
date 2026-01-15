# desktop/tests/sync/test_sync_push_devices_update.py

"""
Responsibilities:
- Test sync push devices update behavior.
"""

# desktop/tests/test_sync_push_devices_update.py

from desktop.core.http_client import post
from desktop.config.settings import SYNC_PUSH_ENDPOINT
from datetime import datetime, timezone

TEST_JWT = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlNxVEg5QjRUS21LM3VJY3QiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2xzamF4ZXZ4emtuaXNld2FwcGRsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2ZGUyZjUxMy1jM2EzLTQxYmUtODc4NS1hZTZlNDE4MjFiM2IiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY2MDcyMzE2LCJpYXQiOjE3NjYwNjg3MTYsImVtYWlsIjoiYWRtaW5AZGVtby5wdCIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY2MDY4NzE2fV0sInNlc3Npb25faWQiOiJmYmQ3NGJlZS0xNDZmLTQ3NGMtOTJiNC1mNDliZGYyMjMyN2YiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.aSUmRr0jNXohUIQf7_zRkiVOJQJrqnq8dgqsmHMuprw"
DEVICE_UUID = "5383c4c1-2f76-4f4c-bbfd-c33c06da3c88"


def main():
    payload = {
        "items": [
            {
                "table_name": "devices",
                "operation": "update",
                "record_uuid": DEVICE_UUID,
                "payload": {
                    "app_version": "1.1.0",
                    "last_sync_at": datetime.now(timezone.utc).isoformat(),
                },
            }
        ]
    }

    resp = post(SYNC_PUSH_ENDPOINT, TEST_JWT, payload)
    print("Resposta do DV Server:", resp)


if __name__ == "__main__":
    main()
