"""Helpers for HF-style benchmark case datasets built from Medical-Calc-MCP."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, cast


@dataclass(frozen=True)
class HfBenchmarkCase:
    """A normalized benchmark case that remains compatible with load_benchmark_cases()."""

    case_id: str
    source: str
    split: str
    question: str
    tool_id: str
    calculator_name: str
    params: dict[str, Any]
    expected_value: float
    abs_tolerance: float | None = None
    lower_limit: float | None = None
    upper_limit: float | None = None
    primary_specialty: str = ""
    specialties: tuple[str, ...] = ()
    guideline_domains: tuple[str, ...] = ()
    formula_source_type: str = ""
    task_family: str = "calculator_execution"
    setting: str = "general"
    references: tuple[dict[str, Any], ...] = ()
    provenance: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> HfBenchmarkCase:
        return cls(
            case_id=str(payload["case_id"]),
            source=str(payload.get("source", "")),
            split=str(payload.get("split", "unspecified")),
            question=str(payload.get("question", "")),
            tool_id=str(payload["tool_id"]),
            calculator_name=str(payload.get("calculator_name", payload["tool_id"])),
            params=cast(dict[str, Any], payload["params"]),
            expected_value=float(payload["expected_value"]),
            abs_tolerance=cast(float | None, payload.get("abs_tolerance")),
            lower_limit=cast(float | None, payload.get("lower_limit")),
            upper_limit=cast(float | None, payload.get("upper_limit")),
            primary_specialty=str(payload.get("primary_specialty", "")),
            specialties=tuple(str(item) for item in payload.get("specialties", [])),
            guideline_domains=tuple(str(item) for item in payload.get("guideline_domains", [])),
            formula_source_type=str(payload.get("formula_source_type", "")),
            task_family=str(payload.get("task_family", "calculator_execution")),
            setting=str(payload.get("setting", "general")),
            references=tuple(cast(dict[str, Any], item) for item in payload.get("references", [])),
            provenance=cast(dict[str, Any], payload.get("provenance", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_hf_benchmark_cases(paths: str | Path | list[str | Path] | tuple[str | Path, ...]) -> list[HfBenchmarkCase]:
    """Load one or more JSONL files into benchmark cases."""

    if isinstance(paths, (str, Path)):
        resolved_paths: tuple[str | Path, ...] = (paths,)
    else:
        resolved_paths = tuple(paths)

    cases: list[HfBenchmarkCase] = []
    for path in resolved_paths:
        dataset_path = Path(path)
        for line_number, line in enumerate(dataset_path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = cast(dict[str, Any], json.loads(stripped))
            if "case_id" not in payload:
                raise ValueError(f"Line {line_number} in {dataset_path} missing case_id")
            cases.append(HfBenchmarkCase.from_dict(payload))
    return cases


def write_hf_benchmark_cases_jsonl(
    cases: list[HfBenchmarkCase] | tuple[HfBenchmarkCase, ...],
    path: str | Path,
) -> None:
    """Write normalized benchmark cases to JSONL."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(case.to_dict(), ensure_ascii=False, sort_keys=True) for case in cases]
    output_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def count_benchmark_cases(paths: str | Path | list[str | Path] | tuple[str | Path, ...]) -> int:
    """Count cases across one or more JSONL files."""

    return len(load_hf_benchmark_cases(paths))
