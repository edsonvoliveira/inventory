# desktop/tests/test_sync_push_inventory_items_update.py

from desktop.core.http_client import post
from desktop.config.settings import SYNC_PUSH_ENDPOINT

# ⚠️ UUID REAL já existente no Supabase
EXISTING_UUID = "e7c071f9-876a-45d3-afdb-b63f31ec2cd6"

TEST_JWT = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlNxVEg5QjRUS21LM3VJY3QiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2xzamF4ZXZ4emtuaXNld2FwcGRsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2ZGUyZjUxMy1jM2EzLTQxYmUtODc4NS1hZTZlNDE4MjFiM2IiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY1ODk0MDA4LCJpYXQiOjE3NjU4OTA0MDgsImVtYWlsIjoiYWRtaW5AZGVtby5wdCIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY1ODkwNDA4fV0sInNlc3Npb25faWQiOiJkZjJlZmMzNC1kNGYxLTQ2Y2ItOTRjYy1jMzk5NTA2MjQ5ZjAiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.4dy3yMdOp3ZED5P3XJGBpGxM95wyImAD0j1_QUm9JxU"


def main():
    payload = {
        "items": [
            {
                "table_name": "inventory_items",
                "operation": "update",
                "record_uuid": EXISTING_UUID,
                "payload": {
                    "qty_counted": 15,  # novo valor
                    "device_timestamp": "2025-12-16T10:30:00Z",
                    "source": "desktop"
                }
            }
        ]
    }

    response = post(
        SYNC_PUSH_ENDPOINT,
        TEST_JWT,
        payload
    )

    print("Resposta do DV Server:", response)


if __name__ == "__main__":
    main()
