# Benchmark Usage Guide

> Status: Operational guide
> Scope: How to use the benchmark datasets, profiles, trace adapters, and reporting pipeline
> Last Updated: 2026-03-23

## Overview

The benchmark stack now has three layers:

1. Source ingestion
2. Workflow-native scenario evaluation
3. HF-style calculator dataset generation
4. Versioned profile execution and reporting

This guide explains what lives where and how to run the pipeline end to end.

## Dataset Layout

### Source Registry

Public and project-authored sources are tracked in:

- `data/benchmarks/source_registry.json`

This registry records source provenance, trust tier, ingestion format, and whether the source is direct or indirect for the benchmark.

The registry now also includes:

- `medical_calc_mcp_hf_v1` for the project-authored HF-style dataset generated from validated test cases.

### HF-Style Calculator Dataset

The generator writes both public release files and internal/private compatibility files.

Public-safe files for a single public remote:

- `data/benchmarks/medical_calc_mcp_hf_v1/release/public-dev/train.jsonl`
- `data/benchmarks/medical_calc_mcp_hf_v1/release/public-dev/validation.jsonl`
- `data/benchmarks/medical_calc_mcp_hf_v1/release/public-dev/public-dev.jsonl`
- `data/benchmarks/medical_calc_mcp_hf_v1/metadata.json`
- `data/benchmarks/medical_calc_mcp_hf_v1/coverage_audit.json`
- `data/benchmarks/medical_calc_mcp_hf_v1/README.md`

Internal/private files typically kept local or pushed only to a private remote:

- `data/benchmarks/medical_calc_mcp_hf_v1/all.jsonl`
- `data/benchmarks/medical_calc_mcp_hf_v1/train.jsonl`
- `data/benchmarks/medical_calc_mcp_hf_v1/validation.jsonl`
- `data/benchmarks/medical_calc_mcp_hf_v1/test.jsonl`
- `data/benchmarks/medical_calc_mcp_hf_v1/release/hidden-test/hidden-test.jsonl`
- `data/benchmarks/medical_calc_mcp_hf_v1/release_manifest.json`
- `data/benchmarks/medical_calc_mcp_hf_v1/RELEASE_CHECKLIST.md`

This dataset is built from successful calculator test invocations and currently provides:

- 500+ validated numeric cases
- split metadata
- guideline domain coverage metadata
- source-test provenance per case
- a public-dev release bundle for publishing
- a stricter hidden-test bundle for private evaluation

### Workflow Scenario Dataset

Workflow-native benchmark scenarios live in:

- `data/agent_decision_bench/scenarios/sepsis_icu.jsonl`
- `data/agent_decision_bench/scenarios/preop_risk.jsonl`
- `data/agent_decision_bench/scenarios/aki_eval.jsonl`
- `data/agent_decision_bench/scenarios/gi_bleed.jsonl`
- `data/agent_decision_bench/scenarios/icu_sedation_delirium.jsonl`

These scenarios encode:

- clinical prompt
- visible vs hidden data
- gold workflow
- expected tools and params
- critical questions
- safety signals
- output trait expectations

### Sample Run Inputs

Sample benchmark inputs live in:

- `data/agent_decision_bench/sample_runs/mixed_agent_runs.jsonl`
- `data/agent_decision_bench/sample_runs/mcp_session_events.jsonl`
- `data/agent_decision_bench/sample_runs/mcp_session_transcript.jsonl`
- `data/agent_decision_bench/sample_runs/session_mapping.json`

The project currently supports three run-input styles:

1. Hand-authored agent runs
2. ToolUsageEvent JSONL traces
3. MCP transcript JSONL traces with `discover`, `get_tool_schema`, and `calculate`

### Versioned Benchmark Profiles

Profiles are versioned in:

- `data/agent_decision_bench/profiles/manifest.json`

Each profile captures:

- `profile_id`
- `model_name`
- `prompt_policy`
- `benchmark_date`
- `run_source`

This is the canonical place to version benchmark comparisons.

## Core Commands

### 1. Ingest External Dataset Into Scenario Schema

```bash
uv run python scripts/benchmark_ingest.py \
  --dataset data/benchmarks/medcalc_bench_sample.csv \
  --source-id medcalc_bench_official \
  --registry data/benchmarks/source_registry.json \
  --output /tmp/ingested-scenarios.jsonl \
  --summary-json /tmp/ingest-summary.json
```

Use this when converting an external benchmark source into the project scenario schema.

### 1.5. Build the Project HF-Style Dataset

```bash
uv run python scripts/build_hf_benchmark_dataset.py
```

Use this when regenerating the project-authored 500+ case dataset from validated test inputs.

The same command now also writes a release-ready bundle with:

- `release/public-dev/` for public distribution
- `release/hidden-test/` for private evaluation
- `release_manifest.json` for path segmentation and file hashes

If the repository has only one public remote, push only `release/public-dev/` plus the dataset card and summary metadata.

### 1.6. Count Dataset Cases

```bash
uv run python scripts/count_benchmark_cases.py \
  data/benchmarks/medical_calc_mcp_hf_v1/all.jsonl --json
```

Use this for a quick total-case and split-count check.

### 2. Adapt Raw MCP Trace Into Agent Run JSONL

#### ToolUsageEvent trace

```bash
uv run python scripts/benchmark_adapt_mcp_trace.py \
  --trace-log data/agent_decision_bench/sample_runs/mcp_session_events.jsonl \
  --trace-format tool_usage_event \
  --scenarios \
  data/agent_decision_bench/scenarios/sepsis_icu.jsonl \
  data/agent_decision_bench/scenarios/preop_risk.jsonl \
  data/agent_decision_bench/scenarios/aki_eval.jsonl \
  data/agent_decision_bench/scenarios/gi_bleed.jsonl \
  data/agent_decision_bench/scenarios/icu_sedation_delirium.jsonl \
  --session-mapping data/agent_decision_bench/sample_runs/session_mapping.json \
  --output /tmp/adapted-runs.jsonl \
  --summary-json /tmp/trace-summary.json
```

#### MCP transcript trace

```bash
uv run python scripts/benchmark_adapt_mcp_trace.py \
  --trace-log data/agent_decision_bench/sample_runs/mcp_session_transcript.jsonl \
  --trace-format mcp_transcript \
  --scenarios \
  data/agent_decision_bench/scenarios/sepsis_icu.jsonl \
  data/agent_decision_bench/scenarios/preop_risk.jsonl \
  data/agent_decision_bench/scenarios/aki_eval.jsonl \
  data/agent_decision_bench/scenarios/gi_bleed.jsonl \
  data/agent_decision_bench/scenarios/icu_sedation_delirium.jsonl \
  --output /tmp/adapted-transcript-runs.jsonl \
  --summary-json /tmp/transcript-summary.json
```

Use this when you want a normalized agent-run file before evaluation.

### 3. Evaluate Agent Runs Directly

```bash
uv run python scripts/benchmark_eval_agent_runs.py \
  --scenarios \
  data/agent_decision_bench/scenarios/sepsis_icu.jsonl \
  data/agent_decision_bench/scenarios/preop_risk.jsonl \
  data/agent_decision_bench/scenarios/aki_eval.jsonl \
  data/agent_decision_bench/scenarios/gi_bleed.jsonl \
  data/agent_decision_bench/scenarios/icu_sedation_delirium.jsonl \
  --runs data/agent_decision_bench/sample_runs/mixed_agent_runs.jsonl \
  --summary-json /tmp/benchmark-summary.json
```

Use this if you already have agent-run JSONL.

### 4. Run a Versioned Benchmark Profile

```bash
uv run python scripts/benchmark_run_profile.py \
  --manifest data/agent_decision_bench/profiles/manifest.json \
  --profile-id sample_transcript_trace \
  --output-dir /tmp/benchmark-profile-transcript
```

This is now the preferred entry point for reproducible benchmark execution.

It will:

- resolve scenarios from the manifest
- load the rubric from the manifest
- load direct runs or adapt traces automatically
- emit a profile bundle and summary JSON

### 5. Build Leaderboard and Time Series Reports

```bash
uv run python scripts/benchmark_build_reports.py \
  --inputs /tmp/benchmark-profile-full /tmp/benchmark-profile-transcript \
  --leaderboard-md /tmp/benchmark-leaderboard.md \
  --time-series-json /tmp/benchmark-time-series.json \
  --report-index-json /tmp/benchmark-report-index.json
```

This aggregates profile bundles into:

- markdown leaderboard
- JSON time series
- combined report index JSON

### 6. Build Coverage Audit

```bash
uv run python scripts/build_benchmark_coverage_audit.py
```

This writes:

- `docs/BENCHMARK_COVERAGE_AUDIT.md`
- `data/benchmarks/medical_calc_mcp_hf_v1/coverage_audit.json`

The audit compares the original workflow benchmark with the expanded HF-style dataset.

## Recommended End-to-End Flow

For ongoing benchmarking, use this sequence:

1. Build or refresh the HF-style dataset with `scripts/build_hf_benchmark_dataset.py`
2. Verify `release/public-dev/` and `release/hidden-test/` were regenerated with the expected counts
3. Run `scripts/build_benchmark_coverage_audit.py` to confirm 500+ cases and 16-domain coverage
4. Convert the dataset to scenario JSONL with `scripts/benchmark_ingest.py` when needed
5. Add or update benchmark profiles in `data/agent_decision_bench/profiles/manifest.json`
6. Run each profile with `scripts/benchmark_run_profile.py`
7. Aggregate outputs with `scripts/benchmark_build_reports.py`
8. Use `data/benchmarks/medical_calc_mcp_hf_v1/RELEASE_CHECKLIST.md` when doing segmented git add/commit/push

## CI and Nightly Automation

### CI Smoke Coverage

`.github/workflows/ci.yml` now smoke-tests:

- direct run profile
- ToolUsageEvent trace profile
- MCP transcript trace profile
- reporting pipeline

### Nightly Tracking

`.github/workflows/benchmark-nightly.yml` now:

1. reads the benchmark profile manifest
2. expands the profile matrix dynamically
3. runs every profile
4. uploads per-profile artifacts
5. builds a markdown leaderboard and JSON time series

## Artifact Semantics

### Per-profile output directory

Each profile run emits:

- `benchmark-summary-<profile_id>.json`
- `profile-result-<profile_id>.json`
- optionally `adapted-runs-<profile_id>.jsonl`
- optionally `trace-adaptation-<profile_id>.json`

### Aggregate reporting output

The reporting layer emits:

- `benchmark-leaderboard.md`
- `benchmark-time-series.json`
- `benchmark-report-index.json`

## When To Use Which Entry Point

Use `benchmark_ingest.py` when:

- you are bringing in a new external dataset

Use `benchmark_adapt_mcp_trace.py` when:

- you want to inspect or debug raw trace-to-run adaptation by itself

Use `benchmark_eval_agent_runs.py` when:

- you already have run JSONL and only need scoring

Use `benchmark_run_profile.py` when:

- you want reproducible, versioned benchmark execution

Use `benchmark_build_reports.py` when:

- you want ranking and historical tracking artifacts

Use `build_hf_benchmark_dataset.py` when:

- you want to regenerate the 500+ case calculator dataset from validated test cases

Use `build_benchmark_coverage_audit.py` when:

- you want to verify total case count, domain coverage, and benchmark release readiness

## Current Sample Profiles

The manifest currently includes:

1. `sample_full_policy`
2. `sample_tool_usage_trace`
3. `sample_transcript_trace`

These are reference profiles for validating the pipeline structure. They are not intended to represent a final production leaderboard.

## Related Docs

- `docs/BENCHMARK_DATASET_SCHEMA.md`
- `docs/BENCHMARK_COVERAGE_AUDIT.md`
- `data/benchmarks/medical_calc_mcp_hf_v1/README.md`
