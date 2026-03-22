#!/usr/bin/env python
"""Evaluate agent workflow runs against workflow-native benchmark scenarios."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

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
from src.shared.agent_benchmarking import load_agent_scenarios_from_paths  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate agent runs against workflow-native benchmark scenarios")
    parser.add_argument(
        "--scenarios",
        nargs="+",
        required=True,
        help="One or more scenario JSONL files.",
    )
    parser.add_argument(
        "--runs",
        required=True,
        help="Path to the agent run JSONL file.",
    )
    parser.add_argument(
        "--rubric",
        default=str(PROJECT_ROOT / "data" / "agent_decision_bench" / "rubrics" / "default_scoring.json"),
        help="Path to the scoring rubric JSON file.",
    )
    parser.add_argument(
        "--summary-json",
        help="Optional path to write a structured JSON summary.",
    )
    parser.add_argument(
        "--fail-on-incomplete",
        action="store_true",
        help="Exit with status 1 when not all tasks are completed.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    scenarios = load_agent_scenarios_from_paths(args.scenarios)
    runs = load_agent_runs(args.runs)
    rubric = load_scoring_rubric(args.rubric)
    summary = evaluate_agent_runs(scenarios, runs, rubric=rubric)

    print(format_evaluation_summary(summary))

    if args.summary_json:
        write_evaluation_summary_json(summary, args.summary_json)
        print(f"Wrote evaluation summary to {args.summary_json}")

    if args.fail_on_incomplete and summary.task_completion_rate < 1.0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
