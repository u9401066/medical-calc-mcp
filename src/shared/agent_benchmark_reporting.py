"""Reporting helpers for benchmark profile result bundles."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast


@dataclass(frozen=True)
class BenchmarkProfileResult:
    profile_id: str
    model_name: str
    prompt_policy: str
    benchmark_date: str
    run_source_type: str
    run_source_path: str
    generated_at: str
    summary: dict[str, Any]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> BenchmarkProfileResult:
        profile_payload = cast(dict[str, Any], payload["profile"])
        run_source_payload = cast(dict[str, Any], profile_payload["run_source"])
        return cls(
            profile_id=str(profile_payload["profile_id"]),
            model_name=str(profile_payload["model_name"]),
            prompt_policy=str(profile_payload["prompt_policy"]),
            benchmark_date=str(profile_payload["benchmark_date"]),
            run_source_type=str(run_source_payload["source_type"]),
            run_source_path=str(run_source_payload["path"]),
            generated_at=str(payload.get("generated_at", "")),
            summary=cast(dict[str, Any], payload["summary"]),
        )

    def task_completion_rate(self) -> float:
        return float(self.summary.get("task_completion_rate", 0.0))

    def weighted_score(self) -> float:
        average_metrics = cast(dict[str, Any], self.summary.get("average_metrics", {}))
        return float(average_metrics.get("weighted_score", 0.0))

    def safety_capture_rate(self) -> float:
        average_metrics = cast(dict[str, Any], self.summary.get("average_metrics", {}))
        return float(average_metrics.get("safety_capture_rate", 0.0))

    def overreach_penalty_rate(self) -> float:
        average_metrics = cast(dict[str, Any], self.summary.get("average_metrics", {}))
        return float(average_metrics.get("overreach_penalty_rate", 0.0))


def load_benchmark_profile_results(paths: list[str | Path] | tuple[str | Path, ...]) -> list[BenchmarkProfileResult]:
    results: list[BenchmarkProfileResult] = []
    for path in paths:
        payload = cast(dict[str, Any], json.loads(Path(path).read_text(encoding="utf-8")))
        results.append(BenchmarkProfileResult.from_dict(payload))
    return results


def build_leaderboard_rows(
    results: list[BenchmarkProfileResult] | tuple[BenchmarkProfileResult, ...],
) -> list[dict[str, Any]]:
    ordered = sorted(
        results,
        key=lambda result: (
            result.task_completion_rate(),
            result.weighted_score(),
            result.safety_capture_rate(),
            -result.overreach_penalty_rate(),
        ),
        reverse=True,
    )
    rows: list[dict[str, Any]] = []
    for rank, result in enumerate(ordered, start=1):
        rows.append(
            {
                "rank": rank,
                "profile_id": result.profile_id,
                "model_name": result.model_name,
                "prompt_policy": result.prompt_policy,
                "benchmark_date": result.benchmark_date,
                "run_source_type": result.run_source_type,
                "run_source_path": result.run_source_path,
                "task_completion_rate": result.task_completion_rate(),
                "weighted_score": result.weighted_score(),
                "safety_capture_rate": result.safety_capture_rate(),
                "overreach_penalty_rate": result.overreach_penalty_rate(),
                "total_scenarios": int(result.summary.get("total_scenarios", 0)),
                "total_runs": int(result.summary.get("total_runs", 0)),
            }
        )
    return rows


def render_markdown_leaderboard(
    results: list[BenchmarkProfileResult] | tuple[BenchmarkProfileResult, ...],
) -> str:
    rows = build_leaderboard_rows(results)
    generated_at = datetime.now(UTC).isoformat()
    lines = [
        "# Benchmark Leaderboard",
        "",
        f"Generated at: {generated_at}",
        "",
        "| Rank | Profile | Model | Prompt Policy | Date | Completion | Weighted | Safety | Overreach |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {rank} | {profile_id} | {model_name} | {prompt_policy} | {benchmark_date} | {completion:.2%} | {weighted:.3f} | {safety:.2%} | {overreach:.2%} |".format(
                rank=row["rank"],
                profile_id=row["profile_id"],
                model_name=row["model_name"],
                prompt_policy=row["prompt_policy"],
                benchmark_date=row["benchmark_date"],
                completion=float(row["task_completion_rate"]),
                weighted=float(row["weighted_score"]),
                safety=float(row["safety_capture_rate"]),
                overreach=float(row["overreach_penalty_rate"]),
            )
        )
    return "\n".join(lines) + "\n"


def build_time_series_payload(
    results: list[BenchmarkProfileResult] | tuple[BenchmarkProfileResult, ...],
) -> dict[str, Any]:
    points = []
    for result in sorted(results, key=lambda item: (item.benchmark_date, item.profile_id)):
        points.append(
            {
                "series_id": f"{result.model_name}::{result.prompt_policy}",
                "profile_id": result.profile_id,
                "model_name": result.model_name,
                "prompt_policy": result.prompt_policy,
                "benchmark_date": result.benchmark_date,
                "run_source_type": result.run_source_type,
                "run_source_path": result.run_source_path,
                "generated_at": result.generated_at,
                "task_completion_rate": result.task_completion_rate(),
                "weighted_score": result.weighted_score(),
                "average_metrics": result.summary.get("average_metrics", {}),
                "total_scenarios": result.summary.get("total_scenarios", 0),
                "total_runs": result.summary.get("total_runs", 0),
            }
        )
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "points": points,
    }


def write_markdown_leaderboard(
    results: list[BenchmarkProfileResult] | tuple[BenchmarkProfileResult, ...],
    path: str | Path,
) -> None:
    Path(path).write_text(render_markdown_leaderboard(results), encoding="utf-8")


def write_time_series_json(
    results: list[BenchmarkProfileResult] | tuple[BenchmarkProfileResult, ...],
    path: str | Path,
) -> None:
    Path(path).write_text(json.dumps(build_time_series_payload(results), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_report_index_json(
    results: list[BenchmarkProfileResult] | tuple[BenchmarkProfileResult, ...],
    path: str | Path,
) -> None:
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "leaderboard": build_leaderboard_rows(results),
        "time_series": build_time_series_payload(results),
    }
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
