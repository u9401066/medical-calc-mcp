# Hepatology Calculators

Tools for liver disease assessment and prognosis.

## Chronic Liver Disease

### Child-Pugh Score

**Tool ID**: `child_pugh`

Classification of cirrhosis severity.

| Parameter | 1 point | 2 points | 3 points |
|-----------|---------|----------|----------|
| Bilirubin (mg/dL) | <2 | 2-3 | >3 |
| Albumin (g/dL) | >3.5 | 2.8-3.5 | <2.8 |
| INR | <1.7 | 1.7-2.3 | >2.3 |
| Ascites | None | Mild | Moderate-severe |
| Encephalopathy | None | Grade 1-2 | Grade 3-4 |

**Classification**:

| Class | Points | 1-year Survival |
|-------|--------|----------------|
| A | 5-6 | 100% |
| B | 7-9 | 80% |
| C | 10-15 | 45% |

---

### MELD Score

**Tool ID**: `meld_score`

Model for End-Stage Liver Disease (transplant prioritization).

**Formula**:
```
MELD = 10 × (0.957 × ln(Cr) + 0.378 × ln(Bili) + 1.12 × ln(INR) + 0.643)
```

**Parameters**:
- Creatinine (mg/dL)
- Bilirubin (mg/dL)
- INR

!!! info "Transplant Listing"
    Higher MELD = higher transplant priority

---

### MELD-Na

**Tool ID**: `meld_na`

MELD with sodium correction (better mortality prediction).

**Formula includes sodium** (125-137 mEq/L range capped).

---

### MELD 3.0

**Tool ID**: `meld_3`

Latest version incorporating sex and albumin.

---

## Alcoholic Liver Disease

### Maddrey's Discriminant Function

**Tool ID**: `maddrey_df`

Severity of alcoholic hepatitis.

**Formula**:
```
DF = 4.6 × (PT - control PT) + Bilirubin
```

| DF | Severity | Treatment |
|----|----------|-----------|
| <32 | Mild-moderate | Supportive |
| ≥32 | Severe | Consider steroids |

---

### Lille Model

**Tool ID**: `lille_model`

Response to steroids in alcoholic hepatitis (assessed at day 7).

| Score | Interpretation |
|-------|----------------|
| <0.45 | Responder - continue steroids |
| ≥0.45 | Non-responder - stop steroids |

---

## Other Hepatology Tools

| Tool | ID | Purpose |
|------|----|---------|
| ABIC Score | `abic_score` | Alcoholic hepatitis prognosis |
| Glasgow Score | `glasgow_alcoholic_hepatitis` | Alcoholic hepatitis severity |
| FIB-4 | `fib4` | Fibrosis estimation |
| APRI | `apri` | Fibrosis estimation |
