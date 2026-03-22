#!/usr/bin/env python
"""Build a coverage audit for benchmark datasets and the active workflow benchmark."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, cast

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.domain.registry import ToolRegistry  # noqa: E402
from src.domain.services.calculators import CALCULATORS  # noqa: E402
from src.shared.agent_benchmarking import load_agent_scenarios_from_paths  # noqa: E402
from src.shared.hf_benchmark_dataset import load_hf_benchmark_cases  # noqa: E402

GUIDELINE_DOMAIN_LABELS = {
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


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    for calculator_class in CALCULATORS:
        registry.register(calculator_class())
    return registry


def parse_guideline_tool_domains() -> dict[str, tuple[str, ...]]:
    doc_path = PROJECT_ROOT / "docs" / "GUIDELINE_RECOMMENDED_TOOLS_2023_2025.md"
    lines = doc_path.read_text(encoding="utf-8").splitlines()
    in_summary = False
    domain_map: dict[str, set[str]] = defaultdict(set)
    alias_map = {
        "SOFA": "sofa_score",
        "SOFA-2": "sofa2_score",
        "qSOFA": "qsofa_score",
        "NEWS2": "news_score",
        "APACHE II": "apache_ii",
        "RASS": "rass",
        "CAM-ICU": "cam_icu",
        "ICDSC": "icdsc",
        "NUTRIC": "nutric_score",
        "CHA₂DS₂-VASc": "chads2_vasc",
        "CHA₂DS₂-VA": "chads2_va",
        "HAS-BLED": "has_bled",
        "HEART": "heart_score",
        "GRACE": "grace_score",
        "TIMI": "timi_stemi",
        "EuroSCORE II": "euroscore_ii",
        "HFA-PEFF": "hfa_peff",
        "SCORE2": "score2",
        "Rockall": "rockall_score",
        "Glasgow-Blatchford": "glasgow_blatchford",
        "AIMS65": "aims65",
        "Child-Pugh": "child_pugh",
        "MELD": "meld_score",
        "MELD-Na": "meld_score",
        "FIB-4": "fib4_index",
        "Maddrey DF": "maddrey_df",
        "Lille Model": "lille_model",
        "KDIGO AKI": "kdigo_aki",
        "CKD-EPI 2021": "ckd_epi_2021",
        "CURB-65": "curb65",
        "PSI/PORT": "psi_port",
        "ROX Index": "rox_index",
        "P/F Ratio": "pf_ratio",
        "Murray Score": "murray_lung_injury_score",
        "Wells DVT": "wells_dvt",
        "Wells PE": "wells_pe",
        "Caprini VTE": "caprini_vte",
        "sPESI": "spesi",
        "GCS": "glasgow_coma_scale",
        "NIHSS": "nihss",
        "mRS": "modified_rankin_scale",
        "ABCD2": "abcd2",
        "Hunt & Hess": "hunt_hess",
        "Fisher": "fisher_grade",
        "4AT": "four_at",
        "ASA": "asa_physical_status",
        "RCRI": "rcri",
        "Mallampati": "mallampati_score",
        "STOP-BANG": "stop_bang",
        "Apfel": "apfel_ponv",
        "Aldrete": "aldrete_score",
        "ISS": "iss",
        "RTS": "rts",
        "TRISS": "triss",
        "Parkland": "parkland_formula",
        "TBSA": "tbsa",
        "PEWS": "pews",
        "pSOFA (Phoenix 2024)": "pediatric_sofa",
        "ECOG PS": "ecog_performance_status",
        "Karnofsky": "karnofsky_performance_scale",
        "NRS-2002": "nrs_2002",
        "DAS28": "das28",
        "FRAX": "frax",
    }

    for line in lines:
        if line.startswith("## 📊 整體對照摘要"):
            in_summary = True
            continue
        if not in_summary:
            continue
        if in_summary and domain_map and not line.lstrip().startswith("|"):
            break
        if not line.lstrip().startswith("|"):
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) < 5:
            continue
        domain_zh = parts[1]
        if domain_zh in {"", "領域"} or set(domain_zh) == {"-"}:
            continue
        domain_en = GUIDELINE_DOMAIN_LABELS.get(domain_zh, domain_zh)
        for raw_tool in [item.strip().strip("`*") for item in parts[2].split(",")]:
            tool_id = alias_map.get(raw_tool)
            if tool_id is not None:
                domain_map[tool_id].add(domain_en)
    return {tool_id: tuple(sorted(domains)) for tool_id, domains in domain_map.items()}


def render_markdown(payload: dict[str, Any]) -> str:
    baseline = cast(dict[str, Any], payload["baseline_workflow_benchmark"])
    expanded = cast(dict[str, Any], payload["expanded_hf_dataset"])
    lines = [
        "# Benchmark Coverage Audit",
        "",
        "## Baseline Workflow Benchmark",
        "",
        f"- Scenario count: {baseline['scenario_count']}",
        f"- Unique tools: {baseline['unique_tools']}",
        f"- Guideline domains covered: {baseline['guideline_domains_covered']}/{baseline['guideline_domain_total']}",
        f"- Missing guideline domains: {', '.join(baseline['missing_guideline_domains']) if baseline['missing_guideline_domains'] else '-'}",
        "",
        "## Expanded HF Dataset",
        "",
        f"- Total cases: {expanded['total_cases']}",
        f"- Unique tools: {expanded['unique_tools']}",
        f"- Unique primary specialties: {expanded['unique_primary_specialties']}",
        f"- Guideline domains covered: {expanded['guideline_domains_covered']}/{expanded['guideline_domain_total']}",
        f"- Missing guideline domains: {', '.join(expanded['missing_guideline_domains']) if expanded['missing_guideline_domains'] else '-'}",
        "",
        "### Split Counts",
        "",
        "| Split | Cases |",
        "| --- | ---: |",
    ]
    for split_name, count in cast(dict[str, Any], expanded["split_counts"]).items():
        lines.append(f"| {split_name} | {count} |")
    lines.extend(["", "### Guideline Domain Counts", "", "| Domain | Cases |", "| --- | ---: |"])
    for domain, count in cast(dict[str, Any], expanded["guideline_domain_counts"]).items():
        lines.append(f"| {domain} | {count} |")
    lines.extend(["", "### Coverage Verdict", ""])
    verdict = "PASS" if not expanded["missing_guideline_domains"] and int(expanded["total_cases"]) >= 500 else "FAIL"
    lines.append(f"- Dataset release readiness: {verdict}")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build benchmark coverage audit report")
    parser.add_argument(
        "--dataset",
        default=str(PROJECT_ROOT / "data" / "benchmarks" / "medical_calc_mcp_hf_v1" / "all.jsonl"),
        help="Path to the expanded HF dataset all.jsonl file.",
    )
    parser.add_argument(
        "--workflow-scenarios",
        nargs="+",
        default=[
            str(PROJECT_ROOT / "data" / "agent_decision_bench" / "scenarios" / "sepsis_icu.jsonl"),
            str(PROJECT_ROOT / "data" / "agent_decision_bench" / "scenarios" / "preop_risk.jsonl"),
            str(PROJECT_ROOT / "data" / "agent_decision_bench" / "scenarios" / "aki_eval.jsonl"),
            str(PROJECT_ROOT / "data" / "agent_decision_bench" / "scenarios" / "gi_bleed.jsonl"),
            str(PROJECT_ROOT / "data" / "agent_decision_bench" / "scenarios" / "icu_sedation_delirium.jsonl"),
        ],
        help="Scenario JSONL files for the active workflow benchmark.",
    )
    parser.add_argument(
        "--markdown-out",
        default=str(PROJECT_ROOT / "docs" / "BENCHMARK_COVERAGE_AUDIT.md"),
        help="Output path for markdown audit report.",
    )
    parser.add_argument(
        "--json-out",
        default=str(PROJECT_ROOT / "data" / "benchmarks" / "medical_calc_mcp_hf_v1" / "coverage_audit.json"),
        help="Output path for JSON audit summary.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    registry = build_registry()
    domain_map = parse_guideline_tool_domains()
    required_domains = set(GUIDELINE_DOMAIN_LABELS.values())

    workflow_scenarios = load_agent_scenarios_from_paths(args.workflow_scenarios)
    workflow_tools = {tool_id for scenario in workflow_scenarios for tool_id in scenario.expected_tools}
    workflow_domains = {domain for tool_id in workflow_tools for domain in domain_map.get(tool_id, ())}

    cases = load_hf_benchmark_cases(args.dataset)
    case_domains = Counter(domain for case in cases for domain in case.guideline_domains)
    split_counts = Counter(case.split for case in cases)
    payload = {
        "registry": {
            "total_tools": len(registry.list_all_ids()),
            "total_primary_specialties": len({(metadata.high_level.specialties[0].value if metadata.high_level.specialties else "other") for metadata in registry.list_all()}),
        },
        "baseline_workflow_benchmark": {
            "scenario_count": len(workflow_scenarios),
            "unique_tools": len(workflow_tools),
            "guideline_domains_covered": len(workflow_domains),
            "guideline_domain_total": len(required_domains),
            "missing_guideline_domains": sorted(required_domains - workflow_domains),
        },
        "expanded_hf_dataset": {
            "total_cases": len(cases),
            "unique_tools": len({case.tool_id for case in cases}),
            "unique_primary_specialties": len({case.primary_specialty for case in cases}),
            "guideline_domains_covered": len(case_domains),
            "guideline_domain_total": len(required_domains),
            "missing_guideline_domains": sorted(required_domains - set(case_domains)),
            "split_counts": dict(sorted(split_counts.items())),
            "guideline_domain_counts": dict(sorted(case_domains.items())),
        },
    }

    markdown = render_markdown(payload)
    markdown_path = Path(args.markdown_out)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(markdown, encoding="utf-8")

    json_path = Path(args.json_out)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(markdown)
    print(f"Wrote markdown audit to {markdown_path}")
    print(f"Wrote JSON audit to {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
