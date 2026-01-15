# mobile_push_smoke.py

import json
import uuid
from datetime import datetime, timezone

from mobile.data.db.connection import get_connection
from mobile.app_core_container import build_services


def main() -> None:
    conn = get_connection()
    cur = conn.cursor()

    zone = cur.execute(
        "SELECT server_id, event_server_id FROM zones_local LIMIT 1"
    ).fetchone()
    user = cur.execute(
        "SELECT server_id FROM users_local LIMIT 1"
    ).fetchone()
    product = cur.execute(
        "SELECT server_id FROM products_local LIMIT 1"
    ).fetchone()

    if not zone or not user:
        raise SystemExit("Sem dados locais: rode o bootstrap/pull antes.")

    zone_server_id, event_server_id = zone
    user_server_id = user[0]
    product_server_id = product[0] if product else None

    record_uuid = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    event_uuid = f"server:{event_server_id}"
    zone_uuid = f"server:{zone_server_id}"
    user_uuid = f"server:{user_server_id}"
    product_uuid = f"server:{product_server_id}" if product_server_id else None

    conn.execute(
        """
        INSERT INTO inventory_items_local (
            uuid, event_uuid, event_server_id, zone_uuid, zone_server_id,
            user_uuid, user_server_id, product_uuid, product_server_id,
            qty_counted, device_timestamp, source, created_at, synced
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record_uuid,
            event_uuid,
            event_server_id,
            zone_uuid,
            zone_server_id,
            user_uuid,
            user_server_id,
            product_uuid,
            product_server_id,
            1,
            now,
            "mobile",
            now,
            0,
        ),
    )

    payload = {
        "zone_id": zone_server_id,
        "product_id": product_server_id,
        "qty_counted": 1,
        "device_timestamp": now,
        "source": "mobile",
    }

    conn.execute(
        """
        INSERT INTO outbox_local (table_name, operation, record_uuid, payload)
        VALUES (?, ?, ?, ?)
        """,
        ("inventory_items", "insert", record_uuid, json.dumps(payload)),
    )

    conn.commit()
    conn.close()

    accepted, failed = build_services().sync_push.run()
    print(f"push accepted={accepted} failed={failed}")


if __name__ == "__main__":
    main()
