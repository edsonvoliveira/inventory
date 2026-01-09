# desktop/tests/test_sync_push_product_barcodes_update.py

from desktop.core.http_client import post
from desktop.config.settings import SYNC_PUSH_ENDPOINT

TEST_JWT = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlNxVEg5QjRUS21LM3VJY3QiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2xzamF4ZXZ4emtuaXNld2FwcGRsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2ZGUyZjUxMy1jM2EzLTQxYmUtODc4NS1hZTZlNDE4MjFiM2IiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY2MDcwMDk0LCJpYXQiOjE3NjYwNjY0OTQsImVtYWlsIjoiYWRtaW5AZGVtby5wdCIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY2MDY2NDkzfV0sInNlc3Npb25faWQiOiJhM2M4ZmEyMS05Mjc3LTQ2ODQtOWNlYS1lOWFjNDE0ZjU2YzciLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.DuOmhBgGRj-ERMWNYabur5jbr7EHA6UuFAszainr4O4"
BARCODE_UUID = "97386479-d510-45ce-864c-068c13756229"


def main():
    payload = {
        "items": [
            {
                "table_name": "product_barcodes",
                "operation": "update",
                "record_uuid": BARCODE_UUID,
                "payload": {
                    "description": "Descrição atualizada",
                    "is_active": True,
                },
            }
        ]
    }

    resp = post(SYNC_PUSH_ENDPOINT, TEST_JWT, payload)
    print("Resposta do DV Server:", resp)


if __name__ == "__main__":
    main()
