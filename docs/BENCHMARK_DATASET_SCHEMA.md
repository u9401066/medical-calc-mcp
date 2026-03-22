# Benchmark Dataset Schema

> Status: HF-style dataset schema and split reference
> Primary dataset path: data/benchmarks/medical_calc_mcp_hf_v1/

## Files

- release/public-dev/train.jsonl: public train split for distribution
- release/public-dev/validation.jsonl: public validation split for distribution
- release/public-dev/public-dev.jsonl: combined public development bundle
- release/hidden-test/hidden-test.jsonl: private held-out benchmark bundle
- metadata.json: aggregate counts and coverage summary
- coverage_audit.json: machine-readable coverage audit
- release_manifest.json: release packaging manifest with file hashes and git segments
- README.md: HF-style dataset card
- RELEASE_CHECKLIST.md: release/push checklist for public vs hidden packaging

Internal compatibility files generated locally and typically withheld from a single public remote:

- all.jsonl: full normalized dataset
- train.jsonl: internal training split mirror
- validation.jsonl: internal validation split mirror
- test.jsonl: internal held-out evaluation split

## Record Schema

Each JSONL row is a normalized calculator benchmark case and is intentionally compatible with the existing benchmark loader for normalized-jsonl.

Required fields:

- case_id: stable case identifier
- source: dataset source label
- split: train, validation, or test
- question: natural-language benchmark prompt
- tool_id: canonical Medical-Calc-MCP tool id
- calculator_name: human-readable calculator name
- params: structured input payload used for calculation
- expected_value: grounded numeric answer

Optional compatibility fields:

- abs_tolerance: absolute tolerance for floating-point comparison
- lower_limit: acceptable lower bound
- upper_limit: acceptable upper bound

Metadata fields used for analysis and HF packaging:

- primary_specialty: primary specialty label from tool metadata
- specialties: all mapped specialties from tool metadata
- guideline_domains: 2023-2025 guideline domains associated with the tool
- formula_source_type: original, guideline, or derived
- task_family: calculator_execution
- setting: general
- references: Vancouver-style reference metadata from the calculator registry
- provenance: source test file, test name, source line number, calculator class name

## Split Policy

- Splits are deterministic and generated from the sorted validated case list.
- Target ratio is 70% train, 15% validation, 15% test.
- Test split is rebalanced so all 16 guideline domains appear at least once.
- Public release exposes only train plus validation as the public-dev bundle.
- Hidden-test release is derived from the internal test split and renamed to `hidden_test` inside the private bundle.

## Release Packaging

- `release/public-dev/` is the publishable Hugging Face style package.
- `release/hidden-test/` is the stricter private evaluation package.
- `release_manifest.json` records counts, file hashes, and recommended public/private git path segments.
- For a single public Git remote, push only the public-dev bundle plus `README.md`, `metadata.json`, and `coverage_audit.json`.

## Validation Rules

- Only cases extracted from successful calculator test calls are retained.
- Only numeric calculator outputs are included.
- Cases from tests with invalid/error-oriented names are excluded.
- Duplicate cases by tool_id plus canonical params are removed.
- Dataset generation fails if fewer than 500 valid cases remain.
- Dataset generation fails if any of the 16 guideline domains are uncovered.

## Benchmark Interoperability

The dataset can be converted into AgentBenchmarkScenario JSONL with:

```bash
uv run python scripts/benchmark_ingest.py \
  --dataset data/benchmarks/medical_calc_mcp_hf_v1/all.jsonl \
  --source-id medical_calc_mcp_hf_v1 \
  --registry data/benchmarks/source_registry.json \
  --input-format normalized-jsonl \
  --output /tmp/medical-calc-mcp-hf-v1-scenarios.jsonl
```

## Counting Cases

Use the reusable count function in src/shared/hf_benchmark_dataset.py or the CLI:

```bash
uv run python scripts/count_benchmark_cases.py data/benchmarks/medical_calc_mcp_hf_v1/all.jsonl
```
