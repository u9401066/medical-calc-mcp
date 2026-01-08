# Active Context

## Current Goals

- ## Current Focus (2026-01-08)
- ### Just Completed
- - CI/CD pipeline enhancement:
- - Added `/health` endpoint for Docker/K8s liveness probes
- - Fixed Docker healthcheck (changed from /sse to /health)
- - Added auto-fix job for develop branch (ruff --fix, format, uv lock)
- - Added auto-release job (creates GitHub Release when version changes)
- - Added concurrency control (cancels in-progress runs)
- - Updated README (EN/ZH-TW) with CI/CD documentation
- - Added tests for health endpoint (test_health_endpoint.py)
- - Fixed cross-platform mcp.json (uv run entry point)
- ### Pending Push
- Files changed:
- - .github/workflows/ci.yml (major CI/CD enhancement)
- - .vscode/mcp.json (cross-platform fix)
- - Dockerfile (healthcheck /health)
- - README.md (CI/CD docs + uv migration)
- - README.zh-TW.md (CI/CD docs + uv migration)
- - src/infrastructure/mcp/server.py (/health endpoint)
- - tests/test_health_endpoint.py (new)
- ### Next Tasks
- 1. Git push and verify CI passes
- 2. High/Low Level discovery tool design discussion
- 3. Parameter definition documentation (docs/PARAMETERS.md)

## Current Blockers

- None yet