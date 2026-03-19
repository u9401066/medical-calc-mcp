#!/usr/bin/env python
"""Validate that implementation, references, guideline docs, and key docs stay aligned."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from src.infrastructure.mcp.server import MedicalCalculatorServer
from src.shared.formula_provenance import validate_formula_provenance_manifest, validate_reference_metadata
from src.shared.project_metadata import PROJECT_ROOT, get_project_version

IMPLEMENTED_GUIDELINE_TOOL_ALIASES: dict[str, str] = {
    "ABCD2": "abcd2",
    "ACEF II": "acef_ii",
    "AIMS65": "aims65",
    "APACHE II": "apache_ii",
    "ASA Physical Status": "asa_physical_status",
    "Aldrete Score": "aldrete_score",
    "Apfel Score": "apfel_ponv",
    "CAM-ICU": "cam_icu",
    "CHA₂DS₂-VA": "chads2_va",
    "CHA₂DS₂-VASc": "chads2_vasc",
    "CKD-EPI 2021": "ckd_epi_2021",
    "CURB-65": "curb65",
    "Caprini VTE": "caprini_vte",
    "Child-Pugh": "child_pugh",
    "EuroSCORE II": "euroscore_ii",
    "FIB-4": "fib4_index",
    "Fisher Grade": "fisher_grade",
    "GCS": "glasgow_coma_scale",
    "GRACE Score": "grace_score",
    "Glasgow-Blatchford": "glasgow_blatchford",
    "Glasgow-Blatchford GBS": "glasgow_blatchford",
    "Glasgow-Blatchford Score": "glasgow_blatchford",
    "Glasgow-Blatchford GBS Score": "glasgow_blatchford",
    "HAS-BLED": "has_bled",
    "HEART Score": "heart_score",
    "Hunt & Hess": "hunt_hess",
    "Hunt Hess": "hunt_hess",
    "IBW TV": "ideal_body_weight",
    "ISS": "iss",
    "KDIGO AKI": "kdigo_aki",
    "Lille Model": "lille_model",
    "MELD": "meld_score",
    "MELD-Na": "meld_score",
    "Mallampati": "mallampati_score",
    "Maddrey DF": "maddrey_df",
    "NIHSS": "nihss",
    "NEWS2": "news2_score",
    "PEWS": "pews",
    "PEWS Brighton": "pews",
    "P F Ratio": "pf_ratio",
    "PF Ratio": "pf_ratio",
    "PSI PORT": "psi_port",
    "Parkland Formula": "parkland_formula",
    "Phoenix Sepsis Score": "pediatric_sofa",
    "Phoenix Sepsis Score pSOFA": "pediatric_sofa",
    "Pitt Bacteremia": "pitt_bacteremia",
    "Pittsburgh Bacteremia": "pitt_bacteremia",
    "QSOFA": "qsofa_score",
    "RASS": "rass",
    "RCRI": "rcri",
    "ROX Index": "rox_index",
    "RTS": "rts",
    "Rockall Score": "rockall_score",
    "SOFA": "sofa_score",
    "SOFA-2": "sofa2_score",
    "STOP-BANG": "stop_bang",
    "TBSA": "tbsa",
    "TIMI STEMI": "timi_stemi",
    "TRISS": "triss",
    "Wells DVT": "wells_dvt",
    "Wells PE": "wells_pe",
    "mRS": "modified_rankin_scale",
    "pSOFA": "pediatric_sofa",
    "qSOFA": "qsofa_score",
    "sPESI": "spesi",
}

DOC_EXPECTATIONS: dict[str, list[str]] = {
    "README.md": [
        "Registry Snapshot**: 151 calculators across 31 specialties",
        "### Generated calculator catalog",
    ],
    "README.zh-TW.md": [
        "Registry Snapshot**: 151 個計算器，涵蓋 31 個專科",
        "### 自動生成工具目錄",
    ],
    "docs_site/index.md": [
        "151 Validated Medical Calculators for AI Agents",
        "provides **151 validated medical calculators**",
        "**151 Clinical Calculators**",
    ],
    "docs_site/development/roadmap.md": [
        "- ✅ 151 Medical Calculators",
    ],
}

GUIDELINE_DOCS = [
    "docs/GUIDELINE_RECOMMENDED_TOOLS_2020_2025.md",
    "docs/GUIDELINE_RECOMMENDED_TOOLS_2023_2025.md",
]

GENERATED_CATALOG_DOCS = [
    "docs/CALCULATOR_CATALOG.md",
    "docs/CALCULATOR_CATALOG.zh-TW.md",
    "docs/GUIDELINE_COVERAGE_SUMMARY.md",
    "docs/GUIDELINE_COVERAGE_SUMMARY.zh-TW.md",
    "docs_site/calculators/index.md",
    "docs_site/zh-tw/calculators.md",
    "docs_site/development/guideline-coverage.md",
    "docs_site/zh-tw/guideline-coverage.md",
]

GENERATED_OPENAPI_DOCS = [
    "docs_site/api/openapi.json",
]

GENERATED_REST_API_DOCS = [
    "docs_site/api/rest-api.md",
]

GENERATED_SPECIALTY_COVERAGE_DOCS = [
    "docs/SPECIALTY_COVERAGE_GAP_ANALYSIS.md",
]


@dataclass(frozen=True)
class RegistryStats:
    calculator_count: int
    specialty_count: int
    total_references: int
    unique_pmids: int
    unique_dois: int
    tools_without_references: tuple[str, ...]


def collect_registry_stats() -> tuple[RegistryStats, set[str]]:
    """Collect implementation-level stats from the calculator registry."""
    server = MedicalCalculatorServer()
    tools = server.registry.list_all()
    specialties = {
        (meta.high_level.specialties[0].value if meta.high_level.specialties else "Other")
        for meta in tools
    }
    unique_pmids = {
        ref.pmid
        for meta in tools
        for ref in meta.references
        if ref.pmid
    }
    unique_dois = {
        ref.doi
        for meta in tools
        for ref in meta.references
        if ref.doi
    }
    tools_without_references = tuple(
        sorted(meta.low_level.tool_id for meta in tools if not meta.references)
    )
    stats = RegistryStats(
        calculator_count=len(tools),
        specialty_count=len(specialties),
        total_references=sum(len(meta.references) for meta in tools),
        unique_pmids=len(unique_pmids),
        unique_dois=len(unique_dois),
        tools_without_references=tools_without_references,
    )
    tool_ids = {meta.low_level.tool_id for meta in tools}
    return stats, tool_ids


def validate_reference_provenance() -> list[str]:
    """Ensure every calculator has provenance metadata and valid reference identifiers."""
    server = MedicalCalculatorServer()
    tools = server.registry.list_all()
    tool_ids = {meta.low_level.tool_id for meta in tools}
    issues = validate_formula_provenance_manifest(tool_ids)

    for meta in tools:
        tool_id = meta.low_level.tool_id
        if not meta.formula_source_type:
            issues.append(f"{tool_id}: missing formula_source_type manifest entry")
        if not meta.references:
            issues.append(f"{tool_id}: no references present")
            continue
        if not any(ref.pmid or ref.doi for ref in meta.references):
            issues.append(f"{tool_id}: references exist but none include PMID or DOI")
        for index, ref in enumerate(meta.references, start=1):
            issues.extend(validate_reference_metadata(ref, context=f"{tool_id} reference #{index}"))

    return issues


def normalize_guideline_label(label: str) -> str:
    """Normalize a guideline table label into an alias lookup key."""
    cleaned = re.sub(r"`", "", label)
    cleaned = re.sub(r"\*", "", cleaned)
    cleaned = cleaned.replace("（", "(").replace("）", ")")
    cleaned = re.sub(r"\([^)]*\)", "", cleaned)
    cleaned = cleaned.replace("/", " ")
    cleaned = cleaned.replace("-", "-")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def iter_guideline_rows(path: Path) -> Iterable[tuple[int, str]]:
    """Yield implemented guideline labels from markdown tables."""
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if "✅" not in line or not line.lstrip().startswith("|"):
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) < 4:
            continue
        raw_label = parts[1]
        status_cell = parts[3]
        if not raw_label or raw_label == "領域" or "**" not in raw_label or "已實作" not in status_cell:
            continue
        yield line_number, normalize_guideline_label(raw_label)


def collect_test_count() -> int:
    """Count collected tests without executing them."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "--collect-only", "-q"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    combined_output = f"{result.stdout}\n{result.stderr}"
    match = re.search(r"(\d+) tests collected", combined_output)
    if result.returncode != 0 or match is None:
        raise RuntimeError(f"Unable to collect tests:\n{combined_output.strip()}")
    return int(match.group(1))


def validate_docs(stats: RegistryStats, version: str, check_tests: bool) -> list[str]:
    """Validate core documentation snapshots against implementation stats."""
    issues: list[str] = []

    if stats.calculator_count != 151:
        issues.append(f"Expected 151 calculators, found {stats.calculator_count}.")
    if stats.specialty_count != 31:
        issues.append(f"Expected 31 specialties, found {stats.specialty_count}.")
    if stats.unique_pmids != 286:
        issues.append(f"Expected 286 unique PMIDs, found {stats.unique_pmids}.")
    if stats.unique_dois != 244:
        issues.append(f"Expected 244 unique DOIs, found {stats.unique_dois}.")
    if stats.tools_without_references:
        issues.append(
            "Calculators without references: " + ", ".join(stats.tools_without_references)
        )

    expected_version_snippet = f"Current Status (v{version})"
    roadmap_text = (PROJECT_ROOT / "docs_site/development/roadmap.md").read_text(encoding="utf-8")
    if expected_version_snippet not in roadmap_text:
        issues.append(
            f"docs_site/development/roadmap.md is missing '{expected_version_snippet}'."
        )

    for relative_path, expected_snippets in DOC_EXPECTATIONS.items():
        text = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
        for snippet in expected_snippets:
            if snippet not in text:
                issues.append(f"{relative_path} is missing '{snippet}'.")

    if check_tests:
        collected_tests = collect_test_count()
        dynamic_expectations = {
            "README.md": f"Quality Snapshot**: {collected_tests} collected tests | 244 PMIDs | 205 DOIs | 100% citation coverage",
            "README.zh-TW.md": f"品質快照**: {collected_tests} 個已收集測試 | 244 個 PMID | 205 個 DOI | 100% 計算器具文獻引用",
            "docs_site/index.md": f"tests-{collected_tests}%20collected-brightgreen.svg",
            "docs_site/development/roadmap.md": f"- ✅ {collected_tests:,} Collected Tests",
        }
        for relative_path, snippet in dynamic_expectations.items():
            text = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
            if snippet not in text:
                issues.append(f"{relative_path} is missing '{snippet}'.")

    return issues


def validate_guideline_docs(tool_ids: set[str]) -> list[str]:
    """Ensure guideline docs only mark implemented tools that actually exist in the code."""
    issues: list[str] = []
    unknown_labels: Counter[str] = Counter()
    missing_tool_ids: Counter[str] = Counter()

    for relative_path in GUIDELINE_DOCS:
        path = PROJECT_ROOT / relative_path
        for line_number, label in iter_guideline_rows(path):
            tool_id = IMPLEMENTED_GUIDELINE_TOOL_ALIASES.get(label)
            if tool_id is None:
                unknown_labels[f"{relative_path}:{line_number}:{label}"] += 1
                continue
            if tool_id not in tool_ids:
                missing_tool_ids[f"{relative_path}:{line_number}:{label}->{tool_id}"] += 1

    issues.extend(f"Unmapped guideline label: {entry}" for entry in sorted(unknown_labels))
    issues.extend(f"Guideline row points to missing tool: {entry}" for entry in sorted(missing_tool_ids))
    return issues


def validate_generated_catalog_docs() -> list[str]:
    """Ensure generated catalog docs exist and match the current registry."""
    issues: list[str] = []

    for relative_path in GENERATED_CATALOG_DOCS:
        if not (PROJECT_ROOT / relative_path).exists():
            issues.append(f"Missing generated catalog doc: {relative_path}")

    result = subprocess.run(
        [sys.executable, "scripts/generate_tool_catalog_docs.py", "--check"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        issues.append(
            "Generated catalog docs are out of date. Run `uv run python scripts/generate_tool_catalog_docs.py`."
            + (f"\n{output}" if output else "")
        )

    return issues


def validate_generated_openapi_docs() -> list[str]:
    """Ensure generated OpenAPI docs exist and match the current REST API."""
    issues: list[str] = []

    for relative_path in GENERATED_OPENAPI_DOCS:
        if not (PROJECT_ROOT / relative_path).exists():
            issues.append(f"Missing generated OpenAPI doc: {relative_path}")

    result = subprocess.run(
        [sys.executable, "scripts/generate_openapi_spec.py", "--check"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        issues.append(
            "Generated OpenAPI docs are out of date. Run `uv run python scripts/generate_openapi_spec.py`."
            + (f"\n{output}" if output else "")
        )

    return issues


def validate_generated_rest_api_docs() -> list[str]:
    """Ensure generated REST API docs exist and match the current OpenAPI schema."""
    issues: list[str] = []

    for relative_path in GENERATED_REST_API_DOCS:
        if not (PROJECT_ROOT / relative_path).exists():
            issues.append(f"Missing generated REST API doc: {relative_path}")

    result = subprocess.run(
        [sys.executable, "scripts/generate_rest_api_docs.py", "--check"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        issues.append(
            "Generated REST API docs are out of date. Run `uv run python scripts/generate_rest_api_docs.py`."
            + (f"\n{output}" if output else "")
        )

    return issues


def validate_generated_specialty_coverage_docs() -> list[str]:
    """Ensure generated specialty coverage docs exist and match the live registry."""
    issues: list[str] = []

    for relative_path in GENERATED_SPECIALTY_COVERAGE_DOCS:
        if not (PROJECT_ROOT / relative_path).exists():
            issues.append(f"Missing generated specialty coverage doc: {relative_path}")

    result = subprocess.run(
        [sys.executable, "scripts/generate_specialty_coverage_gap_analysis.py", "--check"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        issues.append(
            "Generated specialty coverage docs are out of date. Run `uv run python scripts/generate_specialty_coverage_gap_analysis.py`."
            + (f"\n{output}" if output else "")
        )

    return issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-tests",
        action="store_true",
        help="Also collect pytest test counts and validate documentation test snapshots.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    stats, tool_ids = collect_registry_stats()
    version = get_project_version()
    collected_tests: int | None = collect_test_count() if args.check_tests else None

    issues = [
        *validate_docs(stats, version, check_tests=args.check_tests),
        *validate_guideline_docs(tool_ids),
        *validate_reference_provenance(),
        *validate_generated_catalog_docs(),
        *validate_generated_openapi_docs(),
        *validate_generated_rest_api_docs(),
        *validate_generated_specialty_coverage_docs(),
    ]

    if issues:
        print("Project consistency check failed:\n")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Project consistency check passed.")
    print(f"Version: {version}")
    print(
        "Calculators: "
        f"{stats.calculator_count} across {stats.specialty_count} specialties | "
        f"References: {stats.total_references} total ({stats.unique_pmids} PMIDs, {stats.unique_dois} DOIs)"
    )
    if collected_tests is not None:
        print(f"Tests: {collected_tests} collected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
