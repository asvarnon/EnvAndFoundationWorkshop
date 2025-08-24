# Ops Notes (PyPI, Docker, GitHub Actions)

This doc summarizes how to build, publish, and run apicache-cli-av, plus how to use the CI workflows.

## 1) PyPI: manual release (Windows PowerShell)

Prereqs (one-time)
- Create a PyPI API token: https://pypi.org/manage/account/token/
- Copy the token (starts with pypi-).

Release steps
```powershell
# Bump version
poetry version patch   # or: minor / major

# Clean old artifacts
if (Test-Path dist) { Remove-Item -Recurse -Force dist }
if (Test-Path build) { Remove-Item -Recurse -Force build }
Get-ChildItem -Filter *.egg-info | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Build
poetry build
# If Twine isn't installed yet:
poetry run pip install -U twine
poetry run twine check dist/*   # optional

# Upload to PyPI
$env:TWINE_USERNAME="__token__"
$env:TWINE_PASSWORD="pypi-<YOUR-PYPI-TOKEN>"
poetry run twine upload dist/*
```

Verify install (from PyPI)
```powershell
python -m venv .venv-pypi-test
.\.venv-pypi-test\Scripts\Activate.ps1
pip install --upgrade pip
pip install apicache-cli-av
apicache-cli-av --help
```

Common issues
- 403 File already exists → bump version, rebuild, re-upload.
- Not allowed to upload → ensure the name is apicache-cli-av and artifacts in dist/ match that name.
- Missing CLI → ensure pyproject has:
  [tool.poetry.scripts]
  apicache-cli-av = "apicache_cli_av.cli:app"

## 2) Docker: build, tag, push

Build from current branch
```powershell
# Replace 'youruser' with your Docker Hub username 
docker build -t youruser/apicache:dev .
```

Tag and push a release
```powershell
# Example version tag
docker tag youruser/apicache:dev youruser/apicache:v0.1.5
docker push youruser/apicache:v0.1.5
```

Run the CLI via container
```powershell
# Help
docker run --rm youruser/apicache:v0.1.5 apicache-cli-av --help

# Persist outputs/cache to host
mkdir -Force data | Out-Null
docker run --rm -v ${PWD}/data:/app/data youruser/apicache:v0.1.5 `
  apicache-cli-av fetch -r posts -i 1 --output-dir /app/data
```

API key example
```powershell
docker run --rm -e APICACHE_API_KEY="your-api-key" youruser/apicache:v0.1.5 `
  apicache-cli-av fetch -r items -i 42
```

Note: --open won’t launch apps on the host from inside a container.

## 3) GitHub Actions: workflows (in .github/workflows)

- docker.yml: builds/pushes Docker images on pushes/tags.
  - Needs secrets: DOCKERHUB_USERNAME, DOCKERHUB_TOKEN.
  - Tags: latest on main, branch name on other branches, plus sha; GHCR if configured.

- publish.yml: builds artifacts; can publish to TestPyPI on main push and PyPI on tag v*.
  - Needs secrets: TEST_PYPI_API_TOKEN, PYPI_API_TOKEN.
  - Trigger a real PyPI release by pushing a tag like v0.1.5.

- pip-audit.yml: dependency vulnerability audit.
  - Currently manual (workflow_dispatch). To schedule weekly, uncomment the cron.
  - Steps (manual): Actions → pip-audit → Run workflow.

Where to put configs
- Dependabot: .github/dependabot.yml (not a workflow).
- Workflows (CI): .github/workflows/*.yml (docker, publish, pip-audit).

## 4) Local dev quick reference

Install deps and run tests
```powershell
poetry install
poetry run pytest -q
```

Run CLI locally
```powershell
poetry run apicache-cli-av --help
```

Check and update dependencies
```powershell
poetry show --outdated
poetry update <package>
```

Security audit locally (Poetry-managed)
```powershell
# Install export plugin once
poetry self add poetry-plugin-export
# Export current deps and audit
poetry export -f requirements.txt --without-hashes -o req.txt
poetry run pip install -U pip-audit
poetry run pip-audit -r req.txt
```

Alternative audit (plain venv)
```powershell
python -m venv .venv-audit
.\.venv-audit\Scripts\Activate.ps1
pip install -U pip-audit
pip-audit -r req.txt
```

## 5) Package usage

CLI examples
```powershell
apicache-cli-av fetch -r posts -i 1 --output-dir data
apicache-cli-av fetch -r posts -i 1 --output-file data/posts_1.json
apicache-cli-av fetch -r items -i 42 --base-url https://api.example.com
```

Library example (Python)
```python
from apicache_cli_av.api import APIClient
client = APIClient()
data = client.fetch("posts", 1)
print(data)
```

## 6) Notes/policies

- Python support: 3.10–3.12
- Click pinned: < 8.2 (Typer 0.12 compatibility)
- Versioning: bump before publishing; PyPI doesn’t allow re-uploading same version
- Secrets required in GitHub:
  - DOCKERHUB_USERNAME, DOCKERHUB_TOKEN
  - TEST_PYPI_API_TOKEN (optional), PYPI_API_TOKEN