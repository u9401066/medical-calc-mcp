"""Smart input normalization and resolution helpers for MCP-facing interfaces."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field

from .fuzzy_matching import closest_matches

COMMON_IDENTIFIER_PREFIXES = (
    "calculate_",
    "get_",
    "tool_",
)

COMMON_IDENTIFIER_SUFFIXES = (
    "_score",
    "_calculator",
    "_calc",
    "_tool",
)


@dataclass(frozen=True)
class ResolutionResult:
    """Represents a best-effort identifier resolution attempt."""

    raw_value: str
    normalized_value: str
    resolved_value: str | None = None
    suggestions: tuple[str, ...] = field(default_factory=tuple)
    matched_by: str = "none"
    ambiguous_matches: tuple[str, ...] = field(default_factory=tuple)

    @property
    def was_resolved(self) -> bool:
        return self.resolved_value is not None


def normalize_identifier(value: str) -> str:
    """Normalize user-supplied identifiers to a registry-friendly key."""
    normalized = value.strip().lower()
    normalized = normalized.replace("'", "").replace('"', "").replace("`", "")
    normalized = re.sub(r"[\s\-/]+", "_", normalized)
    normalized = re.sub(r"[^a-z0-9_]+", "", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized


def build_identifier_aliases(candidate: str) -> set[str]:
    """Generate relaxed aliases for a canonical identifier."""
    normalized = normalize_identifier(candidate)
    aliases = {normalized, normalized.replace("_", "")}

    pending = {normalized}
    while pending:
        current = pending.pop()
        for prefix in COMMON_IDENTIFIER_PREFIXES:
            if current.startswith(prefix):
                stripped = current.removeprefix(prefix)
                if stripped and stripped not in aliases:
                    aliases.add(stripped)
                    aliases.add(stripped.replace("_", ""))
                    pending.add(stripped)
        for suffix in COMMON_IDENTIFIER_SUFFIXES:
            if current.endswith(suffix):
                stripped = current.removesuffix(suffix)
                if stripped and stripped not in aliases:
                    aliases.add(stripped)
                    aliases.add(stripped.replace("_", ""))
                    pending.add(stripped)

    return {alias for alias in aliases if alias}


def resolve_identifier(
    raw_value: str,
    candidates: Iterable[str],
    *,
    cutoff: float = 0.72,
) -> ResolutionResult:
    """Resolve an arbitrary input string against a set of canonical candidates."""
    candidate_list = sorted(set(candidates))
    normalized_raw = normalize_identifier(raw_value)
    if not normalized_raw:
        return ResolutionResult(raw_value=raw_value, normalized_value=normalized_raw)

    raw_aliases = build_identifier_aliases(raw_value)

    canonical_by_normalized = {normalize_identifier(candidate): candidate for candidate in candidate_list}
    matched_exact = next(
        (canonical_by_normalized[alias] for alias in raw_aliases if alias in canonical_by_normalized),
        None,
    )
    if matched_exact is not None:
        return ResolutionResult(
            raw_value=raw_value,
            normalized_value=normalized_raw,
            resolved_value=matched_exact,
            matched_by="exact",
        )

    alias_map: dict[str, str] = {}
    ambiguous_aliases: dict[str, set[str]] = {}
    for canonical_candidate in candidate_list:
        for alias in build_identifier_aliases(canonical_candidate):
            if alias in alias_map and alias_map[alias] != canonical_candidate:
                ambiguous_aliases.setdefault(alias, {alias_map[alias]}).add(canonical_candidate)
                continue
            alias_map[alias] = canonical_candidate

    matched_alias = next(
        (alias_map[alias] for alias in raw_aliases if alias in alias_map and alias not in ambiguous_aliases),
        None,
    )
    if matched_alias is not None:
        return ResolutionResult(
            raw_value=raw_value,
            normalized_value=normalized_raw,
            resolved_value=matched_alias,
            matched_by="alias",
        )

    search_space = sorted(set(canonical_by_normalized) | set(alias_map))
    fuzzy_inputs = sorted(raw_aliases)
    close_keys: list[str] = []
    for alias in fuzzy_inputs:
        for key in closest_matches(alias, search_space, limit=5, cutoff=cutoff):
            if key not in close_keys:
                close_keys.append(key)
    suggestions: list[str] = []
    for key in close_keys:
        matched_candidate: str | None = canonical_by_normalized.get(key)
        if matched_candidate is None:
            matched_candidate = alias_map.get(key)
        if matched_candidate and matched_candidate not in suggestions:
            suggestions.append(matched_candidate)

    ambiguous_values: set[str] = set()
    for alias in raw_aliases:
        ambiguous_values.update(ambiguous_aliases.get(alias, ()))
    ambiguous_matches = tuple(sorted(ambiguous_values))
    return ResolutionResult(
        raw_value=raw_value,
        normalized_value=normalized_raw,
        suggestions=tuple(suggestions),
        matched_by="fuzzy" if suggestions else "none",
        ambiguous_matches=ambiguous_matches,
    )
