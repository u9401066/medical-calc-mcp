#!/usr/bin/env python
"""Count normalized benchmark cases across one or more JSONL files."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.shared.hf_benchmark_dataset import count_benchmark_cases, load_hf_benchmark_cases  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Count normalized benchmark cases")
    parser.add_argument("paths", nargs="+", help="One or more JSONL benchmark files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of plain text.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    cases = load_hf_benchmark_cases(args.paths)
    by_split = Counter(case.split for case in cases)
    payload = {
        "total_cases": count_benchmark_cases(args.paths),
        "by_split": dict(sorted(by_split.items())),
        "unique_tools": len({case.tool_id for case in cases}),
        "unique_guideline_domains": len({domain for case in cases for domain in case.guideline_domains}),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"Total cases: {payload['total_cases']}")
    print(f"Unique tools: {payload['unique_tools']}")
    print(f"Unique guideline domains: {payload['unique_guideline_domains']}")
    for split_name, count in sorted(by_split.items()):
        print(f"  {split_name}: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
