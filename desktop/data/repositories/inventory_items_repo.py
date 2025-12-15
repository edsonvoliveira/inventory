# desktop/data/repositories/inventory_items_repo.py

import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from desktop.data.db.connection import get_connection


def insert_item(
    *,
    zone_uuid: str,
    product_uuid: Optional[str],
    user_uuid: Optional[str],
    scanned_code: Optional[str],
    qty_counted: float,
    batch_number: Optional[str] = None,
    expiry_date: Optional[str] = None,
    source: str = "desktop",
) -> str:
    """
    Registra uma contagem localmente e cria entrada na outbox.
    Retorna o UUID local do item criado.
    """

    item_uuid = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    payload = {
        "uuid": item_uuid,
        "zone_uuid": zone_uuid,
        "product_uuid": product_uuid,
        "user_uuid": user_uuid,
        "scanned_code": scanned_code,
        "qty_counted": qty_counted,
        "batch_number": batch_number,
        "expiry_date": expiry_date,
        "device_timestamp": now,
        "source": source,
    }

    conn = get_connection()

    # 1️⃣ Inserir item local
    conn.execute(
        """
        INSERT INTO inventory_items_local (
            uuid,
            zone_uuid,
            product_uuid,
            user_uuid,
            scanned_code,
            qty_counted,
            batch_number,
            expiry_date,
            device_timestamp,
            source,
            synced
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """,
        (
            item_uuid,
            zone_uuid,
            product_uuid,
            user_uuid,
            scanned_code,
            qty_counted,
            batch_number,
            expiry_date,
            now,
            source,
        ),
    )

    # 2️⃣ Criar outbox
    conn.execute(
        """
        INSERT INTO outbox_local (
            table_name,
            operation,
            record_uuid,
            payload
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            "inventory_items",
            "insert",
            item_uuid,
            json.dumps(payload),
        ),
    )

    conn.commit()
    conn.close()

    return item_uuid
