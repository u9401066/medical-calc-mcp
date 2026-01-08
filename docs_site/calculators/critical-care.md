# Critical Care Calculators

Calculators for ICU assessment, organ dysfunction, and severity scoring.

## Severity & Prognosis

### SOFA Score (Sequential Organ Failure Assessment)

!!! info "Sepsis-3 Criterion"
    SOFA ≥2 with suspected infection = Sepsis

**Tool ID**: `sofa_score`

| Parameter | Range |
|-----------|-------|
| PaO2/FiO2 ratio | Required |
| Platelets (×10⁹/L) | Required |
| Bilirubin (mg/dL) | Required |
| MAP or vasopressors | Required |
| GCS | Required |
| Creatinine (mg/dL) | Required |

**Reference**: Singer M, et al. JAMA. 2016;315(8):801-810. PMID: 26903338

---

### qSOFA (Quick SOFA)

Bedside screening for sepsis outside the ICU.

**Tool ID**: `qsofa_score`

| Parameter | Criteria |
|-----------|----------|
| Respiratory rate | ≥22/min |
| Systolic BP | ≤100 mmHg |
| Altered mentation | GCS <15 |

**Interpretation**:
- Score ≥2: High risk, consider ICU admission
- Score <2: Low risk, but doesn't exclude sepsis

---

### APACHE II

Mortality prediction for ICU patients.

**Tool ID**: `apache_ii`

**Parameters**: Age, temperature, MAP, heart rate, respiratory rate, oxygenation, pH, sodium, potassium, creatinine, hematocrit, WBC, GCS, chronic health status

**Reference**: Knaus WA, et al. Crit Care Med. 1985;13(10):818-829. PMID: 3928249

---

### NEWS2 (National Early Warning Score 2)

**Tool ID**: `news2_score`

| Score | Risk | Action |
|-------|------|--------|
| 0-4 | Low | Routine monitoring |
| 5-6 | Medium | Urgent review |
| ≥7 | High | Emergency response |

---

## Sedation & Delirium

### RASS (Richmond Agitation-Sedation Scale)

**Tool ID**: `rass`

| Score | Description |
|-------|-------------|
| +4 | Combative |
| +3 | Very agitated |
| +2 | Agitated |
| +1 | Restless |
| 0 | Alert and calm |
| -1 | Drowsy |
| -2 | Light sedation |
| -3 | Moderate sedation |
| -4 | Deep sedation |
| -5 | Unarousable |

---

### CAM-ICU (Confusion Assessment Method for ICU)

**Tool ID**: `cam_icu`

!!! warning "Prerequisite"
    Requires RASS ≥-3 to assess

**Features assessed**:
1. Acute onset or fluctuating course
2. Inattention
3. Altered level of consciousness
4. Disorganized thinking

---

## Other Critical Care Tools

| Tool | ID | Purpose |
|------|----|---------|
| GCS | `glasgow_coma_scale` | Consciousness assessment |
| SAPS II | `saps_ii` | Mortality prediction |
| APACHE IV | `apache_iv` | Updated mortality model |
| MODS | `mods_score` | Multiple organ dysfunction |
| PIM3 | `pim3` | Pediatric ICU mortality |
| PEWS | `pews` | Pediatric early warning |
