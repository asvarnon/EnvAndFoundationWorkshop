# apicache-cli-av

Tiny Typer CLI that fetches an API resource and caches results in SQLite (SQLModel). Use it as a command-line tool or import its library in other projects.

## Features
- Fetch JSON from an HTTP API (configurable base URL)
- Optional API key header
- SQLite-backed cache for idempotent reads
- Save output to an auto-named file or a specific file
- Simple Docker image for zero-setup runs

---

## Install (PyPI)

Recommended for CLI users: pipx
- pipx ensures isolated CLI installs and adds the command to your PATH.

```powershell
pip install --upgrade pipx
pipx install apicache-cli-av
apicache-cli-av --help
```

Standard pip (inside a virtual environment)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U apicache-cli-av
apicache-cli-av --help
```

Install from TestPyPI (if you’re testing pre-releases)
```powershell
pip install --index-url https://test.pypi.org/simple --extra-index-url https://pypi.org/simple apicache-cli-av
```

---

## Usage

Basic fetch (prints JSON and writes a file)
```powershell
apicache-cli-av fetch --resource posts --id 1
```

- By default, the tool writes to an auto-named file under data/, e.g., data/posts_1.json.
- Use --output-file to write to an exact path, or --output-dir to change the default directory.

Save to a specific file
```powershell
apicache-cli-av fetch -r posts -i 1 --output-file data/posts_1.json
```

Save to a different directory with auto filename
```powershell
apicache-cli-av fetch -r posts -i 1 --output-dir out
```

Open the file after saving (Windows will open with the OS default app)
```powershell
apicache-cli-av fetch -r posts -i 1 --output-dir data --open
```

Bypass cache
```powershell
apicache-cli-av fetch -r posts -i 1 --no-cache
```

Specify a base URL
```powershell
apicache-cli-av fetch -r items -i 42 --base-url https://api.example.com
```

Pass an API key (prefer environment variable)
```powershell
# Windows PowerShell
$env:APICACHE_API_KEY = "your-api-key"
apicache-cli-av fetch -r items -i 42

# Or via flag (less secure; may show in history/process list)
apicache-cli-av fetch -r items -i 42 --api-key "your-api-key"
```

Environment variables
- APICACHE_API_KEY: API key to send (usually as Authorization: Bearer <key>)
- API_BASE_URL: Default base URL if not passed via --base-url
- APICACHE_OUTPUT_DIR: Default directory for saved JSON files (when no --output-file)
- APICACHE_DB_PATH: SQLite path for the cache (defaults to data/cache.db)

---

## Docker

Pull the image (replace the repository if you use GHCR or a different namespace)
```powershell
docker pull docker.io/asvarnon/apicache:latest
```

Run the CLI (ephemeral container)
```powershell
docker run --rm docker.io/asvarnon/apicache:latest apicache-cli-av --help
```

Persist cache and outputs to your host
```powershell
mkdir -Force data | Out-Null
docker run --rm `
  -v ${PWD}/data:/app/data `
  docker.io/asvarnon/apicache:latest `
  apicache-cli-av fetch -r posts -i 1 --output-dir /app/data
```

Provide an API key at runtime
```powershell
docker run --rm `
  -e APICACHE_API_KEY="your-api-key" `
  docker.io/asvarnon/apicache:latest `
  apicache-cli-av fetch -r items -i 42
```

Notes
- --open won’t launch desktop apps from inside a container. Save to a mounted volume and open the file on your host.
- Use a specific tag (e.g., :v1.2.3 or :<sha>) for reproducible runs.

---

## Library usage

```python
from apicache_cli_av.api import APIClient

client = APIClient()  # or APIClient(base_url="https://api.example.com", api_key="...")
data = client.fetch("posts", 1)
print(data)
```

---

## Development

Setup
```powershell
poetry install
poetry run pytest -q
```

Local CLI
```powershell
poetry run apicache-cli-av --help
```

Build and publish (manual)
```powershell
poetry build
# TestPyPI
poetry run twine upload --repository testpypi dist/*
# PyPI
poetry run twine upload dist/*
```

---

## Troubleshooting

- Typer/Click error like “Parameter.make_metavar() missing 1 required positional argument: 'ctx'”
  - Ensure Click < 8.2 with Typer 0.12 (this project pins click >=8.1,<8.2).

- TestPyPI upload 403
  - Bump version; ensure you’re using username __token__ and a valid token for the correct index.

- Import errors for utils
  - Package path is apicache_cli_av; make sure relative imports are used within the package and that the project is installed (pip/poetry) or PYTHONPATH includes src/ during debugging.

---

## License

MIT

