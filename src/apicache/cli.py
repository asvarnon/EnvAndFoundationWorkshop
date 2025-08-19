from __future__ import annotations

import typer
import os
import logging
from pathlib import Path

from rich import print
from .api import APIClient
from .cache import get_item, init_db, set_item


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = typer.Typer(help="CLI that fetches from an API and caches results in SQLite")


@app.callback()
def init_callback() -> None:
    init_db()


@app.command()
def fetch(
    resource: str = typer.Option(..., "--resource", "-r", help="API resource, e.g. posts"),
    id: int | None = typer.Option(None, "--id", "-i", help="Resource id"),
    base_url: str | None = typer.Option(None, "--base-url", "-b", help="Base URL of the API"),
    no_cache: bool = typer.Option( False, "--no-cache", help="Bypass cache and force a fresh request"),
    output_file: Path | None = typer.Option(
        None, "--output-file", "-f",
        help="Write to this exact JSON file (overrides --output-dir -d)"
    ),
    output_dir: Path = typer.Option(
        Path("data"), "--output-dir", "-d",
        help="Directory for auto-named file when --output-file is not given",
        file_okay=False, dir_okay=True, writable=True
    ),
    open_after: bool = typer.Option(False, "--open", "-o", help="Open the output file after fetching"),
) -> None:
    """Fetch a resource from the API, using cache when possible."""
    client = APIClient(base_url=base_url)
    key_parts = [client.base_url, resource, str(id) if id is not None else ""]
    key = ":".join([p for p in key_parts if p])
    logger.debug("Cache key: %s", key)

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
    
    # Decide where to write the file
    if output_file is None:
        # Auto filename like: posts_1.json or posts_all.json
        auto_name = f"{resource}_{id}.json" if id is not None else f"{resource}.json"
        target_path = output_dir / auto_name
    else:
        target_path = output_file 

    # Write and optionally open
    client.export_to_json(data, target_path)
    if open_after:
        logger.debug("Opening: %s", target_path)
        os.startfile(target_path)  # Windows


if __name__ == "__main__":
    app()
