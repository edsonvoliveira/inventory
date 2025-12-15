from desktop.core.http_client import post
from desktop.config.settings import SYNC_PUSH_ENDPOINT
import uuid

TEST_UUID = str(uuid.uuid4())

TEST_JWT = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlNxVEg5QjRUS21LM3VJY3QiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2xzamF4ZXZ4emtuaXNld2FwcGRsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2ZGUyZjUxMy1jM2EzLTQxYmUtODc4NS1hZTZlNDE4MjFiM2IiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY1ODQzNTc5LCJpYXQiOjE3NjU4Mzk5NzksImVtYWlsIjoiYWRtaW5AZGVtby5wdCIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY1ODM5OTc5fV0sInNlc3Npb25faWQiOiIxOWU1MjVmNy0zZDUzLTQ0ZTYtYTRhZC1mYjRlZTliMjVlZTAiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.oUwS59j47reKnusoSGPQotHCsnNtbd-jgR2LNQ6CxzQ"


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
