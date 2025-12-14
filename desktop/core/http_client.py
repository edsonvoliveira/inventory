import requests
from typing import Dict, Any


class DVServerError(Exception):
    pass


def get(url: str, token: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Executa GET no DV Server com Bearer token.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    resp = requests.get(url, headers=headers, timeout=timeout)

    if not resp.ok:
        raise DVServerError(
            f"DV Server error {resp.status_code}: {resp.text}"
        )

    return resp.json()
