# Anesthesiology Calculators

Preoperative assessment and perioperative risk stratification tools.

## Preoperative Assessment

### ASA Physical Status

**Tool ID**: `asa_physical_status`

| Class | Definition | Example |
|-------|------------|---------|
| ASA I | Healthy | Healthy, non-smoking |
| ASA II | Mild systemic disease | Well-controlled DM, HTN, obesity |
| ASA III | Severe systemic disease | Poorly controlled DM, COPD on home O₂ |
| ASA IV | Life-threatening disease | Recent MI, sepsis, DIC |
| ASA V | Moribund | Ruptured AAA, massive trauma |
| ASA VI | Brain death | Organ donor |

Add "E" suffix for emergency surgery.

---

### RCRI (Revised Cardiac Risk Index)

Cardiac risk for non-cardiac surgery.

**Tool ID**: `rcri`

**Risk Factors** (1 point each):
1. High-risk surgery (intrathoracic, intraperitoneal, suprainguinal vascular)
2. Ischemic heart disease
3. Heart failure
4. Cerebrovascular disease
5. Insulin-dependent diabetes
6. Creatinine >2.0 mg/dL

| Points | Cardiac Event Risk |
|--------|-------------------|
| 0 | 0.4% |
| 1 | 0.9% |
| 2 | 6.6% |
| ≥3 | 11% |

---

## Airway Assessment

### Mallampati Score

**Tool ID**: `mallampati_score`

| Class | View |
|-------|------|
| I | Full uvula, tonsils, soft palate |
| II | Upper uvula, soft palate |
| III | Soft and hard palate only |
| IV | Hard palate only |

Higher class = higher intubation difficulty risk.

---

### STOP-BANG

OSA screening.

**Tool ID**: `stop_bang`

| Criterion | |
|-----------|---|
| **S**noring | Loud snoring |
| **T**ired | Daytime fatigue |
| **O**bserved | Witnessed apnea |
| **P**ressure | Hypertension |
| **B**MI | >35 kg/m² |
| **A**ge | >50 years |
| **N**eck | >40 cm (male), >38 cm (female) |
| **G**ender | Male |

| Score | OSA Risk |
|-------|----------|
| 0-2 | Low |
| 3-4 | Intermediate |
| 5-8 | High |

---

## Perioperative

### Aldrete Score

Post-anesthesia recovery assessment.

**Tool ID**: `aldrete_score`

| Parameter | 0 | 1 | 2 |
|-----------|---|---|---|
| Activity | Unable | Moves 2 extremities | Moves 4 extremities |
| Respiration | Apneic | Dyspnea | Deep breath, cough |
| Circulation | BP ±50% | BP ±20-50% | BP ±20% |
| Consciousness | Unresponsive | Arousable | Fully awake |
| O₂ Saturation | <90% | 90-92% | >92% |

Score ≥9 typically required for PACU discharge.

---

### MABL (Maximum Allowable Blood Loss)

**Tool ID**: `mabl`

Calculates maximum blood loss before transfusion needed.

**Parameters**:
- Estimated blood volume
- Starting hematocrit
- Minimum acceptable hematocrit

---

## Other Anesthesiology Tools

| Tool | ID | Purpose |
|------|----|---------|
| Caprini VTE | `caprini_vte` | VTE prophylaxis |
| ARISCAT | `ariscat` | Pulmonary complications |
| NSQIP | `nsqip` | Surgical risk |
| Parkland | `parkland_formula` | Burn resuscitation |
