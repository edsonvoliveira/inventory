# desktop/tests/test_sync_push_products_insert.py

from desktop.core.http_client import post
from desktop.config.settings import SYNC_PUSH_ENDPOINT
import uuid

TEST_JWT = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlNxVEg5QjRUS21LM3VJY3QiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2xzamF4ZXZ4emtuaXNld2FwcGRsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2ZGUyZjUxMy1jM2EzLTQxYmUtODc4NS1hZTZlNDE4MjFiM2IiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY1OTg2OTk3LCJpYXQiOjE3NjU5ODMzOTcsImVtYWlsIjoiYWRtaW5AZGVtby5wdCIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY1OTgzMzk3fV0sInNlc3Npb25faWQiOiJlYTMxY2RiZC02MTA0LTRkZjYtYTE0OC00OTAwNTI3NWQxOWEiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.CVvjzDys5odCjXpGQV09mbuhwiqjimuKboot4gXVDvo"

PRODUCT_UUID = str(uuid.uuid4())

def main():
    payload = {
        "items": [
            {
                "table_name": "products",
                "operation": "insert",
                "record_uuid": PRODUCT_UUID,
                "payload": {
                    "company_id": 1,
                    "sku": "SKU-TEST-001",
                    "name": "Produto Teste Sync",
                    "uom_base": "UN",
                    "uom_inventory": "UN",
                    "conversion_factor": 1,
                    "system_qty": 0,
                    "is_sensitive": False,
                    "serial_number_enabled": False
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
