# desktop/tests/test_sync_push_product_categories_insert.py

from desktop.core.http_client import post
from desktop.config.settings import SYNC_PUSH_ENDPOINT
import uuid

TEST_JWT = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlNxVEg5QjRUS21LM3VJY3QiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2xzamF4ZXZ4emtuaXNld2FwcGRsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2ZGUyZjUxMy1jM2EzLTQxYmUtODc4NS1hZTZlNDE4MjFiM2IiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY1OTMyODIyLCJpYXQiOjE3NjU5MjkyMjIsImVtYWlsIjoiYWRtaW5AZGVtby5wdCIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY1OTI5MjIyfV0sInNlc3Npb25faWQiOiJmOGMwMzllYy04YTI5LTRmYWMtYWY4Zi0xZDFlM2VmZTNkNTMiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.xKHbx45LJGuTJaY_vIBxWq3lXr5k7crzreSdof5rE_k"
TEST_UUID = str(uuid.uuid4())


def main():
    payload = {
        "items": [
            {
                "table_name": "product_categories",
                "operation": "insert",
                "record_uuid": TEST_UUID,
                "payload": {
                    "company_id": 1,
                    "code": "CAT-001",
                    "name": "Bebidas",
                    "description": "Categoria de bebidas"
                }
            }
        ]
    }

    print("Enviando payload:")
    print(payload)

    response = post(
        SYNC_PUSH_ENDPOINT,
        TEST_JWT,
        payload
    )

    print("Resposta do DV Server:")
    print(response)


if __name__ == "__main__":
    main()
