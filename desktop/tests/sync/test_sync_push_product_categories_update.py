# desktop/tests/sync/test_sync_push_product_categories_update.py

"""
Responsibilities:
- Test sync push product categories update behavior.
"""

# desktop/tests/test_sync_push_product_categories_update.py

from desktop.core.http_client import post
from desktop.config.settings import SYNC_PUSH_ENDPOINT

TEST_JWT = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlNxVEg5QjRUS21LM3VJY3QiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2xzamF4ZXZ4emtuaXNld2FwcGRsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2ZGUyZjUxMy1jM2EzLTQxYmUtODc4NS1hZTZlNDE4MjFiM2IiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY2MDU3OTg5LCJpYXQiOjE3NjYwNTQzODksImVtYWlsIjoiYWRtaW5AZGVtby5wdCIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY2MDU0Mzg5fV0sInNlc3Npb25faWQiOiIzNmFlOWY0YS03OTNkLTQzNDgtODhkYi1hY2UyNzhiNjNlMzUiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.IB3AyIBdpNkK3HyXvGVdKugBh6iPPLFIKCNZF4qs7DY"
CATEGORY_UUID = "f04ee633-5c4d-484f-b4f9-50ddbb97d2a1"

def main():
    payload = {
        "items": [
            {
                "table_name": "product_categories",
                "operation": "update",
                "record_uuid": CATEGORY_UUID,
                "payload": {
                    "name": "Categoria Atualizada",
                    "description": "Atualizada via sync_push"
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
