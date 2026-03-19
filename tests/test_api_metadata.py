"""Tests for generated REST API metadata."""

from __future__ import annotations

from src.infrastructure.api.metadata import build_api_description, collect_api_catalog_summary
from src.infrastructure.api.server import app


def test_api_description_uses_dynamic_catalog_counts() -> None:
    summary = collect_api_catalog_summary()
    description = build_api_description()

    assert f"提供 {summary.calculator_count} 個經過驗證的臨床評分工具" in description
    assert f"涵蓋 {summary.specialty_count} 個主要專科" in description


def test_openapi_info_uses_generated_description() -> None:
    schema = app.openapi()
    summary = collect_api_catalog_summary()

    assert schema["info"]["description"] == build_api_description()
    assert f"提供 {summary.calculator_count} 個經過驗證的臨床評分工具" in schema["info"]["description"]


def test_api_description_keeps_blank_lines_after_section_headings() -> None:
    description = build_api_description()

    assert "### 功能特色\n\n- " in description
    assert "### 使用流程\n\n1. " in description
    assert "### 代表性專科覆蓋\n\n- " in description
