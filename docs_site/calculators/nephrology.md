# Nephrology Calculators

Tools for kidney function assessment and AKI staging.

## eGFR Calculation

### CKD-EPI 2021 (Recommended)

The 2021 race-free equation.

**Tool ID**: `ckd_epi_2021`

!!! success "Current Standard"
    CKD-EPI 2021 is now recommended over older equations

**Parameters**:
- Serum creatinine (mg/dL)
- Age (years)
- Sex

**CKD Staging**:

| Stage | eGFR (mL/min/1.73m²) | Description |
|-------|---------------------|-------------|
| G1 | ≥90 | Normal or high |
| G2 | 60-89 | Mildly decreased |
| G3a | 45-59 | Mildly to moderately decreased |
| G3b | 30-44 | Moderately to severely decreased |
| G4 | 15-29 | Severely decreased |
| G5 | <15 | Kidney failure |

---

### Cockcroft-Gault

Creatinine clearance estimation (for drug dosing).

**Tool ID**: `cockcroft_gault`

**Parameters**:
- Serum creatinine
- Age
- Weight
- Sex

!!! note "Drug Dosing"
    Many drug manufacturers still reference Cockcroft-Gault for dosing adjustments

---

## Acute Kidney Injury

### KDIGO AKI Staging

**Tool ID**: `kdigo_aki`

**Staging Criteria**:

| Stage | Serum Creatinine | Urine Output |
|-------|-----------------|--------------|
| 1 | 1.5-1.9× baseline OR ≥0.3 mg/dL increase | <0.5 mL/kg/h for 6-12h |
| 2 | 2.0-2.9× baseline | <0.5 mL/kg/h for ≥12h |
| 3 | ≥3× baseline OR ≥4.0 mg/dL OR RRT | <0.3 mL/kg/h for ≥24h OR anuria ≥12h |

---

## Electrolyte Calculations

### Corrected Sodium

**Tool ID**: `corrected_sodium`

Corrects sodium for hyperglycemia.

**Formula**: Na + 1.6 × (Glucose - 100) / 100

---

### FENa (Fractional Excretion of Sodium)

**Tool ID**: `fena`

Differentiates prerenal from intrinsic renal AKI.

| FENa | Interpretation |
|------|----------------|
| <1% | Prerenal azotemia |
| >2% | Intrinsic renal disease |
| 1-2% | Indeterminate |

---

## Other Nephrology Tools

| Tool | ID | Purpose |
|------|----|---------|
| BUN/Creatinine Ratio | `bun_cr_ratio` | Prerenal vs intrinsic |
| Urine Anion Gap | `urine_anion_gap` | RTA differentiation |
| Osmolar Gap | `osmolar_gap` | Toxic alcohol screen |
| Free Water Deficit | `free_water_deficit` | Hypernatremia correction |
