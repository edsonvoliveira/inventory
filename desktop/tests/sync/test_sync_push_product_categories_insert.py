# desktop/tests/sync/test_sync_push_product_categories_insert.py

"""
Responsibilities:
- Test sync push product categories insert behavior.
"""

# desktop/tests/test_sync_push_product_categories_insert.py

from desktop.core.http_client import post
from desktop.config.settings import SYNC_PUSH_ENDPOINT
import uuid

TEST_JWT = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlNxVEg5QjRUS21LM3VJY3QiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2xzamF4ZXZ4emtuaXNld2FwcGRsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2ZGUyZjUxMy1jM2EzLTQxYmUtODc4NS1hZTZlNDE4MjFiM2IiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY2MDU3OTg5LCJpYXQiOjE3NjYwNTQzODksImVtYWlsIjoiYWRtaW5AZGVtby5wdCIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY2MDU0Mzg5fV0sInNlc3Npb25faWQiOiIzNmFlOWY0YS03OTNkLTQzNDgtODhkYi1hY2UyNzhiNjNlMzUiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.IB3AyIBdpNkK3HyXvGVdKugBh6iPPLFIKCNZF4qs7DY"
CAT_UUID = str(uuid.uuid4())


def main():
    payload = {
        "items": [
            {
                "table_name": "product_categories",
                "operation": "insert",
                "record_uuid": CAT_UUID,
                "payload": {
                    "code": "CAT-TEST-001",
                    "name": "Categoria Teste Sync",
                    "description": "Criado via sync_push",
                    "is_active": True
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
