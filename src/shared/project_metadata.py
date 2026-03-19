"""Project metadata helpers shared by runtime and maintenance scripts."""

from __future__ import annotations

import tomllib
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

PROJECT_NAME = "medical-calc-mcp"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"


@lru_cache(maxsize=1)
def get_project_version() -> str:
    """Return the installed package version or fall back to pyproject.toml."""
    try:
        return version(PROJECT_NAME)
    except PackageNotFoundError:
        with PYPROJECT_PATH.open("rb") as handle:
            pyproject = tomllib.load(handle)
        return str(pyproject["project"]["version"])
