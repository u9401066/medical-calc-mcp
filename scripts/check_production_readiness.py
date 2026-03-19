"""Run production-readiness checks for API and MCP services."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate production readiness for Medical Calc services")
    parser.add_argument("--service", choices=["api", "mcp", "all"], default="all", help="Service to validate")
    parser.add_argument("--environment", default=None, help="Override environment name used by readiness checks")
    parser.add_argument("--fail-on-warn", action="store_true", help="Treat readiness warnings as a failing condition")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")
    return parser.parse_args()


def build_api_report() -> dict[str, Any]:
    from src.infrastructure.api.server import _initialize_registry, build_api_readiness_report

    registry, _, _ = _initialize_registry()
    report = build_api_readiness_report(registry)
    payload = report.to_dict()
    payload["service_key"] = "api"
    return payload


def build_mcp_report() -> dict[str, Any]:
    from src.infrastructure.mcp.server import MedicalCalculatorServer

    server = MedicalCalculatorServer()
    report = server.build_readiness_report()
    payload = report.to_dict()
    payload["service_key"] = "mcp"
    return payload


def format_report(report: dict[str, Any]) -> str:
    lines = [
        f"[{report['service_key']}] {report['service']} ({report['environment']})",
        f"  overall_status={report['overall_status']} ready={report['ready']} fails={report['fail_count']} warnings={report['warning_count']}",
    ]
    for check in report["checks"]:
        lines.append(f"  - {check['name']}: {check['status']} | {check['detail']}")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()

    if args.environment:
        os.environ["APP_ENV"] = args.environment

    builders = {
        "api": build_api_report,
        "mcp": build_mcp_report,
    }
    service_keys = [args.service] if args.service != "all" else ["api", "mcp"]
    reports = [builders[service_key]() for service_key in service_keys]

    if args.json:
        print(json.dumps(reports, indent=2, ensure_ascii=False))
    else:
        for report in reports:
            print(format_report(report))

    has_failures = any(not report["ready"] for report in reports)
    has_warnings = any(report["warning_count"] > 0 for report in reports)
    if has_failures or (args.fail_on_warn and has_warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())