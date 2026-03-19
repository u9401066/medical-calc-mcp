#!/usr/bin/env python
"""Evaluate Medical-Calc-MCP calculators against MedCalc-Bench style datasets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.shared.benchmarking import (
    evaluate_cases,
    format_summary,
    load_benchmark_cases,
    write_summary_json,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate registry calculators against MedCalc-Bench style datasets")
    parser.add_argument("--dataset", required=True, help="Path to a MedCalc-Bench CSV or normalized JSONL dataset")
    parser.add_argument(
        "--format",
        default="auto",
        choices=("auto", "medcalc-bench-csv", "normalized-jsonl"),
        help="Dataset format. Defaults to auto-detection by file extension.",
    )
    parser.add_argument(
        "--default-abs-tolerance",
        type=float,
        default=1e-6,
        help="Absolute tolerance when a case does not provide its own comparison limits.",
    )
    parser.add_argument(
        "--report-json",
        help="Optional output path for a structured JSON summary report.",
    )
    parser.add_argument(
        "--fail-on-nonpassing",
        action="store_true",
        help="Exit with status 1 if any case fails, errors, or is skipped.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    cases = load_benchmark_cases(dataset_path, fmt=args.format)
    summary = evaluate_cases(cases, default_abs_tolerance=args.default_abs_tolerance)

    print(format_summary(summary))

    if args.report_json:
        write_summary_json(summary, args.report_json)
        print(f"\nWrote JSON report to {args.report_json}")

    if args.fail_on_nonpassing and (summary.failed or summary.errored or summary.skipped):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
