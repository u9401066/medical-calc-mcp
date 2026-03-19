"""Tests for shared project metadata utilities."""

from __future__ import annotations

import tomllib

from src.infrastructure.mcp.config import McpServerConfig
from src.shared.project_metadata import PROJECT_ROOT, get_project_version


def test_project_version_matches_pyproject() -> None:
    """The shared version helper should remain aligned with pyproject.toml."""
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)

    assert get_project_version() == pyproject["project"]["version"]


def test_mcp_config_uses_project_version() -> None:
    """Default MCP config should derive its version from shared metadata."""
    assert McpServerConfig().version == get_project_version()
