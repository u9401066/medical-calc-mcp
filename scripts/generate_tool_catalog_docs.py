#!/usr/bin/env python
"""Generate registry-backed catalog and guideline coverage docs for docs, docs_site, and README."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from src.domain.registry import ToolRegistry
from src.domain.services.calculators import CALCULATORS
from src.shared.project_metadata import PROJECT_ROOT, get_project_version

SPECIALTY_LABELS: dict[str, tuple[str, str]] = {
    "anesthesiology": ("Anesthesiology", "麻醉科"),
    "cardiology": ("Cardiology", "心臟科"),
    "critical_care": ("Critical Care", "重症醫學科"),
    "dermatology": ("Dermatology", "皮膚科"),
    "emergency_medicine": ("Emergency Medicine", "急診醫學科"),
    "endocrinology": ("Endocrinology", "內分泌科"),
    "family_medicine": ("Family Medicine", "家庭醫學科"),
    "gastroenterology": ("Gastroenterology", "腸胃科"),
    "geriatrics": ("Geriatrics", "老年醫學科"),
    "gynecology": ("Gynecology", "婦科"),
    "hematology": ("Hematology", "血液科"),
    "hepatology": ("Hepatology", "肝膽科"),
    "infectious_disease": ("Infectious Disease", "感染科"),
    "internal_medicine": ("Internal Medicine", "內科"),
    "neonatology": ("Neonatology", "新生兒科"),
    "nephrology": ("Nephrology", "腎臟科"),
    "neurology": ("Neurology", "神經科"),
    "obstetrics": ("Obstetrics", "產科"),
    "obstetrics_gynecology": ("Obstetrics & Gynecology", "婦產科"),
    "oncology": ("Oncology", "腫瘤科"),
    "pain_medicine": ("Pain Medicine", "疼痛醫學"),
    "pediatrics": ("Pediatrics", "小兒科"),
    "preventive_medicine": ("Preventive Medicine", "預防醫學科"),
    "psychiatry": ("Psychiatry", "精神科"),
    "pulmonology": ("Pulmonology", "胸腔科"),
    "rheumatology": ("Rheumatology", "風濕免疫科"),
    "surgery": ("Surgery", "外科"),
    "toxicology": ("Toxicology", "毒理科"),
    "urology": ("Urology", "泌尿科"),
}

GUIDELINE_DOMAIN_LABELS: dict[str, str] = {
    "敗血症/重症": "Sepsis / Critical Care",
    "心血管": "Cardiovascular",
    "消化道出血": "GI Bleeding",
    "肝臟疾病": "Liver Disease",
    "腎臟疾病": "Kidney Disease",
    "肺炎/呼吸": "Respiratory / Pneumonia",
    "血栓栓塞": "Thromboembolism",
    "神經科": "Neurology",
    "麻醉科": "Anesthesiology",
    "創傷": "Trauma",
    "燒傷": "Burns",
    "小兒科": "Pediatrics",
    "腫瘤科": "Oncology",
    "營養科": "Nutrition",
    "風濕科": "Rheumatology",
    "骨質疏鬆": "Osteoporosis",
}

CATALOG_OUTPUTS: dict[tuple[str, str], Path] = {
    ("docs", "en"): PROJECT_ROOT / "docs/CALCULATOR_CATALOG.md",
    ("docs", "zh-TW"): PROJECT_ROOT / "docs/CALCULATOR_CATALOG.zh-TW.md",
    ("docs_site", "en"): PROJECT_ROOT / "docs_site/calculators/index.md",
    ("docs_site", "zh-TW"): PROJECT_ROOT / "docs_site/zh-tw/calculators.md",
}

GUIDELINE_OUTPUTS: dict[tuple[str, str], Path] = {
    ("docs", "en"): PROJECT_ROOT / "docs/GUIDELINE_COVERAGE_SUMMARY.md",
    ("docs", "zh-TW"): PROJECT_ROOT / "docs/GUIDELINE_COVERAGE_SUMMARY.zh-TW.md",
    ("docs_site", "en"): PROJECT_ROOT / "docs_site/development/guideline-coverage.md",
    ("docs_site", "zh-TW"): PROJECT_ROOT / "docs_site/zh-tw/guideline-coverage.md",
}

README_OUTPUTS: dict[str, Path] = {
    "en": PROJECT_ROOT / "README.md",
    "zh-TW": PROJECT_ROOT / "README.zh-TW.md",
}

CATALOG_MARKERS = {
    "en": ("<!-- BEGIN GENERATED:CATALOG_OVERVIEW -->", "<!-- END GENERATED:CATALOG_OVERVIEW -->"),
    "zh-TW": ("<!-- BEGIN GENERATED:CATALOG_OVERVIEW_ZH -->", "<!-- END GENERATED:CATALOG_OVERVIEW_ZH -->"),
}

GUIDELINE_MARKERS = {
    "en": ("<!-- BEGIN GENERATED:GUIDELINE_OVERVIEW -->", "<!-- END GENERATED:GUIDELINE_OVERVIEW -->"),
    "zh-TW": ("<!-- BEGIN GENERATED:GUIDELINE_OVERVIEW_ZH -->", "<!-- END GENERATED:GUIDELINE_OVERVIEW_ZH -->"),
}

PRIMARY_GUIDELINE_DOC = PROJECT_ROOT / "docs/GUIDELINE_RECOMMENDED_TOOLS_2023_2025.md"
SECONDARY_GUIDELINE_DOC = PROJECT_ROOT / "docs/GUIDELINE_RECOMMENDED_TOOLS_2020_2025.md"


@dataclass(frozen=True)
class CatalogEntry:
    tool_id: str
    name: str
    purpose: str
    specialty_key: str
    specialty_label_en: str
    specialty_label_zh: str
    reference_count: int


@dataclass(frozen=True)
class GuidelineDomainSummary:
    domain_zh: str
    domain_en: str
    implemented_count: int
    total_count: int
    recommended_tools: tuple[str, ...]
    pending_tools: tuple[str, ...]


@dataclass(frozen=True)
class GuidelineCoverageSummary:
    domains: tuple[GuidelineDomainSummary, ...]
    implemented_count: int
    total_count: int


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    for calculator_class in CALCULATORS:
        registry.register(calculator_class())
    return registry


def _escape_cell(text: str) -> str:
    return " ".join(text.replace("|", "\\|").split())


def _clean_inline_markdown(text: str) -> str:
    cleaned = re.sub(r"[`*]", "", text)
    return " ".join(cleaned.split())


def _split_markdown_items(text: str) -> tuple[str, ...]:
    cleaned = _clean_inline_markdown(text)
    if cleaned in {"", "-", "—"}:
        return ()
    return tuple(item.strip() for item in cleaned.split(",") if item.strip())


def _parse_ratio(text: str) -> tuple[int, int] | None:
    match = re.search(r"(\d+)\s*/\s*(\d+)", text)
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2))


def _specialty_labels(specialty_key: str) -> tuple[str, str]:
    fallback = specialty_key.replace("_", " ").title()
    return SPECIALTY_LABELS.get(specialty_key, (fallback, specialty_key.replace("_", " ")))


def collect_entries() -> list[CatalogEntry]:
    registry = build_registry()
    entries: list[CatalogEntry] = []

    for metadata in registry.list_all():
        specialty_key = (
            metadata.high_level.specialties[0].value
            if metadata.high_level.specialties
            else "other"
        )
        specialty_en, specialty_zh = _specialty_labels(specialty_key)
        entries.append(
            CatalogEntry(
                tool_id=metadata.low_level.tool_id,
                name=metadata.low_level.name,
                purpose=metadata.low_level.purpose,
                specialty_key=specialty_key,
                specialty_label_en=specialty_en,
                specialty_label_zh=specialty_zh,
                reference_count=len(metadata.references),
            )
        )

    return sorted(entries, key=lambda entry: (entry.specialty_label_en, entry.tool_id))


def collect_by_specialty(entries: list[CatalogEntry]) -> dict[str, list[CatalogEntry]]:
    by_specialty: dict[str, list[CatalogEntry]] = defaultdict(list)
    for entry in entries:
        by_specialty[entry.specialty_key].append(entry)
    return by_specialty


def parse_guideline_summary() -> GuidelineCoverageSummary:
    lines = PRIMARY_GUIDELINE_DOC.read_text(encoding="utf-8").splitlines()
    in_summary = False
    domains: list[GuidelineDomainSummary] = []

    for line in lines:
        if line.startswith("## 📊 整體對照摘要"):
            in_summary = True
            continue
        if not in_summary:
            continue
        if in_summary and domains and not line.lstrip().startswith("|"):
            break
        if not line.lstrip().startswith("|"):
            continue

        parts = [part.strip() for part in line.split("|")]
        if len(parts) < 6:
            continue
        domain_zh = parts[1]
        if domain_zh in {"", "領域"} or set(domain_zh) == {"-"}:
            continue

        recommended_tools = _split_markdown_items(parts[2])
        ratio = _parse_ratio(parts[3])
        pending_tools = _split_markdown_items(parts[4])
        if ratio is None:
            total_count = len(recommended_tools)
            implemented_count = max(total_count - len(pending_tools), 0)
        else:
            implemented_count, total_count = ratio

        domains.append(
            GuidelineDomainSummary(
                domain_zh=domain_zh,
                domain_en=GUIDELINE_DOMAIN_LABELS.get(domain_zh, domain_zh),
                implemented_count=implemented_count,
                total_count=total_count,
                recommended_tools=recommended_tools,
                pending_tools=pending_tools,
            )
        )

    return GuidelineCoverageSummary(
        domains=tuple(domains),
        implemented_count=sum(domain.implemented_count for domain in domains),
        total_count=sum(domain.total_count for domain in domains),
    )


def render_catalog(locale: str, audience: str) -> str:
    entries = collect_entries()
    version = get_project_version()
    by_specialty = collect_by_specialty(entries)
    title = "Calculator Catalog" if audience == "docs" else "Calculator Overview"
    if locale == "zh-TW":
        title = "計算器目錄" if audience == "docs" else "網站版計算器總覽"

    if locale == "en":
        lines = [
            f"# {title}",
            "",
            "> Generated from the live calculator registry. Do not edit manually.",
            f"> Regenerate with `uv run python scripts/generate_tool_catalog_docs.py` (v{version}).",
            "",
            f"This snapshot contains **{len(entries)} calculators** across **{len(by_specialty)} primary specialties**.",
            "",
            "## Specialty Summary",
            "",
            "| Specialty | Tools | Sample tool IDs |",
            "|-----------|------:|-----------------|",
        ]
        for specialty_key in sorted(by_specialty, key=lambda key: _specialty_labels(key)[0]):
            specialty_entries = by_specialty[specialty_key]
            specialty_label, _ = _specialty_labels(specialty_key)
            samples = ", ".join(f"`{entry.tool_id}`" for entry in specialty_entries[:3])
            lines.append(f"| {_escape_cell(specialty_label)} | {len(specialty_entries)} | {samples} |")

        lines.extend(
            [
                "",
                "## Full Tool Catalog",
                "",
                "| Tool ID | Name | Primary Specialty | Purpose | Refs |",
                "|--------|------|-------------------|---------|-----:|",
            ]
        )
        for entry in entries:
            lines.append(
                "| "
                f"`{entry.tool_id}` | {_escape_cell(entry.name)} | {_escape_cell(entry.specialty_label_en)} | "
                f"{_escape_cell(entry.purpose)} | {entry.reference_count} |"
            )

        lines.extend(["", "## By Specialty", ""])
        for specialty_key in sorted(by_specialty, key=lambda key: _specialty_labels(key)[0]):
            specialty_entries = by_specialty[specialty_key]
            specialty_label, _ = _specialty_labels(specialty_key)
            lines.extend(
                [
                    f"### {specialty_label} ({len(specialty_entries)})",
                    "",
                    "| Tool ID | Name | Purpose |",
                    "|--------|------|---------|",
                ]
            )
            for entry in specialty_entries:
                lines.append(
                    "| "
                    f"`{entry.tool_id}` | {_escape_cell(entry.name)} | {_escape_cell(entry.purpose)} |"
                )
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    lines = [
        f"# {title}",
        "",
        "> 由目前 registry 自動產生，請勿手動編輯。",
        f"> 重新產生指令：`uv run python scripts/generate_tool_catalog_docs.py` (v{version})。",
        "",
        f"此快照包含 **{len(entries)} 個計算器**，涵蓋 **{len(by_specialty)} 個主要專科**。",
        "",
        "## 專科摘要",
        "",
        "| 專科 | 工具數 | 範例 tool ID |",
        "|------|------:|--------------|",
    ]
    for specialty_key in sorted(by_specialty, key=lambda key: _specialty_labels(key)[0]):
        specialty_entries = by_specialty[specialty_key]
        _, specialty_label = _specialty_labels(specialty_key)
        samples = ", ".join(f"`{entry.tool_id}`" for entry in specialty_entries[:3])
        lines.append(f"| {_escape_cell(specialty_label)} | {len(specialty_entries)} | {samples} |")

    lines.extend(
        [
            "",
            "## 完整工具清單",
            "",
            "| Tool ID | 名稱 | 主要專科 | 用途 | 文獻數 |",
            "|--------|------|----------|------|------:|",
        ]
    )
    for entry in entries:
        lines.append(
            "| "
            f"`{entry.tool_id}` | {_escape_cell(entry.name)} | {_escape_cell(entry.specialty_label_zh)} | "
            f"{_escape_cell(entry.purpose)} | {entry.reference_count} |"
        )

    lines.extend(["", "## 依專科分組", ""])
    for specialty_key in sorted(by_specialty, key=lambda key: _specialty_labels(key)[0]):
        specialty_entries = by_specialty[specialty_key]
        _, specialty_label = _specialty_labels(specialty_key)
        lines.extend(
            [
                f"### {specialty_label} ({len(specialty_entries)})",
                "",
                "| Tool ID | 名稱 | 用途 |",
                "|--------|------|------|",
            ]
        )
        for entry in specialty_entries:
            lines.append(
                "| "
                f"`{entry.tool_id}` | {_escape_cell(entry.name)} | {_escape_cell(entry.purpose)} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_guideline_summary(locale: str, audience: str) -> str:
    summary = parse_guideline_summary()
    version = get_project_version()
    title = "Guideline Coverage Summary" if locale == "en" else "指引覆蓋摘要"
    if audience == "docs_site" and locale == "en":
        title = "Guideline Coverage"
    if audience == "docs_site" and locale == "zh-TW":
        title = "網站版指引覆蓋摘要"

    if locale == "en":
        lines = [
            f"# {title}",
            "",
            "> Generated from the 2023-2025 guideline review and the live registry. Do not edit manually.",
            f"> Regenerate with `uv run python scripts/generate_tool_catalog_docs.py` (v{version}).",
            "",
            (
                f"Current coverage tracks **{summary.implemented_count}/{summary.total_count}** "
                f"guideline-recommended tools across **{len(summary.domains)}** clinical domains."
            ),
            "",
            "## Coverage by Domain",
            "",
            "| Domain | Implemented | Total | Coverage | Outstanding |",
            "|--------|------------:|------:|---------:|-------------|",
        ]
        for domain in summary.domains:
            outstanding = ", ".join(domain.pending_tools) if domain.pending_tools else "-"
            coverage = 0.0 if domain.total_count == 0 else domain.implemented_count / domain.total_count * 100
            lines.append(
                f"| {_escape_cell(domain.domain_en)} | {domain.implemented_count} | {domain.total_count} | {coverage:.0f}% | {_escape_cell(outstanding)} |"
            )

        lines.extend(
            [
                "",
                "## Source Documents",
                "",
                "- [Generated calculator catalog](CALCULATOR_CATALOG.md)" if audience == "docs" else "- [Website calculator catalog](../calculators/index.md)",
                "- [2023-2025 detailed guideline review](GUIDELINE_RECOMMENDED_TOOLS_2023_2025.md)" if audience == "docs" else "- [2023-2025 detailed guideline review](../../docs/GUIDELINE_RECOMMENDED_TOOLS_2023_2025.md)",
                "- [2020-2025 historical guideline review](GUIDELINE_RECOMMENDED_TOOLS_2020_2025.md)" if audience == "docs" else "- [2020-2025 historical guideline review](../../docs/GUIDELINE_RECOMMENDED_TOOLS_2020_2025.md)",
                "",
            ]
        )
        return "\n".join(lines)

    lines = [
        f"# {title}",
        "",
        "> 由 2023-2025 指引整理與 live registry 自動產生，請勿手動編輯。",
        f"> 重新產生指令：`uv run python scripts/generate_tool_catalog_docs.py` (v{version})。",
        "",
        f"目前共追蹤 **{summary.implemented_count}/{summary.total_count}** 個指引建議工具，涵蓋 **{len(summary.domains)}** 個臨床領域。",
        "",
        "## 各領域覆蓋率",
        "",
        "| 領域 | 已實作 | 總數 | 覆蓋率 | 尚待補齊 |",
        "|------|-------:|-----:|-------:|----------|",
    ]
    for domain in summary.domains:
        outstanding = ", ".join(domain.pending_tools) if domain.pending_tools else "-"
        coverage = 0.0 if domain.total_count == 0 else domain.implemented_count / domain.total_count * 100
        lines.append(
            f"| {_escape_cell(domain.domain_zh)} | {domain.implemented_count} | {domain.total_count} | {coverage:.0f}% | {_escape_cell(outstanding)} |"
        )

    lines.extend(
        [
            "",
            "## 來源文件",
            "",
            "- [生成工具目錄](CALCULATOR_CATALOG.zh-TW.md)" if audience == "docs" else "- [網站版計算器總覽](calculators.md)",
            "- [2023-2025 詳細指引整理](GUIDELINE_RECOMMENDED_TOOLS_2023_2025.md)" if audience == "docs" else "- [2023-2025 詳細指引整理](../../docs/GUIDELINE_RECOMMENDED_TOOLS_2023_2025.md)",
            "- [2020-2025 歷史整理](GUIDELINE_RECOMMENDED_TOOLS_2020_2025.md)" if audience == "docs" else "- [2020-2025 歷史整理](../../docs/GUIDELINE_RECOMMENDED_TOOLS_2020_2025.md)",
            "",
        ]
    )
    return "\n".join(lines)


def render_readme_catalog_overview(locale: str) -> str:
    entries = collect_entries()
    by_specialty = collect_by_specialty(entries)
    top_specialties = sorted(by_specialty.items(), key=lambda item: (-len(item[1]), _specialty_labels(item[0])[0]))[:6]
    specialty_count = len(by_specialty)
    calculator_count = len(entries)

    if locale == "en":
        lines = [
            "This README no longer carries a hand-maintained calculator inventory. The same generated source now feeds repository docs and MkDocs pages.",
            "",
            f"**Registry Snapshot**: {calculator_count} calculators across {specialty_count} specialties",
            "",
            "- [Full calculator catalog](docs/CALCULATOR_CATALOG.md)",
            "- [Traditional Chinese catalog](docs/CALCULATOR_CATALOG.zh-TW.md)",
            "- [Website calculator catalog](docs_site/calculators/index.md)",
            "- [網站版繁中總覽](docs_site/zh-tw/calculators.md)",
            "- Regenerate locally with `uv run python scripts/generate_tool_catalog_docs.py`",
            "",
            "| Specialty | Tools |",
            "|-----------|------:|",
        ]
        for specialty_key, specialty_entries in top_specialties:
            specialty_label, _ = _specialty_labels(specialty_key)
            lines.append(f"| {_escape_cell(specialty_label)} | {len(specialty_entries)} |")
        lines.extend(["", "You can still inspect the live registry via `python scripts/count_tools.py`, `calculator://list`, or `list_calculators()` from your MCP client."])
        return "\n".join(lines)

    lines = [
        "此 README 不再內嵌手動維護的完整工具清單；repository docs 與網站版都改由同一生成來源輸出。",
        "",
        f"**Registry Snapshot**: {calculator_count} 個計算器，涵蓋 {specialty_count} 個專科",
        "",
        "- [完整工具目錄](docs/CALCULATOR_CATALOG.zh-TW.md)",
        "- [English catalog](docs/CALCULATOR_CATALOG.md)",
        "- [網站版計算器總覽](docs_site/zh-tw/calculators.md)",
        "- [Website calculator catalog](docs_site/calculators/index.md)",
        "- 本機重新產生：`uv run python scripts/generate_tool_catalog_docs.py`",
        "",
        "| 專科 | 工具數 |",
        "|------|------:|",
    ]
    for specialty_key, specialty_entries in top_specialties:
        _, specialty_label = _specialty_labels(specialty_key)
        lines.append(f"| {_escape_cell(specialty_label)} | {len(specialty_entries)} |")
    lines.extend(["", "如需直接檢視 live registry，也可執行 `python scripts/count_tools.py`、讀取 `calculator://list`，或在 MCP client 呼叫 `list_calculators()`。"])
    return "\n".join(lines)


def render_readme_guideline_overview(locale: str) -> str:
    summary = parse_guideline_summary()

    if locale == "en":
        lines = [
            "We systematically map our calculators to major clinical guideline reviews, and this overview is generated from the same source used by the docs and website.",
            "",
            f"Tracked coverage: **{summary.implemented_count}/{summary.total_count}** recommended tools across **{len(summary.domains)}** domains.",
            "",
            "- [Generated guideline coverage summary](docs/GUIDELINE_COVERAGE_SUMMARY.md)",
            "- [Website guideline coverage page](docs_site/development/guideline-coverage.md)",
            "- [2023-2025 detailed guideline review](docs/GUIDELINE_RECOMMENDED_TOOLS_2023_2025.md)",
            "- [2020-2025 historical guideline review](docs/GUIDELINE_RECOMMENDED_TOOLS_2020_2025.md)",
            "",
            "| Domain | Implemented | Total | Coverage |",
            "|--------|------------:|------:|---------:|",
        ]
        for domain in summary.domains:
            coverage = 0.0 if domain.total_count == 0 else domain.implemented_count / domain.total_count * 100
            lines.append(f"| {_escape_cell(domain.domain_en)} | {domain.implemented_count} | {domain.total_count} | {coverage:.0f}% |")
        return "\n".join(lines)

    lines = [
        "### 📋 指引對齊概覽",
        "",
        "這份摘要由與 docs / docs_site 相同的生成來源輸出，不再手動維護。",
        "",
        f"目前追蹤 **{summary.implemented_count}/{summary.total_count}** 個指引建議工具，涵蓋 **{len(summary.domains)}** 個臨床領域。",
        "",
        "- [指引覆蓋摘要](docs/GUIDELINE_COVERAGE_SUMMARY.zh-TW.md)",
        "- [網站版指引摘要](docs_site/zh-tw/guideline-coverage.md)",
        "- [2023-2025 詳細指引整理](docs/GUIDELINE_RECOMMENDED_TOOLS_2023_2025.md)",
        "- [2020-2025 歷史整理](docs/GUIDELINE_RECOMMENDED_TOOLS_2020_2025.md)",
        "",
        "| 領域 | 已實作 | 總數 | 覆蓋率 |",
        "|------|-------:|-----:|-------:|",
    ]
    for domain in summary.domains:
        coverage = 0.0 if domain.total_count == 0 else domain.implemented_count / domain.total_count * 100
        lines.append(f"| {_escape_cell(domain.domain_zh)} | {domain.implemented_count} | {domain.total_count} | {coverage:.0f}% |")
    return "\n".join(lines)


def replace_generated_section_text(text: str, path: Path, start_marker: str, end_marker: str, content: str) -> str:
    pattern = re.compile(rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
    replacement = f"{start_marker}\n{content.strip()}\n{end_marker}"
    updated, count = pattern.subn(replacement, text)
    if count != 1:
        raise RuntimeError(f"Could not replace generated section in {path.relative_to(PROJECT_ROOT)}")
    return updated


def render_outputs() -> dict[Path, str]:
    outputs: dict[Path, str] = {}

    for (audience, locale), output_path in CATALOG_OUTPUTS.items():
        outputs[output_path] = render_catalog(locale, audience)

    for (audience, locale), output_path in GUIDELINE_OUTPUTS.items():
        outputs[output_path] = render_guideline_summary(locale, audience)

    english_readme = README_OUTPUTS["en"].read_text(encoding="utf-8")
    english_readme = replace_generated_section_text(
        english_readme,
        README_OUTPUTS["en"],
        CATALOG_MARKERS["en"][0],
        CATALOG_MARKERS["en"][1],
        render_readme_catalog_overview("en"),
    )
    english_readme = replace_generated_section_text(
        english_readme,
        README_OUTPUTS["en"],
        GUIDELINE_MARKERS["en"][0],
        GUIDELINE_MARKERS["en"][1],
        render_readme_guideline_overview("en"),
    )
    outputs[README_OUTPUTS["en"]] = english_readme

    zh_readme = README_OUTPUTS["zh-TW"].read_text(encoding="utf-8")
    zh_readme = replace_generated_section_text(
        zh_readme,
        README_OUTPUTS["zh-TW"],
        CATALOG_MARKERS["zh-TW"][0],
        CATALOG_MARKERS["zh-TW"][1],
        render_readme_catalog_overview("zh-TW"),
    )
    zh_readme = replace_generated_section_text(
        zh_readme,
        README_OUTPUTS["zh-TW"],
        GUIDELINE_MARKERS["zh-TW"][0],
        GUIDELINE_MARKERS["zh-TW"][1],
        render_readme_guideline_overview("zh-TW"),
    )
    outputs[README_OUTPUTS["zh-TW"]] = zh_readme

    return outputs


def write_outputs() -> None:
    for output_path, rendered in render_outputs().items():
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")


def check_outputs() -> list[Path]:
    stale_files: list[Path] = []
    for output_path, rendered in render_outputs().items():
        if not output_path.exists() or output_path.read_text(encoding="utf-8") != rendered:
            stale_files.append(output_path)
    return stale_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if generated catalog and guideline docs are missing or stale.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check:
        stale_files = check_outputs()
        if stale_files:
            print("Generated catalog/guideline docs are stale:")
            for path in stale_files:
                print(f"- {path.relative_to(PROJECT_ROOT)}")
            return 1
        print("Generated catalog/guideline docs are up to date.")
        return 0

    write_outputs()
    for output_path in render_outputs():
        print(f"Wrote {output_path.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
