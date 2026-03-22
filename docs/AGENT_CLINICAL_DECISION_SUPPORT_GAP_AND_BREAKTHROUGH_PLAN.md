# Agent Clinical Decision Support Gap & Breakthrough Plan

> Status: Strategic design document
> Scope: Post-calculator evolution of Medical-Calc-MCP
> Last Updated: 2026-03-21

## Executive Summary

Medical-Calc-MCP has already solved an important layer of the clinical decision-support problem: reliable symbolic execution of validated medical calculators with schema-first access, evidence traceability, and agent-friendly discovery. That layer matters because even high-end LLMs remain brittle at formula selection, threshold fidelity, arithmetic consistency, and auditability.

However, a 150+ calculator platform is not yet the same thing as a strong agentic clinical decision-support system. The current platform is best understood as a validated decision component library. The next breakthrough does not primarily come from adding more isolated calculators. It comes from turning those calculators into workflow-aware, uncertainty-aware, protocol-aware decision support.

This document defines:

1. What the project already solves well.
2. What critical gaps remain.
3. What architectural breakthroughs should be prioritized next.
4. How to measure whether those breakthroughs are real.

## Why So Many Medical Scores Exist

Medical scoring systems exist because clinical decision-making is not one monolithic task. It is a sequence of narrower tasks with different objectives:

- risk stratification
- severity estimation
- prognosis
- triage
- treatment threshold selection
- medication dosing
- monitoring frequency
- escalation or referral triggers

Each score compresses a specific piece of clinical evidence, consensus, or statistical modeling into a repeatable rule. Their value is not merely convenience. Their value is standardization, reproducibility, teachability, and auditability.

For AI agents, this matters even more. A model may reason fluently about a patient, but still fail on:

- using the wrong calculator version
- hallucinating a threshold
- omitting a required variable
- performing incorrect arithmetic
- failing to cite the evidence source

Therefore, a broad score library is not redundant with advanced LLM reasoning. It is the symbolic substrate that makes reasoning safer and more reviewable.

## What Medical-Calc-MCP Already Solves Well

The current platform is strong in six areas:

1. Validated symbolic calculation
   - Formulas are explicit, tested, and versionable.
2. Schema-first tool access
   - Agents can inspect exact input requirements before execution.
3. Discovery and tool retrieval
   - Agents do not need to guess tool ids blindly.
4. Evidence traceability
   - Calculators are linked to PMID/DOI-backed references.
5. Boundary validation
   - Clinically impossible or implausible inputs can be surfaced.
6. Agent integration surface
   - MCP, REST, prompts, and registry metadata make the system usable by general-purpose agents.

These are foundational. They reduce hallucination and increase reproducibility. They do not yet fully solve end-to-end decision support.

## The Real Remaining Gaps

The highest-value gaps are no longer primarily about missing formulas. They are about missing orchestration and missing clinical state.

### Gap 1: Workflow Completeness

Current state:

- Tools are strong individually.
- Multi-step clinical workflows still depend heavily on the agent's own ad hoc planning.

Problem:

- A sepsis workflow is not just qSOFA and SOFA.
- A preoperative workflow is not just ASA and RCRI.
- A GI bleeding workflow is not just GBS and Rockall.

Missing capability:

- explicit branching workflows
- precondition enforcement
- step ordering
- stop conditions
- escalation conditions

### Gap 2: Temporal and Longitudinal State

Current state:

- Most tools operate on a single snapshot.

Problem:

- Many clinical decisions are fundamentally time-series decisions.
- SOFA trend, AKI progression, delirium evolution, ventilator weaning readiness, and shock response cannot be reliably summarized by one isolated calculation.

Missing capability:

- patient-state memory across timepoints
- trend-aware calculators and workflow logic
- repeat-interval recommendations
- change detection and alerting thresholds

### Gap 3: Missing-Data Interrogation

Current state:

- The system can say a parameter is missing.

Problem:

- Agents need to know which missing value matters most for the next decision.
- Clinically, the right move is often to ask one highly informative question rather than request every field.

Missing capability:

- ranked follow-up questions
- information gain oriented prompts
- “minimum viable next step” guidance

### Gap 4: Uncertainty and Fragility Awareness

Current state:

- Tools return results and interpretations.

Problem:

- Most outputs do not yet express decision fragility.
- A clinician needs to know when a result is stable versus when one uncertain parameter could reverse the conclusion.

Missing capability:

- parameter sensitivity flags
- confidence conditions
- contradiction detection
- “do not over-call” guardrails

### Gap 5: Local Protocol Alignment

Current state:

- The system is evidence-based and generally guideline-aware.

Problem:

- Real care is governed by local protocols, formularies, workflow ownership, escalation norms, and documentation expectations.
- A universally correct score can still produce a locally incomplete recommendation.

Missing capability:

- institution-specific overlays
- configurable policy thresholds
- local action mapping after score calculation

### Gap 6: EHR/FHIR and Upstream Data Quality

Current state:

- The platform assumes reasonably structured inputs.

Problem:

- Real agent performance often fails upstream, during extraction from messy notes, flowsheets, scanned documents, or fragmented records.

Missing capability:

- stronger structured-data ingestion contracts
- FHIR mapping
- provenance for extracted parameters
- “source confidence” and value conflict detection

### Gap 7: Human Oversight Integration

Current state:

- The system is designed for assistance, not autonomy.

Problem:

- The platform does not yet fully model the human-in-the-loop operational layer: override reasons, disagreement capture, escalation, and review burden.

Missing capability:

- explicit clinician review checkpoints
- override logging
- acceptance and rejection analytics
- feedback loops into benchmark design

## Strategic Reframe

The project should evolve from:

- “validated calculator platform”

to:

- “transparent, evidence-linked, human-supervised clinical decision copilot infrastructure”

That shift changes the next priority from calculator count to decision support quality.

## Breakthrough Directions

### Breakthrough 1: Clinical Workflow Engine

Add a first-class workflow layer above individual calculators.

Core features:

- step graph with prerequisites
- branching logic
- stopping rules
- escalation triggers
- required-vs-optional data for each step
- workflow-level summaries

Representative workflows:

- sepsis evaluation
- ICU daily review
- preoperative risk assessment
- upper GI bleed triage
- AKI evaluation
- sedation and delirium monitoring

### Breakthrough 2: Decision-State Memory

Introduce patient-state and encounter-state objects rather than treating every call as isolated.

Core features:

- timepoint snapshots
- state diffs
- trend summaries
- unresolved question tracking
- workflow checkpoint persistence

### Breakthrough 3: Uncertainty Layer

Add machine-readable uncertainty outputs.

Core features:

- missing critical inputs
- contradictory inputs
- sensitive thresholds
- confidence conditions
- “safe to proceed” vs “must verify” labels

### Breakthrough 4: Protocol Overlay Layer

Support institution-specific execution rules while preserving the evidence base.

Core features:

- local action bundles
- configurable escalation thresholds
- team ownership routing
- local formulary or care pathway notes

### Breakthrough 5: Evidence-to-Action Mapping

Move beyond score outputs into score-to-decision transitions.

Core features:

- score interpretation to next-step mapping
- contraindication reminders
- balancing competing risks
- explicit “what this does not prove” guidance

### Breakthrough 6: Benchmark-Driven Product Loop

Every new capability should be driven by task-level evaluation, not by feature intuition alone.

The key shift is:

- from unit correctness
- to end-to-end task completion, safety capture, and human usefulness

## Priority Plan

### Phase 1: Next 90 Days

1. Publish formal end-to-end benchmark spec for agent clinical task execution.
2. Encode 3 to 5 canonical workflows as explicit machine-readable graphs.
3. Add ranked missing-data question generation for those workflows.
4. Add workflow-level outputs with uncertainty and escalation signals.

### Phase 2: 3 to 6 Months

1. Add patient-state timeline support for longitudinal workflows.
2. Add protocol overlays for at least one demonstration site profile.
3. Add extraction provenance fields for all benchmarked parameters.
4. Introduce workflow completion metrics into CI or scheduled eval jobs.

### Phase 3: 6 to 12 Months

1. Run shadow-mode evaluations against realistic clinical notes.
2. Measure clinician agreement, override rates, and escalation usefulness.
3. Publish comparative results versus direct LLM reasoning and calculator-only baselines.

## What “Best Possible Today” Actually Means

The project is not at the ceiling of what current technology can do.

It is strong at symbolic correctness.
It is not yet state of the art at full decision orchestration.

The strongest feasible position for the next version is:

- LLM for language understanding and hypothesis generation
- MCP for evidence-backed symbolic execution
- workflow engine for process discipline
- uncertainty layer for calibrated restraint
- human review layer for accountable decision support

That combination is much stronger than either:

- raw LLM reasoning alone
- or a flat calculator catalog alone

## What This Project Should Explicitly Not Claim

To stay scientifically and operationally honest, the platform should not claim that:

- 150+ calculators equal autonomous diagnostic competence
- benchmark gains automatically imply clinical safety
- score correctness alone solves medical decision support

The right claim is narrower and stronger:

- the platform improves the reliability, transparency, and structure of agent-assisted clinical reasoning in bounded decision tasks

## Success Criteria

This strategy should be considered successful only if the project can demonstrate measurable gains in:

1. task completion accuracy
2. correct workflow sequencing
3. critical missing-data questioning
4. unsafe-input capture
5. recommendation appropriateness
6. clinician trust and override calibration

## Immediate Deliverables Triggered by This Plan

This document implies four concrete repo tasks:

1. Define the end-to-end benchmark around agent clinical tasks.
2. Implement workflow graph schemas for key care pathways.
3. Add uncertainty and escalation outputs to workflow execution.
4. Add evaluation infrastructure that goes beyond calculator correctness.

## Bottom Line

The next breakthrough is not “more formulas.”

The next breakthrough is turning Medical-Calc-MCP into a workflow-aware, uncertainty-aware, protocol-aware clinical decision support substrate for agents.

That is the most credible path from a strong calculator MCP to a serious clinical decision copilot platform.
