"""Benchmark utilities for evaluating registry-backed calculators against tabular datasets."""

from __future__ import annotations

import ast
import csv
import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, cast

from src.application.dto import CalculateRequest
from src.application.use_cases.calculate_use_case import CalculateUseCase
from src.infrastructure.mcp.server import MedicalCalculatorServer


def _normalize_key(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum())


def _coerce_scalar(value: Any) -> Any:
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return stripped
        lowered = stripped.lower()
        if lowered in {"true", "false"}:
            return lowered == "true"
        try:
            if any(ch in stripped for ch in (".", "e", "E")):
                numeric = float(stripped)
                return int(numeric) if numeric.is_integer() else numeric
            return int(stripped)
        except ValueError:
            return stripped
    return value


def _parse_entities(raw_value: str) -> dict[str, Any]:
    stripped = raw_value.strip()
    if not stripped:
        return {}
    parsed: Any
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        parsed = ast.literal_eval(stripped)
    if not isinstance(parsed, dict):
        raise ValueError("Relevant Entities must parse to a dictionary")
    return {str(key): _coerce_scalar(value) for key, value in parsed.items()}


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    stripped = str(value).strip()
    if not stripped:
        return None
    return float(stripped)


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    source: str
    calculator_name: str | None
    params: dict[str, Any]
    expected_value: float
    lower_limit: float | None = None
    upper_limit: float | None = None
    abs_tolerance: float | None = None
    rel_tolerance: float | None = None
    tool_id: str | None = None


@dataclass(frozen=True)
class ToolAdapter:
    tool_id: str
    param_aliases: dict[str, str] = field(default_factory=dict)
    defaults: dict[str, Any] = field(default_factory=dict)

    def adapt(self, entities: dict[str, Any]) -> dict[str, Any]:
        adapted = dict(self.defaults)
        normalized_aliases = {_normalize_key(key): value for key, value in self.param_aliases.items()}
        for key, value in entities.items():
            normalized = _normalize_key(key)
            adapted[normalized_aliases.get(normalized, key)] = value
        return adapted


MEDCALC_TOOL_ADAPTERS: dict[str, ToolAdapter] = {
    _normalize_key("bsa_calculator"): ToolAdapter(
        tool_id="body_surface_area",
        defaults={"formula": "mosteller"},
        param_aliases={"height": "height_cm", "weight": "weight_kg"},
    ),
    _normalize_key("body_surface_area"): ToolAdapter(
        tool_id="body_surface_area",
        defaults={"formula": "mosteller"},
        param_aliases={"height": "height_cm", "weight": "weight_kg"},
    ),
    _normalize_key("calcium_correction"): ToolAdapter(
        tool_id="corrected_calcium",
        param_aliases={"calcium": "calcium_mg_dl", "albumin": "albumin_g_dl"},
    ),
    _normalize_key("sodium_correction_hyperglycemia"): ToolAdapter(
        tool_id="corrected_sodium",
        defaults={"formula": "katz", "glucose_unit": "mg/dL"},
        param_aliases={"sodium": "measured_sodium"},
    ),
    _normalize_key("creatinine_clearance"): ToolAdapter(
        tool_id="cockcroft_gault",
        param_aliases={
            "creatinine": "creatinine_mg_dl",
            "serumcreatinine": "creatinine_mg_dl",
            "weight": "weight_kg",
            "height": "height_cm",
        },
    ),
    _normalize_key("free_water_deficit"): ToolAdapter(
        tool_id="free_water_deficit",
        defaults={"target_sodium": 140.0, "patient_type": "adult_male", "correction_time_hours": 24},
        param_aliases={"sodium": "current_sodium", "weight": "weight_kg"},
    ),
    _normalize_key("sosmserumosmolality"): ToolAdapter(
        tool_id="serum_osmolality",
        param_aliases={"bloodureanitrogen": "bun"},
    ),
    _normalize_key("serum_osmolality"): ToolAdapter(
        tool_id="serum_osmolality",
        param_aliases={"bloodureanitrogen": "bun"},
    ),
}


def resolve_tool(case: BenchmarkCase) -> tuple[str | None, dict[str, Any], str | None]:
    if case.tool_id:
        return case.tool_id, case.params, None
    if case.calculator_name is None:
        return None, case.params, "Case does not specify calculator_name or tool_id"
    adapter = MEDCALC_TOOL_ADAPTERS.get(_normalize_key(case.calculator_name))
    if adapter is None:
        return None, case.params, f"Unsupported MedCalc-Bench calculator: {case.calculator_name}"
    return adapter.tool_id, adapter.adapt(case.params), None


def load_benchmark_cases(path: str | Path, *, fmt: str = "auto") -> list[BenchmarkCase]:
    dataset_path = Path(path)
    selected_format = fmt
    if selected_format == "auto":
        selected_format = "normalized-jsonl" if dataset_path.suffix.lower() == ".jsonl" else "medcalc-bench-csv"

    if selected_format == "normalized-jsonl":
        return _load_normalized_jsonl(dataset_path)
    if selected_format == "medcalc-bench-csv":
        return _load_medcalc_bench_csv(dataset_path)
    raise ValueError(f"Unsupported dataset format: {fmt}")


def _load_normalized_jsonl(path: Path) -> list[BenchmarkCase]:
    cases: list[BenchmarkCase] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        payload = cast(dict[str, Any], json.loads(stripped))
        cases.append(
            BenchmarkCase(
                case_id=str(payload.get("case_id", f"jsonl-{line_number}")),
                source=str(payload.get("source", path.name)),
                calculator_name=cast(str | None, payload.get("calculator_name")),
                tool_id=cast(str | None, payload.get("tool_id")),
                params=cast(dict[str, Any], payload["params"]),
                expected_value=float(payload["expected_value"]),
                lower_limit=_float_or_none(payload.get("lower_limit")),
                upper_limit=_float_or_none(payload.get("upper_limit")),
                abs_tolerance=_float_or_none(payload.get("abs_tolerance")),
                rel_tolerance=_float_or_none(payload.get("rel_tolerance")),
            )
        )
    return cases


def _lookup_row_value(row: dict[str, Any], *candidates: str) -> Any:
    normalized = {_normalize_key(key): value for key, value in row.items()}
    for candidate in candidates:
        value = normalized.get(_normalize_key(candidate))
        if value not in (None, ""):
            return value
    return None


def _load_medcalc_bench_csv(path: Path) -> list[BenchmarkCase]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        cases: list[BenchmarkCase] = []
        for index, row in enumerate(reader, start=1):
            calculator_name = cast(str | None, _lookup_row_value(row, "Calculator Name", "calculator_name"))
            relevant_entities_raw = cast(str | None, _lookup_row_value(row, "Relevant Entities", "relevant_entities"))
            if relevant_entities_raw is None:
                raise ValueError(f"Row {index} missing Relevant Entities column")
            expected_value = _lookup_row_value(row, "Ground Truth Answer", "ground_truth_answer", "expected_value")
            if expected_value is None:
                raise ValueError(f"Row {index} missing Ground Truth Answer column")

            case_id = _lookup_row_value(row, "case_id", "Case ID", "id") or f"csv-{index}"
            cases.append(
                BenchmarkCase(
                    case_id=str(case_id),
                    source=path.name,
                    calculator_name=calculator_name,
                    params=_parse_entities(str(relevant_entities_raw)),
                    expected_value=float(expected_value),
                    lower_limit=_float_or_none(_lookup_row_value(row, "Lower Limit", "lower_limit")),
                    upper_limit=_float_or_none(_lookup_row_value(row, "Upper Limit", "upper_limit")),
                    abs_tolerance=_float_or_none(_lookup_row_value(row, "Absolute Tolerance", "abs_tolerance")),
                    rel_tolerance=_float_or_none(_lookup_row_value(row, "Relative Tolerance", "rel_tolerance")),
                )
            )
    return cases


@dataclass(frozen=True)
class BenchmarkCaseResult:
    case_id: str
    status: str
    source: str
    calculator_name: str | None
    tool_id: str | None
    expected_value: float
    actual_value: float | None = None
    lower_limit: float | None = None
    upper_limit: float | None = None
    error: str | None = None


@dataclass(frozen=True)
class BenchmarkSummary:
    total_cases: int
    passed: int
    failed: int
    skipped: int
    errored: int
    executed: int
    accuracy: float
    results: tuple[BenchmarkCaseResult, ...]
    per_tool: dict[str, dict[str, int]]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["results"] = [asdict(result) for result in self.results]
        return payload


def build_calculate_use_case() -> CalculateUseCase:
    server = MedicalCalculatorServer()
    return CalculateUseCase(server.registry)


def _value_within_case_limits(case: BenchmarkCase, actual_value: float, default_abs_tolerance: float) -> bool:
    if case.lower_limit is not None or case.upper_limit is not None:
        lower = case.lower_limit if case.lower_limit is not None else actual_value
        upper = case.upper_limit if case.upper_limit is not None else actual_value
        return lower <= actual_value <= upper
    abs_tol = case.abs_tolerance if case.abs_tolerance is not None else default_abs_tolerance
    rel_tol = case.rel_tolerance if case.rel_tolerance is not None else 0.0
    return math.isclose(actual_value, case.expected_value, rel_tol=rel_tol, abs_tol=abs_tol)


def evaluate_cases(cases: list[BenchmarkCase], *, default_abs_tolerance: float = 1e-6) -> BenchmarkSummary:
    calculator = build_calculate_use_case()
    results: list[BenchmarkCaseResult] = []
    per_tool: dict[str, dict[str, int]] = {}
    passed = failed = skipped = errored = 0

    for case in cases:
        tool_id, adapted_params, resolution_error = resolve_tool(case)
        if resolution_error is not None or tool_id is None:
            skipped += 1
            results.append(
                BenchmarkCaseResult(
                    case_id=case.case_id,
                    status="skipped",
                    source=case.source,
                    calculator_name=case.calculator_name,
                    tool_id=tool_id,
                    expected_value=case.expected_value,
                    lower_limit=case.lower_limit,
                    upper_limit=case.upper_limit,
                    error=resolution_error,
                )
            )
            continue

        tool_stats = per_tool.setdefault(tool_id, {"passed": 0, "failed": 0, "errored": 0})
        response = calculator.execute(CalculateRequest(tool_id=tool_id, params=adapted_params))
        if not response.success:
            errored += 1
            tool_stats["errored"] += 1
            results.append(
                BenchmarkCaseResult(
                    case_id=case.case_id,
                    status="error",
                    source=case.source,
                    calculator_name=case.calculator_name,
                    tool_id=tool_id,
                    expected_value=case.expected_value,
                    lower_limit=case.lower_limit,
                    upper_limit=case.upper_limit,
                    error=response.error,
                )
            )
            continue

        raw_value = response.result
        if not isinstance(raw_value, (int, float)):
            errored += 1
            tool_stats["errored"] += 1
            results.append(
                BenchmarkCaseResult(
                    case_id=case.case_id,
                    status="error",
                    source=case.source,
                    calculator_name=case.calculator_name,
                    tool_id=tool_id,
                    expected_value=case.expected_value,
                    lower_limit=case.lower_limit,
                    upper_limit=case.upper_limit,
                    error=f"Non-numeric result type: {type(raw_value).__name__}",
                )
            )
            continue

        actual_value = float(raw_value)
        if _value_within_case_limits(case, actual_value, default_abs_tolerance):
            passed += 1
            tool_stats["passed"] += 1
            status = "passed"
        else:
            failed += 1
            tool_stats["failed"] += 1
            status = "failed"
        results.append(
            BenchmarkCaseResult(
                case_id=case.case_id,
                status=status,
                source=case.source,
                calculator_name=case.calculator_name,
                tool_id=tool_id,
                expected_value=case.expected_value,
                actual_value=actual_value,
                lower_limit=case.lower_limit,
                upper_limit=case.upper_limit,
            )
        )

    executed = passed + failed + errored
    accuracy = (passed / executed) if executed else 0.0
    return BenchmarkSummary(
        total_cases=len(cases),
        passed=passed,
        failed=failed,
        skipped=skipped,
        errored=errored,
        executed=executed,
        accuracy=accuracy,
        results=tuple(results),
        per_tool=per_tool,
    )


def write_summary_json(summary: BenchmarkSummary, output_path: str | Path) -> None:
    Path(output_path).write_text(json.dumps(summary.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")


def format_summary(summary: BenchmarkSummary) -> str:
    lines = [
        "Medical-Calc-MCP Benchmark Summary",
        f"Total cases: {summary.total_cases}",
        f"Executed: {summary.executed} | Passed: {summary.passed} | Failed: {summary.failed} | Errors: {summary.errored} | Skipped: {summary.skipped}",
        f"Accuracy: {summary.accuracy:.1%}",
        "",
        "Per-tool results:",
    ]
    for tool_id in sorted(summary.per_tool):
        stats = summary.per_tool[tool_id]
        lines.append(
            f"- {tool_id}: {stats['passed']} passed, {stats['failed']} failed, {stats['errored']} errors"
        )
    failing = [result for result in summary.results if result.status in {"failed", "error", "skipped"}]
    if failing:
        lines.append("")
        lines.append("Non-passing cases:")
        for result in failing:
            detail = result.error or f"expected {result.expected_value}, got {result.actual_value}"
            lines.append(f"- {result.case_id} [{result.status}] {detail}")
    return "\n".join(lines)