"""Profile manifest utilities for versioned benchmark runs."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, cast


@dataclass(frozen=True)
class BenchmarkRunSource:
    source_type: str
    path: str
    trace_format: str = "auto"
    session_mapping: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> BenchmarkRunSource:
        return cls(
            source_type=str(payload["source_type"]),
            path=str(payload["path"]),
            trace_format=str(payload.get("trace_format", "auto")),
            session_mapping=cast(str | None, payload.get("session_mapping")),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BenchmarkProfile:
    profile_id: str
    model_name: str
    prompt_policy: str
    benchmark_date: str
    run_source: BenchmarkRunSource
    description: str = ""
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> BenchmarkProfile:
        return cls(
            profile_id=str(payload["profile_id"]),
            model_name=str(payload["model_name"]),
            prompt_policy=str(payload["prompt_policy"]),
            benchmark_date=str(payload["benchmark_date"]),
            run_source=BenchmarkRunSource.from_dict(cast(dict[str, Any], payload["run_source"])),
            description=str(payload.get("description", "")),
            tags=tuple(str(item) for item in payload.get("tags", [])),
            metadata=cast(dict[str, Any], payload.get("metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "run_source": self.run_source.to_dict(),
        }

    def to_matrix_entry(self) -> dict[str, str]:
        return {"profile_id": self.profile_id}


@dataclass(frozen=True)
class BenchmarkProfileManifest:
    version: str
    scenarios: tuple[str, ...]
    rubric: str
    profiles: tuple[BenchmarkProfile, ...]
    generated_at: str = ""


def load_benchmark_profile_manifest(path: str | Path) -> BenchmarkProfileManifest:
    payload = cast(dict[str, Any], json.loads(Path(path).read_text(encoding="utf-8")))
    profiles = tuple(BenchmarkProfile.from_dict(cast(dict[str, Any], item)) for item in payload.get("profiles", []))
    return BenchmarkProfileManifest(
        version=str(payload.get("version", "0.1.0")),
        scenarios=tuple(str(item) for item in payload.get("scenarios", [])),
        rubric=str(payload["rubric"]),
        profiles=profiles,
        generated_at=str(payload.get("generated_at", "")),
    )


def get_benchmark_profile(manifest: BenchmarkProfileManifest, profile_id: str) -> BenchmarkProfile:
    for profile in manifest.profiles:
        if profile.profile_id == profile_id:
            return profile
    available = ", ".join(sorted(profile.profile_id for profile in manifest.profiles))
    raise ValueError(f"Unknown benchmark profile_id: {profile_id}. Available profile ids: {available}")


def manifest_to_github_actions_matrix(manifest: BenchmarkProfileManifest) -> dict[str, list[dict[str, str]]]:
    return {"profile": [profile.to_matrix_entry() for profile in manifest.profiles]}
