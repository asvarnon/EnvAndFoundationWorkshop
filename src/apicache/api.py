from __future__ import annotations

import json
from typing import Any, cast

import httpx

DEFAULT_BASE_URL = "https://jsonplaceholder.typicode.com"


class APIClient:
    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = base_url or DEFAULT_BASE_URL
        self.timeout = timeout

    def build_url(self, resource: str, id: int | None = None) -> str:
        url = f"{self.base_url.rstrip('/')}/{resource.strip('/')}"
        if id is not None:
            url += f"/{id}"
        return url

    def fetch(self, resource: str, id: int | None = None) -> dict[str, Any]:
        url = self.build_url(resource, id)
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url)
            resp.raise_for_status()
            payload: dict[str, Any] = cast(dict[str, Any], resp.json())
            return payload

    def export_to_json(self, data: dict[str, Any], filename: str) -> None:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def to_json_str(data: dict[str, Any]) -> str:
        return json.dumps(data, ensure_ascii=False, sort_keys=True)

    @staticmethod
    def from_json_str(data: str) -> dict[str, Any]:
        return cast(dict[str, Any], json.loads(data))
