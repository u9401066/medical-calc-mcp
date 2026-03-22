#!/usr/bin/env python
"""Run one benchmark profile from the versioned profile manifest."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.shared.agent_benchmark_evaluator import (  # noqa: E402
    evaluate_agent_runs,
    format_evaluation_summary,
    load_agent_runs,
    load_scoring_rubric,
    write_evaluation_summary_json,
)
from src.shared.agent_benchmark_profiles import (  # noqa: E402
    get_benchmark_profile,
    load_benchmark_profile_manifest,
)
from src.shared.agent_benchmark_trace_adapter import (  # noqa: E402
    TraceFormat,
    adapt_trace_entries_to_runs,
    format_trace_adaptation_result,
    load_session_mapping,
    load_trace_entries,
    write_adapted_runs_jsonl,
    write_trace_adaptation_summary_json,
)
from src.shared.agent_benchmarking import load_agent_scenarios_from_paths  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a versioned benchmark profile from the profile manifest")
    parser.add_argument(
        "--manifest",
        default=str(PROJECT_ROOT / "data" / "agent_decision_bench" / "profiles" / "manifest.json"),
        help="Path to the benchmark profile manifest JSON file.",
    )
    parser.add_argument("--profile-id", required=True, help="Benchmark profile id to execute.")
    parser.add_argument("--output-dir", required=True, help="Directory to write generated benchmark artifacts.")
    return parser


def _resolve_project_path(path_value: str) -> Path:
    candidate = Path(path_value)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate


def main() -> int:
    args = build_parser().parse_args()
    manifest = load_benchmark_profile_manifest(args.manifest)
    profile = get_benchmark_profile(manifest, args.profile_id)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scenario_paths = cast(
        list[str | Path],
        [_resolve_project_path(path_value) for path_value in manifest.scenarios],
    )
    rubric_path = _resolve_project_path(manifest.rubric)
    scenarios = load_agent_scenarios_from_paths(scenario_paths)
    rubric = load_scoring_rubric(rubric_path)

    trace_adaptation_payload: dict[str, Any] | None = None
    if profile.run_source.source_type == "direct_runs":
        runs = load_agent_runs(_resolve_project_path(profile.run_source.path))
    elif profile.run_source.source_type == "trace":
        session_mapping = (
            load_session_mapping(_resolve_project_path(profile.run_source.session_mapping))
            if profile.run_source.session_mapping
            else None
        )
        entries = load_trace_entries(
            _resolve_project_path(profile.run_source.path),
            trace_format=cast(TraceFormat, profile.run_source.trace_format),
        )
        adaptation = adapt_trace_entries_to_runs(entries, scenarios, session_mapping=session_mapping)
        adapted_runs_path = output_dir / f"adapted-runs-{profile.profile_id}.jsonl"
        adaptation_summary_path = output_dir / f"trace-adaptation-{profile.profile_id}.json"
        write_adapted_runs_jsonl(adaptation.adapted_runs, adapted_runs_path)
        write_trace_adaptation_summary_json(adaptation, adaptation_summary_path)
        print(format_trace_adaptation_result(adaptation))
        print(f"Wrote adapted runs to {adapted_runs_path}")
        runs = list(adaptation.adapted_runs)
        trace_adaptation_payload = {
            "summary_path": adaptation_summary_path.name,
            "adapted_runs_path": adapted_runs_path.name,
            "summary": adaptation.to_dict(),
        }
    else:
        raise ValueError(f"Unsupported run_source.source_type: {profile.run_source.source_type}")

    summary = evaluate_agent_runs(scenarios, runs, rubric=rubric)
    summary_path = output_dir / f"benchmark-summary-{profile.profile_id}.json"
    write_evaluation_summary_json(summary, summary_path)
    print(format_evaluation_summary(summary))
    print(f"Wrote evaluation summary to {summary_path}")

    bundle_path = output_dir / f"profile-result-{profile.profile_id}.json"
    bundle_payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "manifest_version": manifest.version,
        "profile": profile.to_dict(),
        "summary": summary.to_dict(),
        "summary_path": summary_path.name,
        "trace_adaptation": trace_adaptation_payload,
    }
    bundle_path.write_text(json.dumps(bundle_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote profile bundle to {bundle_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
