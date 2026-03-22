#!/usr/bin/env python
"""Emit GitHub Actions matrix JSON from the benchmark profile manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.shared.agent_benchmark_profiles import load_benchmark_profile_manifest, manifest_to_github_actions_matrix  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Emit benchmark profile matrix JSON")
    parser.add_argument(
        "--manifest",
        default=str(PROJECT_ROOT / "data" / "agent_decision_bench" / "profiles" / "manifest.json"),
        help="Path to the benchmark profile manifest JSON file.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    manifest = load_benchmark_profile_manifest(args.manifest)
    print(json.dumps(manifest_to_github_actions_matrix(manifest), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
