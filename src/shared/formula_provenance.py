"""Helpers for calculator formula provenance and reference metadata validation."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from functools import lru_cache
from typing import cast

from ..domain.value_objects.reference import Reference
from .project_metadata import PROJECT_ROOT

FORMULA_PROVENANCE_PATH = PROJECT_ROOT / "data" / "formula_provenance.json"
ALLOWED_FORMULA_SOURCE_TYPES = ("original", "guideline", "derived")

PMID_PATTERN = re.compile(r"^\d{1,9}$")
DOI_PATTERN = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)


@lru_cache(maxsize=1)
def load_formula_provenance_manifest() -> dict[str, list[str]]:
    """Load the formula provenance manifest from disk."""
    return cast(dict[str, list[str]], json.loads(FORMULA_PROVENANCE_PATH.read_text(encoding="utf-8")))


@lru_cache(maxsize=1)
def get_formula_source_map() -> dict[str, str]:
    """Build a tool_id -> formula_source_type mapping from the manifest."""
    manifest = load_formula_provenance_manifest()
    mapping: dict[str, str] = {}
    for source_type in ALLOWED_FORMULA_SOURCE_TYPES:
        for tool_id in manifest.get(source_type, []):
            mapping[tool_id] = source_type
    return mapping


def get_formula_source_type(tool_id: str) -> str | None:
    """Return the provenance type for a tool id, if present in the manifest."""
    return get_formula_source_map().get(tool_id)


def validate_formula_provenance_manifest(tool_ids: set[str]) -> list[str]:
    """Validate manifest coverage and uniqueness against the current registry."""
    issues: list[str] = []
    manifest = load_formula_provenance_manifest()
    seen: dict[str, str] = {}

    for source_type, values in manifest.items():
        if source_type not in ALLOWED_FORMULA_SOURCE_TYPES:
            issues.append(f"Unknown formula_source_type bucket in manifest: {source_type}")
            continue
        for tool_id in values:
            previous = seen.get(tool_id)
            if previous is not None:
                issues.append(
                    f"Tool '{tool_id}' appears multiple times in formula provenance manifest: {previous}, {source_type}"
                )
                continue
            seen[tool_id] = source_type

    missing = sorted(tool_ids - set(seen))
    extras = sorted(set(seen) - tool_ids)

    if missing:
        issues.append("Tools missing formula provenance entries: " + ", ".join(missing))
    if extras:
        issues.append("Formula provenance manifest contains unknown tools: " + ", ".join(extras))

    return issues


def validate_reference_metadata(reference: Reference, *, context: str) -> list[str]:
    """Validate reference metadata completeness and field formats."""
    issues: list[str] = []
    citation = reference.citation.strip()
    current_year = datetime.now(UTC).year + 1

    if not citation:
        issues.append(f"{context}: citation text is empty")
    if reference.year is not None and (reference.year < 1900 or reference.year > current_year):
        issues.append(f"{context}: invalid publication year {reference.year}")
    if reference.pmid and not PMID_PATTERN.fullmatch(reference.pmid):
        issues.append(f"{context}: invalid PMID format '{reference.pmid}'")
    if reference.doi and not DOI_PATTERN.fullmatch(reference.doi):
        issues.append(f"{context}: invalid DOI format '{reference.doi}'")

    return issues
