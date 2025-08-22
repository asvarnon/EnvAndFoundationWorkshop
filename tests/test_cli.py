from __future__ import annotations

import json
from collections.abc import Generator
from pathlib import Path

import pytest
import respx
from httpx import Response
from typer.testing import CliRunner

from apicache_cli_av.api import APIClient
from apicache_cli_av.cache import get_item, init_db
from apicache_cli_av.cli import app


@pytest.fixture(autouse=True)
def tmp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    # Redirect DB to a temp path for tests
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setattr("apicache_cli_av.cache.DATA_DIR", data_dir)
    monkeypatch.setattr("apicache_cli_av.cache.DB_PATH", data_dir / "cache.db")
    init_db()
    yield


@respx.mock
def test_fetch_and_cache() -> None:
    client = APIClient()
    url = client.build_url("posts", 1)

    respx.get(url).mock(return_value=Response(200, json={"id": 1, "title": "hello"}))

    # First fetch should hit network and cache via CLI
    runner = CliRunner()
    result = runner.invoke(app, ["fetch", "--resource", "posts", "--id", "1"])
    assert result.exit_code == 0
    cached = get_item(f"{client.base_url}:posts:1")
    assert cached is not None
    assert json.loads(cached)["title"] == "hello"

    # Second time, bypass httpx by reading cache directly
    cached2 = get_item(f"{client.base_url}:posts:1")
    assert cached2 is not None
    assert json.loads(cached2)["id"] == 1
