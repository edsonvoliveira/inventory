# desktop/tests/bootstrap/test_outbox_push_once.py

"""
Responsibilities:
- Test outbox push once behavior.
"""

# desktop/tests/test_outbox_push_once.py

import uuid
import json

from desktop.app_core_container import build_services
from desktop.core.session_service import SessionService
from desktop.data.db.connection import get_connection

# 🔑 Cole aqui um JWT VÁLIDO do Supabase (mesmo que usa no /v1/auth/me e /v1/sync/bootstrap)
TEST_JWT = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlNxVEg5QjRUS21LM3VJY3QiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2xzamF4ZXZ4emtuaXNld2FwcGRsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2ZGUyZjUxMy1jM2EzLTQxYmUtODc4NS1hZTZlNDE4MjFiM2IiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY1OTExNjg1LCJpYXQiOjE3NjU5MDgwODUsImVtYWlsIjoiYWRtaW5AZGVtby5wdCIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzY1OTA4MDg1fV0sInNlc3Npb25faWQiOiJmODk1MzQ5ZC1kZjgzLTQ1YzMtYWQzOS0xZTY4YTQ4NDhlZTciLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.Uqkmn2kiJX_cWVbuguat_ofAkCd7EiLbHXaoK-izeYA"


def seed_outbox_inventory_item() -> str:
    """
    Insere um registo de teste na tabela outbox_local,
    simulando um INSERT de inventory_items vindo do desktop.
    Retorna o record_uuid usado.
    """
    record_uuid = str(uuid.uuid4())

    payload = {
        "zone_id": 1,                     # precisa existir em inventory_items.zones no Supabase
        "product_id": 1,                  # precisa existir em products
        "qty_counted": 5,
        "device_timestamp": "2025-12-16T10:00:00Z",
        "source": "desktop",
    }

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO outbox_local (table_name, operation, record_uuid, payload, attempts)
        VALUES (?, ?, ?, ?, 0)
        """,
        (
            "inventory_items",
            "insert",
            record_uuid,
            json.dumps(payload),  # fica TEXT no SQLite; o outbox_repo converte para dict
        ),
    )
    conn.commit()
    conn.close()

    return record_uuid


def main():
    print("=== TESTE push_outbox_once ===")

    record_uuid = seed_outbox_inventory_item()
    print(f"record_uuid inserido na outbox_local: {record_uuid}")

    SessionService.set_jwt_token(TEST_JWT)
    accepted, failed = build_services().sync_push.run()

    print(f"accepted: {accepted}")
    print(f"failed:   {failed}")


if __name__ == "__main__":
    main()
