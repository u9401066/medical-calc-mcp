#!/usr/bin/env python
"""Generate REST API reference docs from the FastAPI OpenAPI schema."""

from __future__ import annotations

import argparse
from typing import Any

from src.infrastructure.api.server import app
from src.shared.project_metadata import PROJECT_ROOT

OUTPUT_PATH = PROJECT_ROOT / "docs_site/api/rest-api.md"


def _schema_label(schema: dict[str, Any] | None) -> str:
    if not schema:
        return "-"
    if "$ref" in schema:
        return str(schema["$ref"]).rsplit("/", maxsplit=1)[-1]
    if "type" in schema:
        return str(schema["type"])
    if "anyOf" in schema:
        return " | ".join(_schema_label(option) for option in schema["anyOf"])
    return "object"


def _escape(text: str) -> str:
    return " ".join(text.replace("|", "\\|").split())


def _append_markdown_block(lines: list[str], text: str) -> None:
    just_closed_fence = False

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        if not line:
            if lines and lines[-1] != "":
                lines.append("")
            just_closed_fence = False
            continue

        if just_closed_fence and lines and lines[-1] != "":
            lines.append("")
        just_closed_fence = False

        if line.startswith("#"):
            if lines and lines[-1] != "":
                lines.append("")
            lines.append(line)
            lines.append("")
            continue

        if line.startswith("```"):
            if lines and lines[-1] != "":
                lines.append("")
            lines.append(line)
            just_closed_fence = True
            continue

        lines.append(line)

    if lines and lines[-1] != "":
        lines.append("")


def render_rest_api_docs() -> str:
    schema = app.openapi()
    info = schema["info"]
    paths: dict[str, Any] = schema["paths"]
    component_schemas = schema.get("components", {}).get("schemas", {})

    lines = [
        "<!-- markdownlint-disable MD024 -->",
        "",
        "# REST API Reference",
        "",
        "> Generated from the FastAPI OpenAPI schema. Do not edit manually.",
        f"> Source: [openapi.json](openapi.json) | OpenAPI {schema['openapi']} | v{info['version']}",
        "",
        (
            f"This API currently publishes **{sum(len(methods) for methods in paths.values())} operations** "
            f"across **{len(paths)} paths**, backed by **{len(component_schemas)} shared schemas**."
        ),
        "",
        "## Base URL",
        "",
        "```",
        "http://localhost:8000",
        "```",
        "",
        "Endpoint paths below are shown in full, including `/api/v1` where applicable.",
        "",
        "Health and docs remain available at the server root: `/health`, `/ready`, `/docs`, `/redoc`, and `/openapi.json`.",
        "",
        "## API Metadata",
        "",
        f"- Title: {_escape(info['title'])}",
        f"- Version: {_escape(info['version'])}",
    ]

    description = str(info.get("description", "")).strip()
    if description:
        lines.extend(["", "### Description", ""])
        _append_markdown_block(lines, description)

    lines.extend(["## Endpoints", ""])

    for path, methods in sorted(paths.items()):
        for method, operation in sorted(methods.items()):
            summary = operation.get("summary", "")
            lines.append(f"### {method.upper()} {path}")
            lines.append("")
            if summary:
                lines.extend(["#### Summary", "", _escape(summary), ""])
            description = str(operation.get("description", "")).strip()
            if description:
                lines.extend(["#### Description", ""])
                _append_markdown_block(lines, description)

            tags = operation.get("tags", [])
            if tags:
                lines.extend(["#### Tags", "", ", ".join(tags), ""])

            parameters = operation.get("parameters", [])
            if parameters:
                lines.extend(
                    [
                        "#### Parameters",
                        "",
                        "| Name | In | Required | Type | Description |",
                        "|------|----|----------|------|-------------|",
                    ]
                )
                for parameter in parameters:
                    param_schema = parameter.get("schema", {})
                    lines.append(
                        "| "
                        f"{_escape(parameter['name'])} | {_escape(parameter.get('in', '-'))} | "
                        f"{'yes' if parameter.get('required') else 'no'} | {_escape(_schema_label(param_schema))} | "
                        f"{_escape(parameter.get('description', '-'))} |"
                    )
                lines.append("")

            request_body = operation.get("requestBody")
            if request_body:
                lines.extend(
                    [
                        "#### Request Body",
                        "",
                        "| Content-Type | Schema | Required |",
                        "|--------------|--------|----------|",
                    ]
                )
                for content_type, content in request_body.get("content", {}).items():
                    lines.append(
                        f"| {_escape(content_type)} | {_escape(_schema_label(content.get('schema')))} | {'yes' if request_body.get('required') else 'no'} |"
                    )
                lines.append("")

            lines.extend(
                [
                    "#### Responses",
                    "",
                    "| Status | Schema | Description |",
                    "|--------|--------|-------------|",
                ]
            )
            for status_code, response in sorted(operation.get("responses", {}).items()):
                content = response.get("content", {})
                schema_label = "-"
                if content:
                    first_content = next(iter(content.values()))
                    schema_label = _schema_label(first_content.get("schema"))
                lines.append(f"| {_escape(status_code)} | {_escape(schema_label)} | {_escape(response.get('description', '-'))} |")
            lines.append("")

    lines.extend(["## Shared Schemas", "", "| Schema | Description |", "|--------|-------------|"])
    for schema_name, schema_body in sorted(component_schemas.items()):
        lines.append(f"| {_escape(schema_name)} | {_escape(str(schema_body.get('description', '-')))} |")
    lines.append("")

    return "\n".join(lines)


def write_output() -> None:
    OUTPUT_PATH.write_text(render_rest_api_docs(), encoding="utf-8")


def is_current() -> bool:
    rendered = render_rest_api_docs()
    return OUTPUT_PATH.exists() and OUTPUT_PATH.read_text(encoding="utf-8") == rendered


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if the generated REST API docs are missing or stale.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check:
        if is_current():
            print("Generated REST API docs are up to date.")
            return 0
        print("Generated REST API docs are stale. Run `uv run python scripts/generate_rest_api_docs.py` to refresh them.")
        return 1

    write_output()
    print(f"Wrote {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
