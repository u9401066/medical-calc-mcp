#!/usr/bin/env python
"""Adapt MCP trace logs into agent benchmark run JSONL."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import cast

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
    parser = argparse.ArgumentParser(description="Adapt MCP trace logs into agent benchmark run JSONL")
    parser.add_argument("--trace-log", required=True, help="Path to the MCP trace JSONL log file.")
    parser.add_argument(
        "--trace-format",
        default="auto",
        choices=("auto", "tool_usage_event", "mcp_transcript"),
        help="Trace input format. Defaults to auto-detection.",
    )
    parser.add_argument("--scenarios", nargs="+", required=True, help="One or more scenario JSONL files.")
    parser.add_argument("--output", required=True, help="Output path for adapted agent runs JSONL.")
    parser.add_argument(
        "--session-mapping",
        help="Optional JSON mapping from session_id to scenario_id. If omitted, the adapter uses exact or sequence-based matching.",
    )
    parser.add_argument("--summary-json", help="Optional path to write an adaptation summary JSON.")
    parser.add_argument("--fail-on-skipped", action="store_true", help="Exit with status 1 if any sessions cannot be mapped.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    entries = load_trace_entries(args.trace_log, trace_format=cast(TraceFormat, args.trace_format))
    scenarios = load_agent_scenarios_from_paths(args.scenarios)
    session_mapping = load_session_mapping(args.session_mapping) if args.session_mapping else None
    result = adapt_trace_entries_to_runs(entries, scenarios, session_mapping=session_mapping)

    write_adapted_runs_jsonl(result.adapted_runs, args.output)
    print(format_trace_adaptation_result(result))
    print(f"Wrote adapted runs to {args.output}")

    if args.summary_json:
        write_trace_adaptation_summary_json(result, args.summary_json)
        print(f"Wrote trace adaptation summary to {args.summary_json}")

    if args.fail_on_skipped and result.skipped_sessions:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
