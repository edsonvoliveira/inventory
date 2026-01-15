# desktop/tests/sync/test_sync_push_product_barcodes_insert.py

"""
Responsibilities:
- Test sync push product barcodes insert behavior.
"""

# desktop/tests/test_sync_push_product_barcodes_insert.py

from desktop.core.http_client import post
from desktop.config.settings import SYNC_PUSH_ENDPOINT
import uuid

TEST_JWT = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlNxVEg5QjRUS21LM3VJY3QiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2xzamF4ZXZ4emtuaXNld2FwcGRsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2ZGUyZjUxMy1jM2EzLTQxYmUtODc4NS1hZTZlNDE4MjFiM2IiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY2MDcwMDk0LCJpYXQiOjE3NjYwNjY0OTQsImVtYWlsIjoiYWRtaW5AZGVtby5wdCIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY2MDY2NDkzfV0sInNlc3Npb25faWQiOiJhM2M4ZmEyMS05Mjc3LTQ2ODQtOWNlYS1lOWFjNDE0ZjU2YzciLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.DuOmhBgGRj-ERMWNYabur5jbr7EHA6UuFAszainr4O4"

BARCODE_UUID = str(uuid.uuid4())


def main():
    payload = {
        "items": [
            {
                "table_name": "product_barcodes",
                "operation": "insert",
                "record_uuid": BARCODE_UUID,
                "payload": {
                    "product_id": 1,   # server_id do produto
                    "barcode": "7891234567890",
                    "description": "Código de barras teste",
                    "is_active": True,
                },
            }
        ]
    }

    resp = post(SYNC_PUSH_ENDPOINT, TEST_JWT, payload)
    print("Resposta do DV Server:", resp)


if __name__ == "__main__":
    main()
