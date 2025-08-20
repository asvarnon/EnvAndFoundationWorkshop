from __future__ import annotations

from pathlib import Path
import json
import os
from typing import Any, cast
from .utils.json_utils import save_json
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://jsonplaceholder.typicode.com"


class APIClient:
    def __init__(
        self, 
        base_url: str | None = None,
        timeout: float = 10.0,
        api_key: str | None = None,
        auth_header: str = "Authorization",
        auth_scheme: str = "Bearer",
    ) -> None:
        self.base_url = base_url or DEFAULT_BASE_URL
        self.timeout = timeout
        self.api_key = api_key
        self.auth_header = auth_header
        self.auth_scheme = auth_scheme

    def build_url(self, resource: str, id: int | None = None) -> str:
        url = f"{self.base_url.rstrip('/')}/{resource.strip('/')}"
        if id is not None:
            url += f"/{id}"
        logger.debug("Built URL: %s", url)
        return url
    
    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if not self.api_key:
            return headers
        if self.auth_header.lower() == "authorization":
            # Use canonical header casing; include scheme only if present
            value = f"{self.auth_scheme} {self.api_key}" if self.auth_scheme else str(self.api_key)
            headers["Authorization"] = value
        else:
            headers[self.auth_header] = str(self.api_key)
        return headers

    def fetch(self, resource: str, id: int | None = None) -> dict[str, Any]:
        url = self.build_url(resource, id)
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url)
            resp.raise_for_status()
            payload: dict[str, Any] = cast(dict[str, Any], resp.json())
            # logger.debug("Fetched data: %s", payload)
            logger.debug("Fetched data IS RETURNED")
            return payload

    def export_to_json(self, data: dict[str, Any], filename: str | Path) -> Path:
        return save_json(data, filename)

    @staticmethod
    def to_json_str(data: dict[str, Any]) -> str:
        return json.dumps(data, ensure_ascii=False, sort_keys=True)

    @staticmethod
    def from_json_str(data: str) -> dict[str, Any]:
        return cast(dict[str, Any], json.loads(data))
