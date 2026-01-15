# desktop/tests/bootstrap/test_bootstrap_real.py

"""
Responsibilities:
- Test bootstrap real behavior.
"""

from desktop.core.bootstrap_service import run_bootstrap
from desktop.data.repositories.app_meta_repo import get_meta

TEST_JWT = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlNxVEg5QjRUS21LM3VJY3QiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2xzamF4ZXZ4emtuaXNld2FwcGRsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2ZGUyZjUxMy1jM2EzLTQxYmUtODc4NS1hZTZlNDE4MjFiM2IiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY2MzEwNzg4LCJpYXQiOjE3NjYzMDcxODgsImVtYWlsIjoiYWRtaW5AZGVtby5wdCIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY2MzA3MTg4fV0sInNlc3Npb25faWQiOiIyMWRlNTExMS05NGZhLTQ3NTUtODFiZC05ZmJkOWYyMjc1NTMiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.SFhljaSi8wlg0lBgeIVH9_DbgCg3UzacEWkbQ7zB54c"


def main():
    ok = run_bootstrap(TEST_JWT)
    print("Bootstrap OK?", ok)
    print("bootstrap_done:", get_meta("bootstrap_done"))
    print("last_full_sync_at:", get_meta("last_full_sync_at"))


if __name__ == "__main__":
    main()
