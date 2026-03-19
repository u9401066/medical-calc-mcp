"""Shared fuzzy matching helpers with an optional rapidfuzz backend."""

from __future__ import annotations

from difflib import SequenceMatcher
from difflib import get_close_matches as difflib_get_close_matches
from importlib import import_module
from typing import Any

try:  # pragma: no branch - import depends on optional dependency presence
    _rapidfuzz_fuzz: Any = import_module("rapidfuzz.fuzz")
    _rapidfuzz_process: Any = import_module("rapidfuzz.process")
except ImportError:  # pragma: no cover - fallback path depends on installed extras
    _rapidfuzz_fuzz = None
    _rapidfuzz_process = None


def rapidfuzz_available() -> bool:
    """Return whether rapidfuzz is available in the current environment."""
    return _rapidfuzz_fuzz is not None and _rapidfuzz_process is not None


def similarity_ratio(left: str, right: str) -> float:
    """Return normalized similarity ratio in the range 0-1."""
    if rapidfuzz_available():
        return float(_rapidfuzz_fuzz.ratio(left, right)) / 100.0
    return SequenceMatcher(None, left, right).ratio()


def closest_matches(value: str, candidates: list[str], *, limit: int = 5, cutoff: float = 0.72) -> list[str]:
    """Return the closest candidate strings above the provided cutoff."""
    if not candidates:
        return []

    if rapidfuzz_available():
        matches = _rapidfuzz_process.extract(
            value,
            candidates,
            limit=limit,
            score_cutoff=cutoff * 100.0,
        )
        return [candidate for candidate, _score, _index in matches]

    return list(difflib_get_close_matches(value, candidates, n=limit, cutoff=cutoff))
