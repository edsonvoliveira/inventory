# desktop/tests/test_sync_push_locations_delete.py

from desktop.core.http_client import post
from desktop.config.settings import SYNC_PUSH_ENDPOINT

TEST_JWT = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlNxVEg5QjRUS21LM3VJY3QiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2xzamF4ZXZ4emtuaXNld2FwcGRsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2ZGUyZjUxMy1jM2EzLTQxYmUtODc4NS1hZTZlNDE4MjFiM2IiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY2MDYwNDA2LCJpYXQiOjE3NjYwNTY4MDYsImVtYWlsIjoiYWRtaW5AZGVtby5wdCIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY2MDU2ODA2fV0sInNlc3Npb25faWQiOiI4OTYxNDNmZS05NjFmLTQ0OGYtYWU5Ny1lMmE0YjhmZGNiNmMiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.POyimlmWr0qbV0CgiP1BYt9aZAuSvo11SaLsCjpKzlE"
LOCATION_UUID = "6d3b6496-6cd7-475a-9c76-1f8dd8d37b1c"

def main():
    payload = {
        "items": [
            {
                "table_name": "locations",
                "operation": "delete",
                "record_uuid": LOCATION_UUID,
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
