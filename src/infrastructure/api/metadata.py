"""Dynamic metadata builders for the REST API and generated API docs."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from src.domain.services.calculators import CALCULATORS


@dataclass(frozen=True)
class SpecialtySummary:
    label: str
    count: int
    sample_tools: tuple[str, ...]


@dataclass(frozen=True)
class ApiCatalogSummary:
    calculator_count: int
    specialty_count: int
    top_specialties: tuple[SpecialtySummary, ...]


def _specialty_label(specialty_key: str) -> str:
    return specialty_key.replace("_", " ").title()


def collect_api_catalog_summary() -> ApiCatalogSummary:
    specialty_tools: dict[str, list[str]] = defaultdict(list)

    for calculator_class in CALCULATORS:
        calculator = calculator_class()
        metadata = calculator.metadata
        specialty_key = metadata.high_level.specialties[0].value if metadata.high_level.specialties else "other"
        specialty_tools[specialty_key].append(metadata.low_level.name)

    top_specialties = tuple(
        SpecialtySummary(
            label=_specialty_label(specialty_key),
            count=len(tool_names),
            sample_tools=tuple(sorted(tool_names)[:4]),
        )
        for specialty_key, tool_names in sorted(specialty_tools.items(), key=lambda item: (-len(item[1]), _specialty_label(item[0])))[:4]
    )

    return ApiCatalogSummary(
        calculator_count=len(CALCULATORS),
        specialty_count=len(specialty_tools),
        top_specialties=top_specialties,
    )


def build_api_description() -> str:
    summary = collect_api_catalog_summary()
    lines = [
        "## 醫學計算器 REST API",
        "",
        (f"提供 {summary.calculator_count} 個經過驗證的臨床評分工具，涵蓋 {summary.specialty_count} 個主要專科；所有計算器均引用同儕審查研究論文。"),
        "",
        "### 功能特色",
        "",
        "- 智慧工具探索 (依專科、臨床情境搜尋)",
        "- 循證醫學 (所有公式引用原始論文)",
        "- 參數驗證 (範圍檢查、必填檢查)",
        "",
        "### 使用流程",
        "",
        "1. `GET /api/v1/calculators` - 列出所有計算器",
        "2. `GET /api/v1/calculators/{tool_id}` - 取得計算器詳情",
        "3. `POST /api/v1/calculate/{tool_id}` - 執行計算",
        "",
        "### 代表性專科覆蓋",
        "",
    ]

    for specialty in summary.top_specialties:
        samples = ", ".join(specialty.sample_tools)
        lines.append(f"- {specialty.label}: {specialty.count} tools ({samples})")

    lines.append("")
    return "\n".join(lines)
