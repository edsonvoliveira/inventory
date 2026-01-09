# desktop/core/sync_pull_service.py

from desktop.core.http_client import get
from desktop.config.settings import SYNC_PULL_ENDPOINT
from desktop.data.db.connection import get_connection
from desktop.data.repositories.products_repo import upsert_many


def pull_once(jwt_token: str) -> int:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT value FROM app_meta WHERE key = 'last_pull_at'"
    )
    row = cur.fetchone()

    since = row[0] if row else "1970-01-01T00:00:00Z"

    payload = get(
        SYNC_PULL_ENDPOINT,
        jwt_token,
        params={"since": since},
    )

    total = 0

    products = payload.get("products", [])
    if products:
        upsert_many(products)
        total += len(products)

    cur.execute(
        """
        INSERT OR REPLACE INTO app_meta (key, value)
        VALUES ('last_pull_at', ?)
        """,
        (payload["server_ts"],),
    )

    conn.commit()
    return total