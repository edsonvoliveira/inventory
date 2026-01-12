# backend/app/services/sync/push_orchestrator.py

from app.services.sync.registry import SYNC_HANDLERS
from app.schemas.sync import SyncItem


class PushOrchestrator:
    def run(self, items: list[SyncItem], user):
        accepted: list[str] = []
        failed: list[str] = []

        for item in items:
            handler = SYNC_HANDLERS.get(item.table_name)

            if not handler:
                failed.append(item.record_uuid)
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

            except Exception:
                failed.append(item.record_uuid)

        return accepted, failed