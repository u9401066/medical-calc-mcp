#!/usr/bin/env python
"""Generate a stable OpenAPI snapshot from the FastAPI application."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.infrastructure.api.server import app
from src.shared.project_metadata import PROJECT_ROOT, get_project_version

OUTPUT_PATH = PROJECT_ROOT / "docs_site/api/openapi.json"


def render_openapi() -> str:
    schema = app.openapi()
    return json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_output(output_path: Path) -> None:
    output_path.write_text(render_openapi(), encoding="utf-8")


def check_output(output_path: Path) -> bool:
    rendered = render_openapi()
    if not output_path.exists():
        return False
    return output_path.read_text(encoding="utf-8") == rendered


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the generated OpenAPI snapshot is missing or stale.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.check:
        if check_output(OUTPUT_PATH):
            print("Generated OpenAPI spec is up to date.")
            return 0
        print(
            "Generated OpenAPI spec is stale. "
            "Run `uv run python scripts/generate_openapi_spec.py` to refresh it."
        )
        return 1

    write_output(OUTPUT_PATH)
    print(
        f"Wrote {OUTPUT_PATH.relative_to(PROJECT_ROOT)} "
        f"for Medical Calculator API v{get_project_version()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
