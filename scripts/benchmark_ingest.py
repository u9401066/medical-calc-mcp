#!/usr/bin/env python
"""Ingest external benchmark datasets into the agent scenario schema."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.shared.agent_benchmarking import (  # noqa: E402
    format_ingestion_result,
    get_source_registry_entry,
    ingest_dataset_to_scenarios,
    load_source_registry,
    write_ingestion_summary_json,
    write_scenarios_jsonl,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest external benchmark datasets into agent scenario JSONL")
    parser.add_argument(
        "--dataset",
        required=True,
        help="Path to the external dataset file to ingest.",
    )
    parser.add_argument(
        "--source-id",
        required=True,
        help="Source id from the source registry.",
    )
    parser.add_argument(
        "--registry",
        default=str(PROJECT_ROOT / "data" / "benchmarks" / "source_registry.json"),
        help="Path to the benchmark source registry JSON file.",
    )
    parser.add_argument(
        "--input-format",
        default="auto",
        choices=("auto", "medcalc-bench-csv", "normalized-jsonl", "agent-scenario-jsonl"),
        help="Dataset format. Defaults to auto or the registry entry ingestion format.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output path for the scenario JSONL file.",
    )
    parser.add_argument(
        "--summary-json",
        help="Optional output path for a structured ingestion summary JSON.",
    )
    parser.add_argument(
        "--fail-on-skipped",
        action="store_true",
        help="Exit with status 1 when any records are skipped during ingestion.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    registry = load_source_registry(args.registry)
    source_entry = get_source_registry_entry(registry, args.source_id)
    result = ingest_dataset_to_scenarios(
        args.dataset,
        input_format=args.input_format,
        source_entry=source_entry,
    )

    write_scenarios_jsonl(result.scenarios, args.output)
    print(format_ingestion_result(result))
    print(f"Wrote scenarios to {args.output}")

    if args.summary_json:
        write_ingestion_summary_json(result, args.summary_json)
        print(f"Wrote ingestion summary to {args.summary_json}")

    if args.fail_on_skipped and result.skipped_records:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
