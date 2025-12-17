# desktop/core/sync_service.py

from typing import Tuple, Dict, Any, List

from desktop.core.http_client import post
from desktop.config.settings import SYNC_PUSH_ENDPOINT
from desktop.data.outbox.outbox_repo import (
    get_pending,
    mark_success,
    mark_failed,
)


def push_outbox_once(jwt_token: str) -> Tuple[int, int]:
    """
    Envia um lote de registos da outbox_local para o DV Server.

    - Lê até N registos pendentes (attempts < 5)
    - Monta o payload no formato esperado pelo /v1/sync/push
    - Chama o endpoint
    - Remove os 'accepted'
    - Marca como falhados os 'failed'

    Retorna (qtd_accepted, qtd_failed).
    """

    pending = get_pending(limit=100)

    if not pending:
        return 0, 0

    # Mapa record_uuid -> outbox_id
    id_by_uuid: Dict[str, int] = {
        row["record_uuid"]: row["id"] for row in pending
    }

    items: List[Dict[str, Any]] = []
    for row in pending:
        items.append(
            {
                "table_name": row["table_name"],
                "operation": row["operation"],
                "record_uuid": row["record_uuid"],
                "payload": row["payload"],
            }
        )

    payload = {"items": items}

    # Chamada ao DV Server
    resp = post(SYNC_PUSH_ENDPOINT, jwt_token, payload)

    accepted_uuids = resp.get("accepted", []) or []
    failed_uuids = resp.get("failed", []) or []

    # Remover da outbox os aceites
    success_ids = [id_by_uuid[u] for u in accepted_uuids if u in id_by_uuid]
    if success_ids:
        mark_success(success_ids)

    # Atualizar tentativa + erro genérico nos falhados
    for u in failed_uuids:
        outbox_id = id_by_uuid.get(u)
        if outbox_id is not None:
            mark_failed(outbox_id, "Rejected by DV Server")

    return len(accepted_uuids), len(failed_uuids)
