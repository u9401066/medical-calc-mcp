# Dependency Upgrade Playbook

This playbook defines which dependencies can be upgraded in grouped automation, and which ones must be upgraded one package at a time with targeted validation.

## Upgrade Lanes

## How Dependabot Works In This Repo

Dependabot does two separate things:

1. It scans manifests such as `pyproject.toml`, GitHub Actions workflow versions, and Docker image references.
2. When it finds an allowed update, it opens a PR with only that dependency change.

In this repo, Dependabot is intentionally split into multiple update lanes in [.github/dependabot.yml](../.github/dependabot.yml):

- `pip` safe tooling lane: weekly, grouped PRs for low-risk packages such as `ruff` and `pre-commit`
- `pip` manual-review lane: monthly, isolated PRs for runtime, protocol, typing, and test-engine packages
- `docker` lane: monthly PRs for Docker image updates
- `github-actions` lane: weekly PRs for workflow action version bumps

Because this repo uses `uv.lock`, Dependabot alone is not enough for Python packages. A companion workflow in [.github/workflows/dependabot-lockfile.yml](../.github/workflows/dependabot-lockfile.yml) detects `pyproject.toml` changes on Dependabot PRs and regenerates `uv.lock` automatically.

### Lane A: Safe to auto-upgrade in grouped PRs

These are tooling-only or low-blast-radius dependencies. They may still break CI, but they do not normally change runtime behavior of the MCP server or REST API.

| Package | Why it can be grouped | Required validation |
|---------|------------------------|---------------------|
| `ruff` | Formatter/linter only | `ruff check .`, `ruff format --check src tests scripts` |
| `pre-commit` | Hook runner only | `python -m pre_commit run --all-files` |
| `pytest-cov` | Reporting layer only | `pytest tests --cov=src --cov-report=xml` |
| `mkdocs-awesome-pages-plugin` | Docs navigation only | `docs.yml` workflow or local MkDocs build |

These packages are grouped into a single weekly PR by Dependabot.

### Lane B: Must upgrade one package at a time

These affect protocol behavior, schema generation, typing, async execution, or test semantics. Upgrade them in isolated PRs with focused review.

| Package | Why it must be isolated | Extra validation |
|---------|--------------------------|------------------|
| `mcp[cli]` | Protocol compatibility, FastMCP behavior, tool schema injection, progress support | MCP smoke tests, `scripts/check_project_consistency.py --check-tests`, manual MCP inspector run |
| `fastapi` | REST routing, OpenAPI generation, dependency injection | Regenerate OpenAPI + REST docs, run API tests |
| `starlette` | Transport/runtime layer below FastAPI and MCP custom routes | API tests, Docker smoke test |
| `pydantic` | Request/response validation and schema generation | mypy, API tests, OpenAPI diff |
| `uvicorn` | Runtime serving behavior | local API startup, Docker smoke test |
| `sse-starlette` | SSE transport behavior | MCP HTTP/SSE manual smoke test |
| `pytest` | Assertion semantics, async fixtures, collection behavior | full `pytest tests`, check collected count drift |
| `pytest-asyncio` | async fixture lifecycle | focused async/API tests |
| `mypy` | type system behavior and stricter diagnostics | `mypy --no-incremental src tests`, review new diagnostics |

These packages are still proposed by Dependabot, but as isolated PRs with `manual-review` labeling.

### Lane C: External toolchain, always manual

These are outside normal package lock updates and should never be batch-upgraded blindly.

| Tool | Policy |
|------|--------|
| `uv` | Upgrade manually and verify lockfile behavior, frozen sync, and CI cache behavior |
| Python minor versions | Add/upgrade one version at a time in CI matrix |
| GitHub Actions versions | Review changelogs and permissions before bumping |

## How To Adjust The Mapping

When you add or move a dependency, update the repo in this order:

1. Decide which lane the package belongs to.
2. Update [.github/dependabot.yml](../.github/dependabot.yml).
3. If the package is Python-related, keep `uv.lock` in sync.
4. Update this playbook if the policy changed.

Examples:

- Add a new low-risk docs or lint tool:
  Put it in the `pip` safe tooling lane `allow` list and, if appropriate, the `tooling-safe` group.
- Move a package from safe to manual review:
  Remove it from the grouped safe lane and add it to the manual-review lane.
- Add a new runtime package:
  Add it to the manual-review `pip` lane so Dependabot proposes it one PR at a time.
- Change update frequency:
  Edit the relevant `schedule` block in [.github/dependabot.yml](../.github/dependabot.yml).
- Add a new ecosystem:
  Add another `updates` entry, for example `npm`, `terraform`, or an extra Docker directory.

## Operational Notes

- If a Dependabot Python PR changes `pyproject.toml`, the lockfile workflow should commit an updated `uv.lock` back to the PR branch.
- If you intentionally do not want a package auto-proposed, leave it out of the corresponding `allow` list.
- If a package starts causing repeated breakage, move it from Lane A to Lane B rather than disabling Dependabot entirely.

## Standard Upgrade Procedure

### Grouped tooling upgrade

```bash
uv lock --upgrade-package ruff --upgrade-package pre-commit --upgrade-package pytest-cov
uv sync --extra dev --group dev
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m ruff format src tests scripts --check
.venv\Scripts\python.exe -m pre_commit run --all-files
```

### Isolated runtime or protocol upgrade

```bash
uv lock --upgrade-package fastapi
uv sync --extra dev --group dev
.venv\Scripts\python.exe -m mypy --no-incremental src tests
.venv\Scripts\python.exe -m pytest tests -q
.venv\Scripts\python.exe scripts\generate_openapi_spec.py
.venv\Scripts\python.exe scripts\generate_rest_api_docs.py
.venv\Scripts\python.exe scripts\generate_tool_catalog_docs.py
.venv\Scripts\python.exe scripts\check_project_consistency.py --check-tests
```

## Required Validation Matrix

Run all of the following before merging any Lane B or Lane C upgrade:

```bash
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m mypy --no-incremental src tests
.venv\Scripts\python.exe -m pytest tests -q
.venv\Scripts\python.exe scripts\generate_openapi_spec.py --check
.venv\Scripts\python.exe scripts\generate_rest_api_docs.py --check
.venv\Scripts\python.exe scripts\generate_tool_catalog_docs.py --check
.venv\Scripts\python.exe scripts\check_project_consistency.py --check-tests
```

## Review Rules

- Never combine `mcp`, `fastapi`, `pydantic`, and `starlette` in the same upgrade PR.
- Any OpenAPI diff requires review of [docs_site/api/openapi.json](docs_site/api/openapi.json) and [docs_site/api/rest-api.md](docs_site/api/rest-api.md).
- Any MCP SDK diff requires review of progress support, tool schema injection, and health endpoint behavior.
- If collected test count changes unexpectedly, inspect collection output before accepting the upgrade.

## Rollback Strategy

- Revert the lockfile and dependency bounds together.
- Regenerate OpenAPI and REST docs after rollback to remove stale artifacts.
- Re-run the full validation matrix before re-merging.
