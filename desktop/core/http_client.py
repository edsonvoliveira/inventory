# desktop/core/http_client.py

import requests


class DVServerError(Exception):
    pass


def _headers(jwt_token: str) -> dict:
    return {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
    }


def get(url: str, jwt_token: str, params: dict | None = None, timeout: int = 10) -> dict:
    resp = requests.get(
        url,
        headers=_headers(jwt_token),
        params=params,
        timeout=timeout,
    )

    if resp.status_code != 200:
        raise DVServerError(
            f"DV Server error {resp.status_code}: {resp.text}"
        )

    return resp.json()


def post(url: str, jwt_token: str, json_body: dict, timeout: int = 10) -> dict:
    resp = requests.post(
        url,
        headers=_headers(jwt_token),
        json=json_body,
        timeout=timeout,
    )

    if resp.status_code != 200:
        raise DVServerError(
            f"DV Server error {resp.status_code}: {resp.text}"
        )

    return resp.json()
