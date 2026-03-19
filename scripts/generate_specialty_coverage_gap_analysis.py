#!/usr/bin/env python
"""Generate a live specialty coverage gap analysis from the registry."""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass

from src.domain.registry import ToolRegistry
from src.domain.services.calculators import CALCULATORS
from src.domain.value_objects.tool_keys import Specialty
from src.shared.project_metadata import PROJECT_ROOT, get_project_version

OUTPUT_PATH = PROJECT_ROOT / "docs/SPECIALTY_COVERAGE_GAP_ANALYSIS.md"
GUIDELINE_SUMMARY_PATH = PROJECT_ROOT / "docs/GUIDELINE_COVERAGE_SUMMARY.md"


@dataclass(frozen=True)
class SpecialtyCoverage:
    specialty: Specialty
    tool_ids: tuple[str, ...]

    @property
    def count(self) -> int:
        return len(self.tool_ids)


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    for calculator_class in CALCULATORS:
        registry.register(calculator_class())
    return registry


def collect_specialty_coverage(registry: ToolRegistry) -> list[SpecialtyCoverage]:
    tools_by_specialty: dict[Specialty, set[str]] = defaultdict(set)

    for metadata in registry.list_all():
        for specialty in metadata.high_level.specialties:
            tools_by_specialty[specialty].add(metadata.low_level.tool_id)

    return [
        SpecialtyCoverage(
            specialty=specialty,
            tool_ids=tuple(sorted(tools_by_specialty.get(specialty, set()))),
        )
        for specialty in Specialty
    ]


def _specialty_label(specialty: Specialty) -> str:
    return specialty.value.replace("_", " ").title()


def _bucket_name(count: int) -> str:
    if count == 0:
        return "uncovered"
    if count <= 2:
        return "thin"
    if count <= 4:
        return "developing"
    return "established"


def _load_guideline_summary_line() -> str:
    for line in GUIDELINE_SUMMARY_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("Current coverage tracks **"):
            return line.strip()
    return "Current guideline summary not found."


def render_report(coverage_rows: list[SpecialtyCoverage]) -> str:
    version = get_project_version()
    total_specialties = len(coverage_rows)
    covered_rows = [row for row in coverage_rows if row.count > 0]
    uncovered_rows = [row for row in coverage_rows if row.count == 0]
    thin_rows = [row for row in coverage_rows if 1 <= row.count <= 2]
    developing_rows = [row for row in coverage_rows if 3 <= row.count <= 4]
    established_rows = [row for row in coverage_rows if row.count >= 5]
    guideline_line = _load_guideline_summary_line()

    lines = [
        "# Specialty Coverage Gap Analysis",
        "",
        "> Generated from the live calculator registry. Do not edit manually.",
        f"> Regenerate with `uv run python scripts/generate_specialty_coverage_gap_analysis.py` (v{version}).",
        "",
        "## Current Status",
        "",
        f"- Specialty enum total: {total_specialties}",
        f"- Specialties with at least one calculator: {len(covered_rows)}",
        f"- Specialties with no calculators: {len(uncovered_rows)}",
        f"- Established coverage (>=5 tools): {len(established_rows)}",
        f"- Developing coverage (3-4 tools): {len(developing_rows)}",
        f"- Thin coverage (1-2 tools): {len(thin_rows)}",
        f"- {guideline_line}",
        "",
        "## Interpretation",
        "",
        "- This report measures breadth across specialty labels, not just guideline-recommended tools.",
        "- The guideline program is currently complete, but broad specialty coverage is not.",
        "- Several specialties from older planning notes are now implemented and should no longer be treated as missing.",
        "",
        "## Established Coverage",
        "",
        "| Specialty | Tool Count | Example Tool IDs |",
        "|-----------|-----------:|------------------|",
    ]

    for row in sorted(established_rows, key=lambda item: (-item.count, item.specialty.value)):
        sample = ", ".join(row.tool_ids[:5])
        lines.append(f"| {_specialty_label(row.specialty)} | {row.count} | {sample} |")

    lines.extend([
        "",
        "## Developing Coverage",
        "",
        "| Specialty | Tool Count | Tool IDs |",
        "|-----------|-----------:|----------|",
    ])

    for row in sorted(developing_rows, key=lambda item: (-item.count, item.specialty.value)):
        lines.append(f"| {_specialty_label(row.specialty)} | {row.count} | {', '.join(row.tool_ids)} |")

    lines.extend([
        "",
        "## Thin Coverage",
        "",
        "| Specialty | Tool Count | Tool IDs |",
        "|-----------|-----------:|----------|",
    ])

    for row in sorted(thin_rows, key=lambda item: (item.count, item.specialty.value)):
        lines.append(f"| {_specialty_label(row.specialty)} | {row.count} | {', '.join(row.tool_ids)} |")

    lines.extend([
        "",
        "## Uncovered Specialties",
        "",
        "These specialty enums currently have zero calculators mapped to them and are the primary candidates for future PubMed/guideline expansion.",
        "",
        "| Specialty | Coverage Bucket |",
        "|-----------|-----------------|",
    ])

    for row in sorted(uncovered_rows, key=lambda item: item.specialty.value):
        lines.append(f"| {_specialty_label(row.specialty)} | {_bucket_name(row.count)} |")

    lines.extend([
        "",
        "## Recommended Next Pass",
        "",
        "1. Prioritize uncovered primary specialties before subspecialties that mostly re-label existing internal medicine or surgery tools.",
        "2. For each target specialty, confirm a stable, literature-backed score with clear clinical adoption before implementation.",
        "3. Add PubMed/guideline evidence, tests, MCP handler wiring, and provenance metadata together as one unit.",
        "4. Regenerate this report after each batch so the backlog stays live instead of drifting.",
        "",
        "## Priority Research Queue",
        "",
        "The following uncovered specialties are likely higher-yield than niche subspecialties and should be researched first:",
        "",
        "- Palliative Care",
        "- Dentistry",
        "- Public Health",
        "- Preventive Medicine",
        "- Sleep Medicine",
        "- Pathology",
        "- Nuclear Medicine",
        "- Cardiac Surgery",
        "- Thoracic Surgery",
        "- Vascular Surgery",
    ])

    return "\n".join(lines) + "\n"


def main() -> None:
    registry = build_registry()
    coverage_rows = collect_specialty_coverage(registry)
    OUTPUT_PATH.write_text(render_report(coverage_rows), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the generated specialty coverage report is missing or stale.",
    )
    return parser.parse_args()


def is_current() -> bool:
    registry = build_registry()
    coverage_rows = collect_specialty_coverage(registry)
    rendered = render_report(coverage_rows)
    return OUTPUT_PATH.exists() and OUTPUT_PATH.read_text(encoding="utf-8") == rendered


if __name__ == "__main__":
    args = parse_args()
    if args.check:
        if is_current():
            print("Generated specialty coverage analysis is up to date.")
            raise SystemExit(0)
        print("Generated specialty coverage analysis is stale. Run `uv run python scripts/generate_specialty_coverage_gap_analysis.py` to refresh it.")
        raise SystemExit(1)
    main()
