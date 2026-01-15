# desktop/tests/sync/test_sync_push_products_delete.py

"""
Responsibilities:
- Test sync push products delete behavior.
"""

# desktop/tests/test_sync_push_products_delete.py

from desktop.core.http_client import post
from desktop.config.settings import SYNC_PUSH_ENDPOINT

TEST_JWT = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlNxVEg5QjRUS21LM3VJY3QiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2xzamF4ZXZ4emtuaXNld2FwcGRsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2ZGUyZjUxMy1jM2EzLTQxYmUtODc4NS1hZTZlNDE4MjFiM2IiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY1OTkxMDM3LCJpYXQiOjE3NjU5ODc0MzcsImVtYWlsIjoiYWRtaW5AZGVtby5wdCIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY1OTg3NDM3fV0sInNlc3Npb25faWQiOiI3YTJjMjk0Zi0xYWUzLTQxYTItYWE0MS0zYjM3MjczN2QxYTEiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.ttVXZ76Wxz-hfG2R1t4bfXnTwPbHkoEp1fJFiCTHpyQ"
PRODUCT_UUID = "27e37a95-50fb-4470-b036-080532795a22"

def main():
    payload = {
        "items": [
            {
                "table_name": "products",
                "operation": "delete",
                "record_uuid": PRODUCT_UUID,
                "payload": {}
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
