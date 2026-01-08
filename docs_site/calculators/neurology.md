# Neurology Calculators

Tools for neurological assessment and prognosis.

## Consciousness & Coma

### Glasgow Coma Scale (GCS)

**Tool ID**: `glasgow_coma_scale`

| Component | Score | Response |
|-----------|-------|----------|
| **Eye Opening** | 4 | Spontaneous |
| | 3 | To voice |
| | 2 | To pain |
| | 1 | None |
| **Verbal** | 5 | Oriented |
| | 4 | Confused |
| | 3 | Inappropriate words |
| | 2 | Incomprehensible sounds |
| | 1 | None |
| **Motor** | 6 | Obeys commands |
| | 5 | Localizes pain |
| | 4 | Withdraws from pain |
| | 3 | Flexion to pain |
| | 2 | Extension to pain |
| | 1 | None |

**Severity**:
- 13-15: Mild
- 9-12: Moderate
- 3-8: Severe (intubation often needed)

---

## Stroke

### NIHSS (NIH Stroke Scale)

**Tool ID**: `nihss`

15-item scale for stroke severity.

| Score | Severity |
|-------|----------|
| 0 | No stroke symptoms |
| 1-4 | Minor |
| 5-15 | Moderate |
| 16-20 | Moderate-severe |
| 21-42 | Severe |

---

## Subarachnoid Hemorrhage

### Hunt & Hess Grade

**Tool ID**: `hunt_hess`

Clinical grading of SAH.

| Grade | Criteria | Mortality |
|-------|----------|-----------|
| I | Asymptomatic or mild headache | 1% |
| II | Moderate-severe headache, nuchal rigidity | 5% |
| III | Drowsy, confused, mild focal deficit | 19% |
| IV | Stupor, moderate hemiparesis | 42% |
| V | Coma, decerebrate posturing | 77% |

---

### Fisher Grade

**Tool ID**: `fisher_grade`

CT grading for vasospasm risk.

| Grade | CT Findings | Vasospasm Risk |
|-------|-------------|----------------|
| 1 | No blood | Low |
| 2 | Diffuse thin (<1mm) | Low |
| 3 | Localized clot or thick (>1mm) | High |
| 4 | Intraventricular/parenchymal | Moderate |

---

## Intracerebral Hemorrhage

### ICH Score

**Tool ID**: `ich_score`

30-day mortality prediction for ICH.

| Factor | Points |
|--------|--------|
| GCS 3-4 | 2 |
| GCS 5-12 | 1 |
| GCS 13-15 | 0 |
| Age ≥80 | 1 |
| ICH volume ≥30mL | 1 |
| Intraventricular hemorrhage | 1 |
| Infratentorial origin | 1 |

| Score | 30-day Mortality |
|-------|-----------------|
| 0 | 0% |
| 1 | 13% |
| 2 | 26% |
| 3 | 72% |
| 4 | 97% |
| 5-6 | 100% |
