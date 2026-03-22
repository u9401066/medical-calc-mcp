# Benchmark Source Scouting Plan

> Status: Initial scouting and intake plan
> Scope: Public benchmark sources for medical tool-use and workflow evaluation
> Last Updated: 2026-03-21

## Goal

Build a public, reproducible benchmark pipeline for medical tool use.

The target is not only calculator correctness. The target is agent task performance across:

- tool selection
- parameter extraction
- missing-data questioning
- workflow sequencing
- uncertainty handling
- recommendation restraint

## Search Surfaces

### GitHub Categories

1. Official benchmark repositories
   - Author-maintained repos tied to papers or organizations.
2. Dataset release repositories
   - Repos that publish raw CSV, JSON, JSONL, or parquet artifacts.
3. Evaluation harness repositories
   - Repos that encode scoring logic, task rubrics, or tool-use traces.
4. Conversion and mirror repositories
   - High-trust community repos that normalize official datasets without changing labels.
5. Workflow and guideline task repos
   - Repos that encode sepsis, preoperative, AKI, delirium, or GI bleed workflows.

### Hugging Face Categories

1. Official dataset releases
   - Dataset cards published by the original authors or organizations.
2. High-trust community mirrors
   - Verified, documented conversions of official datasets.
3. Medical QA datasets with clinical vignettes
   - Useful for prompt and extraction stress-testing even if not tool-use native.
4. Tool-calling and slot-filling datasets
   - Indirect but useful for evaluation dimensions like schema adherence and argument extraction.

## Search Keywords

### Core Keywords

- medical calculator benchmark
- MedCalc-Bench
- clinical decision support benchmark
- medical tool use benchmark
- medical function calling benchmark
- clinical workflow benchmark
- clinical scenario benchmark
- de-identified clinical vignette dataset

### Workflow Keywords

- sepsis workflow benchmark
- ICU delirium benchmark
- preoperative risk benchmark
- upper GI bleeding benchmark
- AKI benchmark
- sedation assessment benchmark

### Extraction and Tooling Keywords

- clinical parameter extraction dataset
- medical slot filling benchmark
- function calling medical
- tool calling healthcare
- structured output clinical benchmark

### Host-Specific Query Patterns

#### GitHub

- MedCalc-Bench dataset benchmark medical
- clinical workflow evaluation benchmark
- sepsis guideline dataset benchmark
- function calling benchmark medical

#### Hugging Face

- medcalc
- medical benchmark
- pubmedqa
- medqa
- tool calling
- clinical notes benchmark

## Intake Policy

### Inclusion Rules

A source can enter the registry when it meets all required rules:

1. Provenance is clear.
   - Paper, author, lab, organization, or benchmark owner is identifiable.
2. License is clear enough for benchmark use.
   - Public redistribution or benchmark evaluation is allowed.
3. Data are safe to handle.
   - Synthetic, de-identified, or explicitly public case material only.
4. Task definition is reproducible.
   - Inputs, labels, scoring logic, or evaluation target are inspectable.
5. Schema conversion is feasible.
   - Can be mapped into scenario records without hidden assumptions.

### Preferred Properties

- official or author-maintained
- stable versioning
- documented splits
- clear label semantics
- explicit evaluation protocol
- realistic clinical context
- compatibility with public artifact release

### Exclusion Rules

Do not ingest or publish sources when any of the following are true:

1. License is missing or incompatible.
2. Source is scraped from proprietary clinical websites.
3. Patient privacy status is unclear.
4. Labels or methodology cannot be audited.
5. Community mirror changes labels without documentation.
6. Dataset is mostly duplicate content from another registered source.
7. Benchmark requires credentials or usage terms that block public redistribution.

## Registry States

Each candidate source should be tracked in one of these states:

- scouting: discovered but not verified
- candidate: verified enough for manual review
- active: approved for ingestion or benchmarking
- restricted: useful internally but cannot be redistributed
- excluded: rejected with reason recorded

## Source Prioritization

### Priority 1: Direct Benchmark Inputs

These map directly to public benchmark scenarios:

- official medical calculator benchmarks
- high-trust mirrors of those benchmarks
- explicit workflow scenario datasets

### Priority 2: Indirect Benchmark Inputs

These are useful for sub-dimensions of the benchmark:

- medical QA vignette datasets
- function-calling benchmarks
- slot-filling datasets

### Priority 3: Restricted Research Inputs

These may inform rubric design but should not be in the public release:

- credential-gated clinical note corpora
- institution-specific workflow datasets

## First Release Scope

The first public release should prioritize sources that can support:

1. calculator execution scenarios
2. parameter extraction scenarios
3. workflow sequencing scenarios

Recommended first-wave source mix:

- 1 official direct calculator benchmark
- 1 high-trust mirror of that benchmark
- 1 to 2 medical vignette datasets for indirect scenario synthesis
- 1 tool-calling benchmark for argument-structure stress tests

## Acceptance Review Checklist

Before promoting a source to active, confirm:

- provenance verified
- license recorded
- URL pinned
- host recorded
- source type categorized
- task fit classified as direct or indirect
- ingestion path defined
- conversion assumptions documented

## Conversion Targets

Every accepted source should eventually map into the internal scenario schema with:

- scenario_id
- source_id
- task_family
- clinical_prompt
- available_data
- hidden_data
- gold_workflow
- expected_tools
- expected_params
- expected_result
- safety_checks
- expected_output_traits
- provenance

## Initial Execution Loop

1. Search GitHub for official benchmark repos.
2. Search Hugging Face for official or high-trust mirrors.
3. Cross-check paper, host, and license.
4. Add source to the registry with state and notes.
5. Run ingestion on a small sample.
6. Inspect conversion quality before scaling.

## Success Criterion

This scouting plan is working if the project can continuously answer:

- Which public sources are trustworthy?
- Which sources are legally usable?
- Which sources map directly into tool-use scenarios?
- Which sources only support indirect evaluation dimensions?
- Which sources are ready for public benchmark release today?