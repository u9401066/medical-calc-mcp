# Cardiology Calculators

Calculators for cardiovascular risk assessment and management.

## Atrial Fibrillation

### CHA₂DS₂-VASc Score

Stroke risk in atrial fibrillation.

**Tool ID**: `chads2_vasc`

| Factor | Points |
|--------|--------|
| Congestive heart failure | 1 |
| Hypertension | 1 |
| Age ≥75 | 2 |
| Diabetes | 1 |
| Stroke/TIA/thromboembolism | 2 |
| Vascular disease | 1 |
| Age 65-74 | 1 |
| Sex (female) | 1 |

**Anticoagulation Recommendations**:

| Score | Risk | Recommendation |
|-------|------|----------------|
| 0 (male) / 1 (female) | Low | No anticoagulation |
| 1 (male) | Moderate | Consider anticoagulation |
| ≥2 | High | Anticoagulation recommended |

---

### HAS-BLED Score

Bleeding risk with anticoagulation.

**Tool ID**: `has_bled`

!!! tip "Clinical Pearl"
    Always calculate both CHA₂DS₂-VASc AND HAS-BLED for AF patients

| Factor | Points |
|--------|--------|
| Hypertension (uncontrolled) | 1 |
| Abnormal renal/liver function | 1-2 |
| Stroke | 1 |
| Bleeding history | 1 |
| Labile INR | 1 |
| Elderly (>65) | 1 |
| Drugs/Alcohol | 1-2 |

---

## Acute Coronary Syndrome

### HEART Score

Risk stratification for chest pain.

**Tool ID**: `heart_score`

| Component | 0 | 1 | 2 |
|-----------|---|---|---|
| History | Slightly suspicious | Moderately suspicious | Highly suspicious |
| ECG | Normal | Non-specific changes | Significant ST deviation |
| Age | <45 | 45-64 | ≥65 |
| Risk factors | None | 1-2 | ≥3 or known CAD |
| Troponin | Normal | 1-3× normal | >3× normal |

**Risk Stratification**:
- 0-3: Low risk (1.7% MACE)
- 4-6: Intermediate risk (16.6% MACE)
- 7-10: High risk (50.1% MACE)

---

### TIMI Risk Score (STEMI)

**Tool ID**: `timi_stemi`

Mortality prediction after STEMI.

---

### TIMI Risk Score (NSTEMI/UA)

**Tool ID**: `timi_nstemi`

14-day risk of death, MI, or urgent revascularization.

---

## Heart Failure

### NYHA Functional Class

**Tool ID**: `nyha_class`

| Class | Description |
|-------|-------------|
| I | No limitation |
| II | Slight limitation |
| III | Marked limitation |
| IV | Symptoms at rest |

---

## Other Cardiology Tools

| Tool | ID | Purpose |
|------|----|---------|
| Wells PE | `wells_pe` | PE probability |
| Wells DVT | `wells_dvt` | DVT probability |
| GRACE Score | `grace_score` | ACS mortality |
| Framingham | `framingham` | 10-year CVD risk |
| ASCVD Risk | `ascvd_risk` | Atherosclerotic CVD risk |
