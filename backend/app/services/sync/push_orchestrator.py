# backend/app/services/sync/push_orchestrator.py

"""
Responsibilities:
- Sync service component for push orchestrator.
- Coordinate sync workflow steps.
"""

# backend/app/services/sync/push_orchestrator.py

import logging

from app.clients.supabase_client import get_supabase_service_client
from app.core.sync_logging import ensure_correlation_id, log_sync_event
from app.services.sync.registry import SYNC_HANDLERS
from app.schemas.sync import SyncItem


class PushOrchestrator:
    _mobile_write_tables = {"inventory_items", "zone_user_progress", "devices"}
    _admin_write_tables = {
        "inventory_items",
        "zone_user_progress",
        "devices",
        "locations",
        "products",
        "product_barcodes",
        "product_categories",
        "inventory_events",
        "inventory_event_targets",
        "zones",
        "users",
    }
    _manager_write_tables = _admin_write_tables - {"users"}
    def _get_server_id(self, table_name: str, record_uuid: str) -> int | None:
        sb = get_supabase_service_client()
        resp = (
            sb.table(table_name)
            .select("id")
            .eq("uuid", record_uuid)
            .limit(1)
            .execute()
        )
        data = resp.data or []
        if not isinstance(data, list) or not data:
            return None
        row = data[0]
        if not isinstance(row, dict):
            return None
        raw_id = row.get("id")
        if isinstance(raw_id, (int, str)):
            return int(raw_id)
        return None

    def _extract_device_uuid(self, items: list[SyncItem]) -> str | None:
        for item in items:
            payload = item.payload or {}
            device_uuid = payload.get("device_uuid") or payload.get("device_id")
            if device_uuid:
                return str(device_uuid)
        return None

    def _is_device_blocked(self, device_uuid: str) -> bool:
        sb = get_supabase_service_client()
        resp = (
            sb.table("devices")
            .select("is_blocked")
            .eq("device_uuid", device_uuid)
            .limit(1)
            .execute()
        )
        data = resp.data or []
        return bool(data and data[0].get("is_blocked") is True)

    def run(
        self,
        items: list[SyncItem],
        user,
        *,
        origin: str = "desktop",
        correlation_id: str | None = None,
    ):
        logger = logging.getLogger(__name__)
        corr_id = ensure_correlation_id(correlation_id)
        company_id = getattr(user, "company_id", getattr(user, "company_server_id", None))
        accepted: list[str] = []
        failed: list[str] = []
        rejected: dict[str, str] = {}
        server_ids: dict[str, int] = {}

        device_uuid = self._extract_device_uuid(items)
        if device_uuid and self._is_device_blocked(device_uuid):
            for item in items:
                failed.append(item.record_uuid)
                rejected[item.record_uuid] = "DEVICE_BLOCKED"
                log_sync_event(
                    logger,
                    "sync_push_item",
                    {
                        "correlation_id": corr_id,
                        "origin": origin,
                        "role": getattr(user, "role", ""),
                        "company_id": company_id,
                        "user_id": getattr(user, "db_user_id", None),
                        "device_uuid": device_uuid,
                        "table_name": item.table_name,
                        "operation": item.operation,
                        "record_uuid": item.record_uuid,
                        "status": "rejected",
                        "error_code": "DEVICE_BLOCKED",
                    },
                )
            return accepted, failed, rejected, server_ids

        for item in items:
            payload = item.payload or {}
            item_device_uuid = payload.get("device_uuid") or payload.get("device_id")
            if isinstance(item.payload, dict) and "deleted_at" in item.payload:
                item.payload.pop("deleted_at", None)

            role = getattr(user, "role", "")
            table = item.table_name
            if origin == "mobile":
                if table not in self._mobile_write_tables:
                    failed.append(item.record_uuid)
                    rejected[item.record_uuid] = "OPERATION_NOT_ALLOWED_FOR_ORIGIN"
                    log_sync_event(
                        logger,
                        "sync_push_item",
                        {
                            "correlation_id": corr_id,
                            "origin": origin,
                            "role": getattr(user, "role", ""),
                            "company_id": company_id,
                            "user_id": getattr(user, "db_user_id", None),
                            "device_uuid": item_device_uuid,
                            "table_name": table,
                            "operation": item.operation,
                            "record_uuid": item.record_uuid,
                            "status": "rejected",
                            "error_code": "OPERATION_NOT_ALLOWED_FOR_ORIGIN",
                        },
                    )
                    continue
            else:
                if role == "admin":
                    if table == "companies":
                        failed.append(item.record_uuid)
                        rejected[item.record_uuid] = "OPERATION_NOT_ALLOWED_FOR_ORIGIN"
                        log_sync_event(
                            logger,
                            "sync_push_item",
                            {
                                "correlation_id": corr_id,
                                "origin": origin,
                                "role": getattr(user, "role", ""),
                                "company_id": company_id,
                                "user_id": getattr(user, "db_user_id", None),
                                "device_uuid": item_device_uuid,
                                "table_name": table,
                                "operation": item.operation,
                                "record_uuid": item.record_uuid,
                                "status": "rejected",
                                "error_code": "OPERATION_NOT_ALLOWED_FOR_ORIGIN",
                            },
                        )
                        continue
                    allowed = table in self._admin_write_tables
                elif role == "manager":
                    if table in {"companies", "users"}:
                        failed.append(item.record_uuid)
                        rejected[item.record_uuid] = "OPERATION_NOT_ALLOWED_FOR_ORIGIN"
                        log_sync_event(
                            logger,
                            "sync_push_item",
                            {
                                "correlation_id": corr_id,
                                "origin": origin,
                                "role": getattr(user, "role", ""),
                                "company_id": company_id,
                                "user_id": getattr(user, "db_user_id", None),
                                "device_uuid": item_device_uuid,
                                "table_name": table,
                                "operation": item.operation,
                                "record_uuid": item.record_uuid,
                                "status": "rejected",
                                "error_code": "OPERATION_NOT_ALLOWED_FOR_ORIGIN",
                            },
                        )
                        continue
                    allowed = table in self._manager_write_tables
                else:
                    allowed = False

                if not allowed:
                    failed.append(item.record_uuid)
                    rejected[item.record_uuid] = "OPERATION_NOT_ALLOWED_FOR_ORIGIN"
                    log_sync_event(
                        logger,
                        "sync_push_item",
                        {
                            "correlation_id": corr_id,
                            "origin": origin,
                            "role": getattr(user, "role", ""),
                            "company_id": company_id,
                            "user_id": getattr(user, "db_user_id", None),
                            "device_uuid": item_device_uuid,
                            "table_name": table,
                            "operation": item.operation,
                            "record_uuid": item.record_uuid,
                            "status": "rejected",
                            "error_code": "OPERATION_NOT_ALLOWED_FOR_ORIGIN",
                        },
                    )
                    continue

            handler = SYNC_HANDLERS.get(item.table_name)

            if not handler:
                failed.append(item.record_uuid)
                log_sync_event(
                    logger,
                    "sync_push_item",
                    {
                        "correlation_id": corr_id,
                        "origin": origin,
                        "role": getattr(user, "role", ""),
                        "company_id": company_id,
                        "user_id": getattr(user, "db_user_id", None),
                        "device_uuid": item_device_uuid,
                        "table_name": item.table_name,
                        "operation": item.operation,
                        "record_uuid": item.record_uuid,
                        "status": "rejected",
                        "error_code": "HANDLER_NOT_FOUND",
                    },
                )
                continue

            try:
                if item.operation == "insert":
                    handler.insert(
                        payload=item.payload,
                        record_uuid=item.record_uuid,
                        user=user,
                    )

                elif item.operation == "update":
                    handler.update(
                        payload=item.payload,
                        record_uuid=item.record_uuid,
                        user=user,
                    )

                elif item.operation == "delete":
                    handler.delete(
                        payload=item.payload,
                        record_uuid=item.record_uuid,
                        user=user,
                    )

                else:
                    raise ValueError(f"Unsupported operation: {item.operation}")

                accepted.append(item.record_uuid)
                server_id = self._get_server_id(item.table_name, item.record_uuid)
                if server_id is not None:
                    server_ids[item.record_uuid] = server_id
                log_sync_event(
                    logger,
                    "sync_push_item",
                    {
                        "correlation_id": corr_id,
                        "origin": origin,
                        "role": getattr(user, "role", ""),
                        "company_id": company_id,
                        "user_id": getattr(user, "db_user_id", None),
                        "device_uuid": item_device_uuid,
                        "table_name": item.table_name,
                        "operation": item.operation,
                        "record_uuid": item.record_uuid,
                        "status": "accepted",
                    },
                )

            except Exception as exc:
                failed.append(item.record_uuid)
                rejected[item.record_uuid] = str(exc) or "server_rejected"
                log_sync_event(
                    logger,
                    "sync_push_item",
                    {
                        "correlation_id": corr_id,
                        "origin": origin,
                        "role": getattr(user, "role", ""),
                        "company_id": company_id,
                        "user_id": getattr(user, "db_user_id", None),
                        "device_uuid": item_device_uuid,
                        "table_name": item.table_name,
                        "operation": item.operation,
                        "record_uuid": item.record_uuid,
                        "status": "failed",
                        "error_code": str(exc) or "server_rejected",
                    },
                )

        return accepted, failed, rejected, server_ids
