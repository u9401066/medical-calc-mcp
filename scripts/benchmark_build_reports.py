#!/usr/bin/env python
"""Build leaderboard and time-series artifacts from benchmark profile bundles."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import cast

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.shared.agent_benchmark_reporting import (  # noqa: E402
    load_benchmark_profile_results,
    render_markdown_leaderboard,
    write_markdown_leaderboard,
    write_report_index_json,
    write_time_series_json,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build benchmark leaderboard and time-series artifacts")
    parser.add_argument("--inputs", nargs="+", required=True, help="Profile bundle JSON files or directories.")
    parser.add_argument("--leaderboard-md", required=True, help="Output path for markdown leaderboard.")
    parser.add_argument("--time-series-json", required=True, help="Output path for JSON time-series payload.")
    parser.add_argument("--report-index-json", help="Optional output path for combined report index JSON.")
    return parser


def _collect_input_paths(inputs: list[str]) -> list[Path]:
    collected: list[Path] = []
    for raw_input in inputs:
        candidate = Path(raw_input)
        if candidate.is_dir():
            collected.extend(sorted(candidate.rglob("profile-result-*.json")))
            continue
        collected.append(candidate)
    unique_paths = []
    seen: set[Path] = set()
    for path in collected:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique_paths.append(path)
    return unique_paths


def main() -> int:
    args = build_parser().parse_args()
    input_paths = _collect_input_paths(args.inputs)
    results = load_benchmark_profile_results(cast(list[str | Path], input_paths))

    write_markdown_leaderboard(results, args.leaderboard_md)
    write_time_series_json(results, args.time_series_json)
    if args.report_index_json:
        write_report_index_json(results, args.report_index_json)

    print(render_markdown_leaderboard(results))
    print(f"Wrote markdown leaderboard to {args.leaderboard_md}")
    print(f"Wrote JSON time series to {args.time_series_json}")
    if args.report_index_json:
        print(f"Wrote report index to {args.report_index_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
