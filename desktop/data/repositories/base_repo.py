from __future__ import annotations
"""
Responsibilities:
- Basic CRUD operations for local database repositories
- Outbox pattern for async operations
- Syncing with server
- Configurable via RepoConfig
- Designed for extensibility for specific entity repositories
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Optional
from uuid import uuid4
import json

from desktop.data.db.connection import get_connection


@dataclass(frozen=True)
class RepoConfig:
    table: str
    entity_name: str                 # ex: "products"
    uuid_col: str = "uuid"

    # colunas opcionais
    synced_col: Optional[str] = None
    synced_at_col: Optional[str] = None
    updated_at_col: Optional[str] = None
    deleted_at_col: Optional[str] = None
    active_col: Optional[str] = None
    source_col: Optional[str] = None

    # comportamento
    enable_outbox: bool = False

    # colunas para upsert do servidor
    server_upsert_cols: tuple[str, ...] = ()

    # colunas editáveis pela UI
    ui_writable_cols: tuple[str, ...] = ()


class BaseRepo:
    def __init__(self, cfg: RepoConfig, conn=None):
        self.cfg = cfg
        self._owns_conn = conn is None
        self.conn = conn or get_connection()

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------
    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _commit(self):
        if self._owns_conn:
            self.conn.commit()

    def _close(self):
        if self._owns_conn:
            self.conn.close()

    def _enqueue_outbox(self, operation: str, record_uuid: str, payload: dict):
        if not self.cfg.enable_outbox:
            return

        self.conn.execute(
            """
            INSERT INTO outbox_local (table_name, operation, record_uuid, payload)
            VALUES (?, ?, ?, ?)
            """,
            (self.cfg.entity_name, operation, record_uuid, json.dumps(payload)),
        )

    # --------------------------------------------------
    # READ (UI)
    # --------------------------------------------------
    def get_all(self, active_only: bool = True):
        sql = f"SELECT * FROM {self.cfg.table}"
        if active_only and self.cfg.active_col:
            sql += f" WHERE {self.cfg.active_col} = 1"
        cur = self.conn.execute(sql)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def get_by_uuid(self, uuid: str):
        cur = self.conn.execute(
            f"SELECT * FROM {self.cfg.table} WHERE {self.cfg.uuid_col} = ?",
            (uuid,),
        )
        row = cur.fetchone()
        if not row:
            return None
        cols = [c[0] for c in cur.description]
        return dict(zip(cols, row))

    # --------------------------------------------------
    # CRUD LOCAL (UI)
    # --------------------------------------------------
    def create(self, data: dict) -> str:
        uuid = data.get(self.cfg.uuid_col) or str(uuid4())
        now = self._now()

        record = {self.cfg.uuid_col: uuid}
        for c in self.cfg.ui_writable_cols:
            if c in data:
                record[c] = data[c]

        # company_server_id automático (se existir na tabela)
        if "company_server_id" in self.cfg.server_upsert_cols and "company_server_id" not in record:
            from desktop.data.repositories.app_meta_repo import get_meta
            company_server_id = get_meta("company_server_id", self.conn)
            if company_server_id is None:
                raise RuntimeError("company_server_id não definido no app_meta")
            record["company_server_id"] = int(company_server_id)

        if self.cfg.updated_at_col:
            record[self.cfg.updated_at_col] = now
        if self.cfg.synced_col:
            record[self.cfg.synced_col] = 0
        if self.cfg.synced_at_col:
            record[self.cfg.synced_at_col] = None
        if self.cfg.source_col:
            record[self.cfg.source_col] = "desktop"
        if self.cfg.active_col:
            record.setdefault(self.cfg.active_col, 1)

        cols = list(record.keys())
        sql = f"""
        INSERT INTO {self.cfg.table} ({', '.join(cols)})
        VALUES ({', '.join(['?'] * len(cols))})
        """
        self.conn.execute(sql, tuple(record[c] for c in cols))

        self._enqueue_outbox("insert", uuid, record)
        self._commit()
        self._close()
        return uuid

    def update(self, uuid: str, data: dict):
        now = self._now()
        updates = {}

        for c in self.cfg.ui_writable_cols:
            if c in data:
                updates[c] = data[c]

        if not updates:
            return

        if self.cfg.updated_at_col:
            updates[self.cfg.updated_at_col] = now
        if self.cfg.synced_col:
            updates[self.cfg.synced_col] = 0
        if self.cfg.synced_at_col:
            updates[self.cfg.synced_at_col] = None
        if self.cfg.source_col:
            updates[self.cfg.source_col] = "desktop"

        set_sql = ", ".join(f"{k}=?" for k in updates)
        self.conn.execute(
            f"UPDATE {self.cfg.table} SET {set_sql} WHERE {self.cfg.uuid_col}=?",
            tuple(updates.values()) + (uuid,),
        )

        self._enqueue_outbox("update", uuid, updates)
        self._commit()
        self._close()

    # --------------------------------------------------
    # SYNC PULL (SERVER -> LOCAL)
    # --------------------------------------------------
    def upsert_many(self, rows: list[Mapping[str, Any]]) -> int:
        if not rows:
            return 0

        cols = list(self.cfg.server_upsert_cols)
        placeholders = ", ".join(["?"] * len(cols))
        updates = ", ".join(f"{c}=excluded.{c}" for c in cols if c != self.cfg.uuid_col)

        sql = f"""
        INSERT INTO {self.cfg.table} ({', '.join(cols)})
        VALUES ({placeholders})
        ON CONFLICT({self.cfg.uuid_col}) DO UPDATE SET {updates}
        """

        count = 0
        for row in rows:
            self.conn.execute(sql, tuple(row.get(c) for c in cols))
            count += 1

        self._commit()
        self._close()
        return count

    
    def soft_delete(self, uuid: str):
        if not self.cfg.active_col:
            raise RuntimeError("Soft delete nao suportado")

        now = self._now()
        updates: dict[str, Any] = {}

        updates[self.cfg.active_col] = 0
        if self.cfg.updated_at_col:
            updates[self.cfg.updated_at_col] = now
        if self.cfg.synced_col:
            updates[self.cfg.synced_col] = 0
        if self.cfg.synced_at_col:
            updates[self.cfg.synced_at_col] = None
        if self.cfg.source_col:
            updates[self.cfg.source_col] = "desktop"

        set_sql = ", ".join(f"{k}=?" for k in updates)
        self.conn.execute(
            f"UPDATE {self.cfg.table} SET {set_sql} WHERE {self.cfg.uuid_col}=?",
            tuple(updates.values()) + (uuid,),
        )

        self._enqueue_outbox("delete", uuid, updates)
        self._commit()
        self._close()

    def restore(self, uuid: str):
        if not self.cfg.active_col:
            raise RuntimeError("Restore nao suportado para esta entidade")

        now = self._now()
        updates: dict[str, Any] = {}

        updates[self.cfg.active_col] = 1
        if self.cfg.updated_at_col:
            updates[self.cfg.updated_at_col] = now
        if self.cfg.synced_col:
            updates[self.cfg.synced_col] = 0
        if self.cfg.synced_at_col:
            updates[self.cfg.synced_at_col] = None
        if self.cfg.source_col:
            updates[self.cfg.source_col] = "desktop"

        set_sql = ", ".join(f"{k}=?" for k in updates)
        self.conn.execute(
            f"UPDATE {self.cfg.table} SET {set_sql} WHERE {self.cfg.uuid_col}=?",
            tuple(updates.values()) + (uuid,),
        )

        self._enqueue_outbox("update", uuid, updates)
        self._commit()
        self._close()

    # --------------------------------------------------
    # HARD DELETE (ADMIN)
    # --------------------------------------------------
    def delete_all(self):
        self.conn.execute(f"DELETE FROM {self.cfg.table}")
        self._commit()
        self._close()
