# desktop/tests/sync/test_sync_push_users_insert.py

"""
Responsibilities:
- Test sync push users insert behavior.
"""

# desktop/tests/test_sync_push_users_insert.py


from desktop.core.http_client import post
from desktop.config.settings import SYNC_PUSH_ENDPOINT
import uuid

TEST_JWT = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlNxVEg5QjRUS21LM3VJY3QiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2xzamF4ZXZ4emtuaXNld2FwcGRsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2ZGUyZjUxMy1jM2EzLTQxYmUtODc4NS1hZTZlNDE4MjFiM2IiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY2MDcyMzE2LCJpYXQiOjE3NjYwNjg3MTYsImVtYWlsIjoiYWRtaW5AZGVtby5wdCIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY2MDY4NzE2fV0sInNlc3Npb25faWQiOiJmYmQ3NGJlZS0xNDZmLTQ3NGMtOTJiNC1mNDliZGYyMjMyN2YiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.aSUmRr0jNXohUIQf7_zRkiVOJQJrqnq8dgqsmHMuprw"
USER_UUID = str(uuid.uuid4())


def main():
    payload = {
        "items": [
            {
                "table_name": "users",
                "operation": "insert",
                "record_uuid": USER_UUID,
                "payload": {
                    "email": "user.sync@test.com",
                    "username": "user_sync",
                    "name": "User Sync Test",
                    "role": "auditor",
                },
            }
        ]
    }

    resp = post(SYNC_PUSH_ENDPOINT, TEST_JWT, payload)
    print("Resposta do DV Server:", resp)


if __name__ == "__main__":
    main()
