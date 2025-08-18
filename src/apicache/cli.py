from __future__ import annotations

import typer
from rich import print

from .api import APIClient
from .cache import get_item, init_db, set_item

app = typer.Typer(help="CLI that fetches from an API and caches results in SQLite")


@app.callback()
def init_callback() -> None:
    init_db()


@app.command()
def fetch(
    resource: str = typer.Option(..., "--resource", "-r", help="API resource, e.g. posts"),
    id: int | None = typer.Option(None, "--id", "-i", help="Resource id"),
    base_url: str | None = typer.Option(None, "--base-url", "-b", help="Base URL of the API"),
    no_cache: bool = typer.Option(
        False, "--no-cache", help="Bypass cache and force a fresh request"
    ),
) -> None:
    """Fetch a resource from the API, using cache when possible."""
    client = APIClient(base_url=base_url)
    key_parts = [client.base_url, resource, str(id) if id is not None else ""]
    key = ":".join([p for p in key_parts if p])

    if not no_cache:
        cached = get_item(key)
        if cached is not None:
            print("[green]Cache hit[/green]")
            print(cached)
            raise typer.Exit(code=0)

    data = client.fetch(resource, id)
    json_str = client.to_json_str(data)
    set_item(key, json_str)
    print("[yellow]Fetched fresh[/yellow]")
    print(json_str)


if __name__ == "__main__":
    app()
