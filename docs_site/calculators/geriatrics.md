# Geriatrics Calculators

Tools for comprehensive geriatric assessment including cognitive, functional, nutritional, and frailty evaluation.

## Cognitive Assessment

### MMSE (Mini-Mental State Examination)

The gold standard for cognitive screening.

**Tool ID**: `mmse`

| Domain | Max Points |
|--------|------------|
| Orientation (time) | 5 |
| Orientation (place) | 5 |
| Registration | 3 |
| Attention/Calculation | 5 |
| Recall | 3 |
| Language | 8 |
| Visuospatial | 1 |
| **Total** | **30** |

**Interpretation**:

| Score | Interpretation |
|-------|----------------|
| 24-30 | Normal |
| 20-23 | Mild cognitive impairment |
| 10-19 | Moderate cognitive impairment |
| <10 | Severe cognitive impairment |

!!! note "Education Adjustment"
    Consider education level when interpreting scores

---

### MoCA (Montreal Cognitive Assessment)

More sensitive than MMSE for mild cognitive impairment.

**Tool ID**: `moca`

**Domains assessed**:
- Visuospatial/Executive
- Naming
- Memory
- Attention
- Language
- Abstraction
- Delayed recall
- Orientation

**Interpretation**:
- ≥26: Normal
- <26: Cognitive impairment (add 1 point if ≤12 years education)

---

## Functional Assessment

### Barthel Index (ADL)

Assessment of activities of daily living.

**Tool ID**: `barthel_index`

| Activity | Score Range |
|----------|-------------|
| Feeding | 0-10 |
| Bathing | 0-5 |
| Grooming | 0-5 |
| Dressing | 0-10 |
| Bowel control | 0-10 |
| Bladder control | 0-10 |
| Toilet use | 0-10 |
| Transfers | 0-15 |
| Mobility | 0-15 |
| Stairs | 0-10 |
| **Total** | **0-100** |

**Interpretation**:
- 100: Independent
- 80-99: Minimal dependence
- 60-79: Mild dependence
- 40-59: Moderate dependence
- 20-39: Severe dependence
- <20: Total dependence

---

### TUG (Timed Up and Go)

Simple mobility and fall risk assessment.

**Tool ID**: `tug`

**Procedure**: Time (in seconds) to rise from chair, walk 3 meters, turn, walk back, sit down.

| Time | Interpretation |
|------|----------------|
| <10s | Normal |
| 10-14s | Mildly impaired |
| 14-20s | Moderate impairment, increased fall risk |
| >20s | Severe impairment, high fall risk |

---

## Frailty

### Clinical Frailty Scale (CFS)

**Tool ID**: `cfs`

| Score | Category | Description |
|-------|----------|-------------|
| 1 | Very fit | Robust, exercises regularly |
| 2 | Well | Less robust, occasional activity |
| 3 | Managing well | Medical problems controlled |
| 4 | Vulnerable | Not dependent but slowed down |
| 5 | Mildly frail | Needs help with IADLs |
| 6 | Moderately frail | Needs help with ADLs |
| 7 | Severely frail | Completely dependent |
| 8 | Very severely frail | Near end of life |
| 9 | Terminally ill | Life expectancy <6 months |

---

## Nutritional Assessment

### MNA (Mini Nutritional Assessment)

**Tool ID**: `mna`

Screening for malnutrition risk in elderly patients.

| Score | Status |
|-------|--------|
| ≥12 | Normal nutritional status |
| 8-11 | At risk of malnutrition |
| <8 | Malnourished |

**Screening Questions**:
- Food intake decline
- Weight loss
- Mobility
- Psychological stress
- Neuropsychological problems
- BMI or calf circumference
