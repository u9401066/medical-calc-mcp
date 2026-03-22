"""Adapters for converting MCP tool usage traces and MCP transcripts into benchmark run records."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal, cast

from src.infrastructure.logging import ToolUsageEvent

from .agent_benchmark_evaluator import AgentRunRecord, AgentToolCall
from .agent_benchmarking import AgentBenchmarkScenario

TraceFormat = Literal["auto", "tool_usage_event", "mcp_transcript"]


@dataclass(frozen=True)
class TraceEntry:
    session_id: str
    sequence_number: int
    trace_format: str
    timestamp: str = ""
    scenario_id: str | None = None
    entry_type: str = "tool_call"
    action: str | None = None
    tool_id: str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    param_names: tuple[str, ...] = ()
    text: str = ""
    cited_tools: tuple[str, ...] = ()
    questions_asked: tuple[str, ...] = ()
    safety_signals: tuple[str, ...] = ()
    output_traits: tuple[str, ...] = ()
    overreach_flags: tuple[str, ...] = ()
    observed_modalities: tuple[str, ...] = ()


@dataclass(frozen=True)
class TraceAdaptationResult:
    total_events: int
    total_sessions: int
    adapted_runs: tuple[AgentRunRecord, ...]
    skipped_sessions: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["adapted_runs"] = [asdict(run) for run in self.adapted_runs]
        return payload


def load_tool_usage_events(path: str | Path) -> list[ToolUsageEvent]:
    trace_path = Path(path)
    events: list[ToolUsageEvent] = []
    for line_number, line in enumerate(trace_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        payload = cast(dict[str, Any], json.loads(stripped))
        if "tool_id" not in payload:
            raise ValueError(f"Line {line_number} missing tool_id")
        events.append(
            ToolUsageEvent(
                event_id=str(payload.get("event_id", f"evt_{line_number}")),
                timestamp=str(payload.get("timestamp", "")),
                tool_id=str(payload["tool_id"]),
                tool_category=str(payload.get("tool_category", "")),
                param_names=[str(item) for item in payload.get("param_names", [])],
                param_count=int(payload.get("param_count", 0)),
                success=bool(payload.get("success", False)),
                has_warnings=bool(payload.get("has_warnings", False)),
                warning_types=[str(item) for item in payload.get("warning_types", [])],
                error_type=cast(str | None, payload.get("error_type")),
                duration_ms=float(payload.get("duration_ms", 0.0)),
                session_id=cast(str | None, payload.get("session_id")),
                sequence_number=int(payload.get("sequence_number", 0)),
                previous_tool=cast(str | None, payload.get("previous_tool")),
            )
        )
    return events


def _ensure_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return cast(dict[str, Any], value)
    return {}


def _parse_tool_usage_event_entry(payload: dict[str, Any], line_number: int) -> TraceEntry:
    event = ToolUsageEvent(
        event_id=str(payload.get("event_id", f"evt_{line_number}")),
        timestamp=str(payload.get("timestamp", "")),
        tool_id=str(payload["tool_id"]),
        tool_category=str(payload.get("tool_category", "")),
        param_names=[str(item) for item in payload.get("param_names", [])],
        param_count=int(payload.get("param_count", 0)),
        success=bool(payload.get("success", False)),
        has_warnings=bool(payload.get("has_warnings", False)),
        warning_types=[str(item) for item in payload.get("warning_types", [])],
        error_type=cast(str | None, payload.get("error_type")),
        duration_ms=float(payload.get("duration_ms", 0.0)),
        session_id=cast(str | None, payload.get("session_id")),
        sequence_number=int(payload.get("sequence_number", 0)),
        previous_tool=cast(str | None, payload.get("previous_tool")),
    )
    return TraceEntry(
        session_id=event.session_id or f"session_{event.event_id}",
        sequence_number=event.sequence_number,
        trace_format="tool_usage_event",
        timestamp=event.timestamp,
        entry_type="tool_call",
        action="calculate",
        tool_id=event.tool_id,
        params={"_observed_param_names": event.param_names},
        param_names=tuple(event.param_names),
        safety_signals=tuple(event.warning_types if event.has_warnings else ()),
        cited_tools=(event.tool_id,),
        observed_modalities=("tool_calls", "cited_tools"),
    )


def _infer_entry_type(payload: dict[str, Any]) -> str:
    raw_type = str(payload.get("event_type") or payload.get("type") or payload.get("kind") or "").strip().lower()
    role = str(payload.get("role") or "").strip().lower()

    if raw_type in {"tool_call", "tool", "call"}:
        return "tool_call"
    if raw_type in {"assistant", "assistant_message", "message"} or role == "assistant":
        return "assistant_message"
    if raw_type in {"user", "user_message"} or role == "user":
        return "user_message"
    if any(key in payload for key in ("action", "tool_name", "tool_call", "tool", "arguments", "params")):
        return "tool_call"
    if any(key in payload for key in ("text", "content", "message")):
        return "assistant_message"
    return "metadata"


def _parse_transcript_tool_call(payload: dict[str, Any]) -> tuple[str | None, str | None, dict[str, Any]]:
    call_payload = _ensure_mapping(payload.get("tool_call") or payload.get("tool"))
    action = cast(
        str | None,
        payload.get("action")
        or payload.get("tool_name")
        or call_payload.get("tool_name")
        or call_payload.get("name"),
    )
    raw_arguments = (
        payload.get("arguments")
        or payload.get("params")
        or payload.get("input")
        or call_payload.get("arguments")
        or call_payload.get("params")
        or {}
    )
    arguments = _ensure_mapping(raw_arguments)
    tool_id = cast(str | None, payload.get("tool_id") or call_payload.get("tool_id"))

    normalized_params = arguments
    if action in {"get_tool_schema", "calculate"} and tool_id is None and "tool_id" in arguments:
        tool_id = str(arguments.get("tool_id"))

    if action == "calculate":
        nested_params = arguments.get("params")
        if isinstance(nested_params, dict):
            normalized_params = cast(dict[str, Any], nested_params)
        else:
            normalized_params = {key: value for key, value in arguments.items() if key != "tool_id"}
    elif action == "get_tool_schema":
        normalized_params = {}
    else:
        normalized_params = dict(arguments)

    return action, tool_id, normalized_params


def _parse_transcript_entry(payload: dict[str, Any], line_number: int) -> TraceEntry:
    entry_type = _infer_entry_type(payload)
    session_id = str(
        payload.get("session_id")
        or payload.get("conversation_id")
        or payload.get("thread_id")
        or payload.get("scenario_id")
        or f"session_{line_number}"
    )
    scenario_id = cast(str | None, payload.get("scenario_id"))
    sequence_number = int(payload.get("sequence_number", line_number - 1))
    timestamp = str(payload.get("timestamp", ""))
    text = str(payload.get("text") or payload.get("content") or payload.get("message") or "")

    action: str | None = None
    tool_id: str | None = None
    params: dict[str, Any] = {}
    observed_modalities: list[str] = []

    if entry_type == "tool_call":
        action, tool_id, params = _parse_transcript_tool_call(payload)
        observed_modalities.append("tool_calls")
        if tool_id:
            observed_modalities.append("cited_tools")
        if action == "calculate" and params:
            observed_modalities.append("params")

    explicit_questions = tuple(str(item) for item in payload.get("questions_asked", []))
    explicit_cited_tools = tuple(str(item) for item in payload.get("cited_tools", []))
    safety_signals = tuple(str(item) for item in payload.get("safety_signals", []))
    output_traits = tuple(str(item) for item in payload.get("output_traits", []))
    overreach_flags = tuple(str(item) for item in payload.get("overreach_flags", []))

    if "questions_asked" in payload:
        observed_modalities.append("questions")
    if "cited_tools" in payload:
        observed_modalities.append("cited_tools")
    if "safety_signals" in payload:
        observed_modalities.append("safety_signals")
    if "output_traits" in payload:
        observed_modalities.append("output_traits")
    if "overreach_flags" in payload:
        observed_modalities.append("overreach")

    return TraceEntry(
        session_id=session_id,
        sequence_number=sequence_number,
        trace_format="mcp_transcript",
        timestamp=timestamp,
        scenario_id=scenario_id,
        entry_type=entry_type,
        action=action,
        tool_id=tool_id,
        params=params,
        param_names=tuple(str(key) for key in params),
        text=text,
        cited_tools=explicit_cited_tools,
        questions_asked=explicit_questions,
        safety_signals=safety_signals,
        output_traits=output_traits,
        overreach_flags=overreach_flags,
        observed_modalities=tuple(dict.fromkeys(observed_modalities)),
    )


def load_trace_entries(path: str | Path, *, trace_format: TraceFormat = "auto") -> list[TraceEntry]:
    trace_path = Path(path)
    entries: list[TraceEntry] = []
    for line_number, line in enumerate(trace_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        payload = cast(dict[str, Any], json.loads(stripped))
        resolved_format = trace_format
        if resolved_format == "auto":
            if "tool_id" in payload and "action" not in payload and "tool_name" not in payload and "tool_call" not in payload:
                resolved_format = "tool_usage_event"
            else:
                resolved_format = "mcp_transcript"
        if resolved_format == "tool_usage_event":
            if "tool_id" not in payload:
                raise ValueError(f"Line {line_number} missing tool_id")
            entries.append(_parse_tool_usage_event_entry(payload, line_number))
            continue
        entries.append(_parse_transcript_entry(payload, line_number))
    return entries


def _group_entries_by_session(entries: list[TraceEntry]) -> dict[str, list[TraceEntry]]:
    grouped: dict[str, list[TraceEntry]] = {}
    for entry in entries:
        grouped.setdefault(entry.session_id, []).append(entry)
    for session_id, session_entries in grouped.items():
        grouped[session_id] = sorted(
            session_entries,
            key=lambda entry: (entry.sequence_number, entry.timestamp, entry.tool_id or "", entry.action or ""),
        )
    return grouped


def _infer_scenario_id(
    session_id: str,
    entries: list[TraceEntry],
    scenarios: list[AgentBenchmarkScenario],
    session_mapping: dict[str, str] | None,
) -> str | None:
    if session_mapping and session_id in session_mapping:
        return session_mapping[session_id]

    explicit_scenario_ids = tuple(dict.fromkeys(entry.scenario_id for entry in entries if entry.scenario_id))
    if explicit_scenario_ids:
        return explicit_scenario_ids[0]

    scenario_ids = {scenario.scenario_id for scenario in scenarios}
    if session_id in scenario_ids:
        return session_id

    actual_tools = tuple(entry.tool_id for entry in entries if entry.entry_type == "tool_call" and entry.tool_id)
    best_scenario_id: str | None = None
    best_score = 0.0
    for scenario in scenarios:
        expected_tools = scenario.expected_tools
        if not expected_tools:
            continue
        matched = 0
        pointer = 0
        for actual_tool in actual_tools:
            if pointer < len(expected_tools) and actual_tool == expected_tools[pointer]:
                matched += 1
                pointer += 1
        overlap_score = matched / len(expected_tools)
        if overlap_score > best_score:
            best_score = overlap_score
            best_scenario_id = scenario.scenario_id
    if best_score <= 0:
        return None
    return best_scenario_id


def adapt_trace_entries_to_runs(
    entries: list[TraceEntry],
    scenarios: list[AgentBenchmarkScenario],
    *,
    session_mapping: dict[str, str] | None = None,
) -> TraceAdaptationResult:
    grouped_entries = _group_entries_by_session(entries)
    adapted_runs: list[AgentRunRecord] = []
    skipped_sessions: list[str] = []

    for session_id, session_entries in grouped_entries.items():
        scenario_id = _infer_scenario_id(session_id, session_entries, scenarios, session_mapping)
        if scenario_id is None:
            skipped_sessions.append(session_id)
            continue

        tool_calls = tuple(
            AgentToolCall(
                action=entry.action or "calculate",
                tool_id=entry.tool_id,
                params=entry.params,
            )
            for entry in session_entries
            if entry.entry_type == "tool_call" and entry.action is not None
        )
        questions_asked = tuple(
            dict.fromkeys(question for entry in session_entries for question in entry.questions_asked)
        )
        cited_tools = tuple(
            dict.fromkeys(
                tool_id
                for entry in session_entries
                for tool_id in ((entry.tool_id,) if entry.tool_id else ()) + entry.cited_tools
            )
        )
        safety_signals = tuple(
            dict.fromkeys(signal for entry in session_entries for signal in entry.safety_signals)
        )
        output_traits = tuple(
            dict.fromkeys(trait for entry in session_entries for trait in entry.output_traits)
        )
        overreach_flags = tuple(
            dict.fromkeys(flag for entry in session_entries for flag in entry.overreach_flags)
        )
        final_messages = [entry.text for entry in session_entries if entry.entry_type == "assistant_message" and entry.text]
        observed_modalities = tuple(
            dict.fromkeys(modality for entry in session_entries for modality in entry.observed_modalities)
        )

        adapted_runs.append(
            AgentRunRecord(
                scenario_id=scenario_id,
                tool_calls=tool_calls,
                questions_asked=questions_asked,
                cited_tools=cited_tools,
                safety_signals=safety_signals,
                output_traits=output_traits,
                overreach_flags=overreach_flags,
                final_text=final_messages[-1] if final_messages else "",
                observed_modalities=observed_modalities or ("tool_calls",),
            )
        )

    return TraceAdaptationResult(
        total_events=len(entries),
        total_sessions=len(grouped_entries),
        adapted_runs=tuple(adapted_runs),
        skipped_sessions=tuple(skipped_sessions),
    )


def adapt_tool_usage_events_to_runs(
    events: list[ToolUsageEvent],
    scenarios: list[AgentBenchmarkScenario],
    *,
    session_mapping: dict[str, str] | None = None,
) -> TraceAdaptationResult:
    entries = [
        TraceEntry(
            session_id=event.session_id or f"session_{event.event_id}",
            sequence_number=event.sequence_number,
            trace_format="tool_usage_event",
            timestamp=event.timestamp,
            entry_type="tool_call",
            action="calculate",
            tool_id=event.tool_id,
            params={"_observed_param_names": event.param_names},
            param_names=tuple(event.param_names),
            safety_signals=tuple(event.warning_types if event.has_warnings else ()),
            cited_tools=(event.tool_id,),
            observed_modalities=("tool_calls", "cited_tools"),
        )
        for event in events
    ]
    return adapt_trace_entries_to_runs(entries, scenarios, session_mapping=session_mapping)


def load_session_mapping(path: str | Path) -> dict[str, str]:
    payload = cast(dict[str, Any], json.loads(Path(path).read_text(encoding="utf-8")))
    return {str(key): str(value) for key, value in payload.items()}


def write_adapted_runs_jsonl(runs: tuple[AgentRunRecord, ...] | list[AgentRunRecord], path: str | Path) -> None:
    output_path = Path(path)
    lines = [json.dumps(asdict(run), ensure_ascii=False, sort_keys=True) for run in runs]
    output_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def write_trace_adaptation_summary_json(result: TraceAdaptationResult, path: str | Path) -> None:
    Path(path).write_text(json.dumps(result.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def format_trace_adaptation_result(result: TraceAdaptationResult) -> str:
    lines = [
        f"Total events: {result.total_events}",
        f"Total sessions: {result.total_sessions}",
        f"Adapted runs: {len(result.adapted_runs)}",
        f"Skipped sessions: {len(result.skipped_sessions)}",
    ]
    if result.skipped_sessions:
        lines.append("Skipped session ids: " + ", ".join(result.skipped_sessions))
    return "\n".join(lines)
