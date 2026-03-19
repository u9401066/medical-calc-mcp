$ErrorActionPreference = "Stop"

$python = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
$python = [System.IO.Path]::GetFullPath($python)

if (-not (Test-Path $python)) {
    Write-Error ".venv Python not found. Create the environment first with: uv sync --extra dev --group dev"
}

& $python -m pre_commit install --install-hooks --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
& $python -m pre_commit install-hooks

Write-Host "Installed pre-commit, pre-push, and commit-msg hooks." -ForegroundColor Green
