"""Utilities for source registry management, scenario loading, and benchmark ingestion."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, cast

from .benchmarking import BenchmarkCase, load_benchmark_cases, resolve_tool

DEFAULT_EXPECTED_OUTPUT_TRAITS: tuple[str, ...] = (
    "bounded_claims",
    "numeric_grounding",
    "schema_first_execution",
)
DEFAULT_SAFETY_CHECKS: tuple[str, ...] = (
    "do_not_invent_missing_inputs",
    "ground_result_in_explicit_calculation",
)


@dataclass(frozen=True)
class SourceIngestionConfig:
    input_format: str
    task_family: str = "calculator_execution"
    setting: str = "general"
    expected_output_traits: tuple[str, ...] = DEFAULT_EXPECTED_OUTPUT_TRAITS
    safety_checks: tuple[str, ...] = DEFAULT_SAFETY_CHECKS

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SourceIngestionConfig:
        return cls(
            input_format=str(payload.get("input_format", "medcalc-bench-csv")),
            task_family=str(payload.get("task_family", "calculator_execution")),
            setting=str(payload.get("setting", "general")),
            expected_output_traits=tuple(
                str(item) for item in payload.get("expected_output_traits", DEFAULT_EXPECTED_OUTPUT_TRAITS)
            ),
            safety_checks=tuple(str(item) for item in payload.get("safety_checks", DEFAULT_SAFETY_CHECKS)),
        )


@dataclass(frozen=True)
class SourceRegistryEntry:
    source_id: str
    title: str
    category: str
    trust_tier: str
    origin_tier: str
    host: str
    primary_url: str
    mirror_url: str | None = None
    license: str | None = None
    task_fit: str = "direct"
    status: str = "candidate"
    ingestion: SourceIngestionConfig = field(default_factory=lambda: SourceIngestionConfig(input_format="auto"))
    notes: str | None = None
    evidence: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SourceRegistryEntry:
        return cls(
            source_id=str(payload["source_id"]),
            title=str(payload["title"]),
            category=str(payload["category"]),
            trust_tier=str(payload["trust_tier"]),
            origin_tier=str(payload["origin_tier"]),
            host=str(payload["host"]),
            primary_url=str(payload["primary_url"]),
            mirror_url=cast(str | None, payload.get("mirror_url")),
            license=cast(str | None, payload.get("license")),
            task_fit=str(payload.get("task_fit", "direct")),
            status=str(payload.get("status", "candidate")),
            ingestion=SourceIngestionConfig.from_dict(cast(dict[str, Any], payload.get("ingestion", {}))),
            notes=cast(str | None, payload.get("notes")),
            evidence=tuple(str(item) for item in payload.get("evidence", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentBenchmarkScenario:
    scenario_id: str
    source_id: str
    source_title: str
    category: str
    task_family: str
    setting: str
    clinical_prompt: str
    available_data: dict[str, Any]
    hidden_data: dict[str, Any]
    gold_workflow: tuple[str, ...]
    expected_tools: tuple[str, ...]
    expected_params: dict[str, Any]
    expected_result: dict[str, Any]
    track_id: str = ""
    critical_questions: tuple[str, ...] = ()
    acceptable_questions: tuple[str, ...] = ()
    required_safety_signals: tuple[str, ...] = ()
    safety_checks: tuple[str, ...] = ()
    expected_output_traits: tuple[str, ...] = ()
    prohibited_output_traits: tuple[str, ...] = ()
    task_weights: dict[str, float] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> AgentBenchmarkScenario:
        return cls(
            scenario_id=str(payload["scenario_id"]),
            source_id=str(payload["source_id"]),
            source_title=str(payload["source_title"]),
            category=str(payload["category"]),
            task_family=str(payload["task_family"]),
            setting=str(payload["setting"]),
            clinical_prompt=str(payload["clinical_prompt"]),
            available_data=cast(dict[str, Any], payload["available_data"]),
            hidden_data=cast(dict[str, Any], payload.get("hidden_data", {})),
            gold_workflow=tuple(str(item) for item in payload.get("gold_workflow", [])),
            expected_tools=tuple(str(item) for item in payload.get("expected_tools", [])),
            expected_params=cast(dict[str, Any], payload.get("expected_params", {})),
            expected_result=cast(dict[str, Any], payload.get("expected_result", {})),
            track_id=str(payload.get("track_id", "")),
            critical_questions=tuple(str(item) for item in payload.get("critical_questions", [])),
            acceptable_questions=tuple(str(item) for item in payload.get("acceptable_questions", [])),
            required_safety_signals=tuple(str(item) for item in payload.get("required_safety_signals", [])),
            safety_checks=tuple(str(item) for item in payload.get("safety_checks", [])),
            expected_output_traits=tuple(str(item) for item in payload.get("expected_output_traits", [])),
            prohibited_output_traits=tuple(str(item) for item in payload.get("prohibited_output_traits", [])),
            task_weights={str(key): float(value) for key, value in payload.get("task_weights", {}).items()},
            provenance=cast(dict[str, Any], payload.get("provenance", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IngestionResult:
    source_id: str | None
    input_format: str
    total_records: int
    converted_records: int
    skipped_records: int
    scenarios: tuple[AgentBenchmarkScenario, ...]
    skipped_details: tuple[dict[str, str], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["scenarios"] = [scenario.to_dict() for scenario in self.scenarios]
        return payload


def load_source_registry(path: str | Path) -> dict[str, SourceRegistryEntry]:
    registry_path = Path(path)
    payload = cast(dict[str, Any], json.loads(registry_path.read_text(encoding="utf-8")))
    entries_payload = cast(list[dict[str, Any]], payload.get("entries", []))
    entries = [SourceRegistryEntry.from_dict(entry_payload) for entry_payload in entries_payload]
    return {entry.source_id: entry for entry in entries}


def get_source_registry_entry(
    registry: dict[str, SourceRegistryEntry],
    source_id: str,
) -> SourceRegistryEntry:
    try:
        return registry[source_id]
    except KeyError as exc:
        available = ", ".join(sorted(registry))
        raise ValueError(f"Unknown source_id: {source_id}. Available source ids: {available}") from exc


def _select_input_format(
    dataset_path: Path,
    requested_format: str,
    source_entry: SourceRegistryEntry | None,
) -> str:
    if requested_format != "auto":
        return requested_format
    if source_entry is not None and source_entry.ingestion.input_format != "auto":
        return source_entry.ingestion.input_format
    if dataset_path.suffix.lower() == ".jsonl":
        return "normalized-jsonl"
    return "medcalc-bench-csv"


def _build_expected_result_payload(case_payload: BenchmarkCase) -> dict[str, Any]:
    result = {"numeric": float(case_payload.expected_value)}
    if case_payload.lower_limit is not None:
        result["lower_limit"] = case_payload.lower_limit
    if case_payload.upper_limit is not None:
        result["upper_limit"] = case_payload.upper_limit
    if case_payload.abs_tolerance is not None:
        result["abs_tolerance"] = case_payload.abs_tolerance
    if case_payload.rel_tolerance is not None:
        result["rel_tolerance"] = case_payload.rel_tolerance
    return result


def _build_calculator_scenario(
    case_payload: BenchmarkCase,
    *,
    source_entry: SourceRegistryEntry | None,
) -> tuple[AgentBenchmarkScenario | None, str | None]:
    tool_id, adapted_params, resolution_error = resolve_tool(case_payload)
    if resolution_error is not None or tool_id is None:
        return None, resolution_error or "Unable to resolve tool id"

    source_id = source_entry.source_id if source_entry is not None else "unregistered_source"
    source_title = source_entry.title if source_entry is not None else str(case_payload.source)
    category = source_entry.category if source_entry is not None else "calculator_benchmark"
    ingestion = source_entry.ingestion if source_entry is not None else SourceIngestionConfig(input_format="auto")
    calculator_label = case_payload.calculator_name or tool_id
    prompt = (
        f"Use the available structured patient data to run {calculator_label} via the canonical tool "
        f"{tool_id} and report the grounded result without inventing missing inputs."
    )

    scenario = AgentBenchmarkScenario(
        scenario_id=f"{source_id}__{case_payload.case_id}",
        track_id=ingestion.task_family,
        source_id=source_id,
        source_title=source_title,
        category=category,
        task_family=ingestion.task_family,
        setting=ingestion.setting,
        clinical_prompt=prompt,
        available_data={
            "structured": adapted_params,
            "free_text": "",
            "source_case": {
                "calculator_name": case_payload.calculator_name,
                "source_dataset": case_payload.source,
            },
        },
        hidden_data={},
        gold_workflow=(f"get_tool_schema:{tool_id}", f"calculate:{tool_id}"),
        expected_tools=(tool_id,),
        expected_params=adapted_params,
        expected_result=_build_expected_result_payload(case_payload),
        critical_questions=(),
        safety_checks=ingestion.safety_checks,
        expected_output_traits=ingestion.expected_output_traits,
        provenance={
            "original_case_id": case_payload.case_id,
            "original_calculator_name": case_payload.calculator_name,
            "original_params": case_payload.params,
            "source_dataset": case_payload.source,
            "source_url": source_entry.primary_url if source_entry is not None else None,
        },
    )
    return scenario, None


def load_agent_scenarios(path: str | Path) -> list[AgentBenchmarkScenario]:
    scenario_path = Path(path)
    scenarios: list[AgentBenchmarkScenario] = []
    for line_number, line in enumerate(scenario_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        payload = cast(dict[str, Any], json.loads(stripped))
        if "scenario_id" not in payload:
            raise ValueError(f"Line {line_number} missing scenario_id")
        scenarios.append(AgentBenchmarkScenario.from_dict(payload))
    return scenarios


def load_agent_scenarios_from_paths(paths: list[str | Path] | tuple[str | Path, ...]) -> list[AgentBenchmarkScenario]:
    scenarios: list[AgentBenchmarkScenario] = []
    for path in paths:
        scenarios.extend(load_agent_scenarios(path))
    return scenarios


def ingest_dataset_to_scenarios(
    dataset_path: str | Path,
    *,
    input_format: str = "auto",
    source_entry: SourceRegistryEntry | None = None,
) -> IngestionResult:
    resolved_dataset_path = Path(dataset_path)
    selected_format = _select_input_format(resolved_dataset_path, input_format, source_entry)

    if selected_format == "agent-scenario-jsonl":
        existing_scenarios = load_agent_scenarios(resolved_dataset_path)
        return IngestionResult(
            source_id=source_entry.source_id if source_entry is not None else None,
            input_format=selected_format,
            total_records=len(existing_scenarios),
            converted_records=len(existing_scenarios),
            skipped_records=0,
            scenarios=tuple(existing_scenarios),
            skipped_details=(),
        )

    benchmark_cases = load_benchmark_cases(resolved_dataset_path, fmt=selected_format)
    scenarios: list[AgentBenchmarkScenario] = []
    skipped_details: list[dict[str, str]] = []

    for benchmark_case in benchmark_cases:
        scenario, error = _build_calculator_scenario(benchmark_case, source_entry=source_entry)
        if scenario is None:
            skipped_details.append({"case_id": benchmark_case.case_id, "reason": error or "Unknown ingestion error"})
            continue
        scenarios.append(scenario)

    return IngestionResult(
        source_id=source_entry.source_id if source_entry is not None else None,
        input_format=selected_format,
        total_records=len(benchmark_cases),
        converted_records=len(scenarios),
        skipped_records=len(skipped_details),
        scenarios=tuple(scenarios),
        skipped_details=tuple(skipped_details),
    )


def write_scenarios_jsonl(scenarios: tuple[AgentBenchmarkScenario, ...] | list[AgentBenchmarkScenario], path: str | Path) -> None:
    output_path = Path(path)
    lines = [json.dumps(scenario.to_dict(), ensure_ascii=False, sort_keys=True) for scenario in scenarios]
    output_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def write_ingestion_summary_json(result: IngestionResult, path: str | Path) -> None:
    Path(path).write_text(json.dumps(result.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def format_ingestion_result(result: IngestionResult) -> str:
    lines = [
        f"Source: {result.source_id or 'unregistered'}",
        f"Input format: {result.input_format}",
        f"Total records: {result.total_records}",
        f"Converted records: {result.converted_records}",
        f"Skipped records: {result.skipped_records}",
    ]
    if result.skipped_details:
        lines.append("Skipped case ids: " + ", ".join(detail["case_id"] for detail in result.skipped_details))
    return "\n".join(lines)

