"""
MCP Prompt Handler

Provides reusable prompt templates for common clinical workflows.
These prompts guide AI agents through multi-step clinical assessments.

MCP Prompts are different from Tools:
- Tools: Execute calculations and return results
- Prompts: Provide structured guidance for using tools together

Reference: https://modelcontextprotocol.io/docs/concepts/prompts
"""

from mcp.server.fastmcp import FastMCP

from ....domain.registry.tool_registry import ToolRegistry


class PromptHandler:
    """
    Handler for MCP prompt templates.
    
    Prompts provide clinical workflow guidance that helps AI agents
    understand how to use multiple tools together for comprehensive
    patient assessments.
    """
    
    def __init__(self, mcp: FastMCP, registry: ToolRegistry):
        self._mcp = mcp
        self._registry = registry
        self._register_prompts()
    
    def _register_prompts(self) -> None:
        """Register all clinical workflow prompts"""
        
        @self._mcp.prompt()
        def sepsis_evaluation() -> str:
            """
            Sepsis Evaluation Workflow - 敗血症評估工作流程
            
            A structured approach to evaluate patients with suspected sepsis
            using Sepsis-3 criteria.
            """
            return """# Sepsis Evaluation Workflow (Sepsis-3)
敗血症評估工作流程

## Overview
This workflow guides you through the Sepsis-3 evaluation process using
sequential assessment tools.

## Step 1: Initial Screening with qSOFA (Bedside)
First, perform a quick bedside assessment:

```
Tool: calculate_qsofa
Parameters:
  - respiratory_rate: Breaths per minute (≥22 scores 1 point)
  - systolic_bp: mmHg (≤100 scores 1 point)
  - altered_mentation: GCS <15 or acute change (scores 1 point)
```

**Interpretation:**
- qSOFA ≥2: Higher risk, proceed to full SOFA assessment
- qSOFA <2: Lower risk, but does not rule out sepsis

⚠️ **Important**: Per SSC 2021 Guidelines, qSOFA should NOT be used as
a standalone screening tool for sepsis.

## Step 2: Full SOFA Score (If qSOFA ≥2 or High Suspicion)
Assess all 6 organ systems:

```
Tool: calculate_sofa
Required Parameters:
  - pao2_fio2_ratio: PaO2/FiO2 ratio (respiratory)
  - platelets: ×10³/µL (coagulation)
  - bilirubin: mg/dL (liver)
  - gcs_score: 3-15 (neurologic)
  - creatinine: mg/dL (renal)
  
Optional (for cardiovascular scoring):
  - map_value: mmHg (if no vasopressors)
  - dopamine_dose, epinephrine_dose, norepinephrine_dose: µg/kg/min
```

**Sepsis-3 Definition:**
- Suspected infection + SOFA increase ≥2 = Sepsis
- SOFA ≥2 alone indicates >10% mortality risk

## Step 3: Septic Shock Assessment
If sepsis confirmed, evaluate for septic shock criteria:

**Septic Shock = Sepsis + ALL of:**
1. Vasopressors required to maintain MAP ≥65 mmHg
2. Serum lactate >2 mmol/L
3. Despite adequate fluid resuscitation

## Step 4: Hour-1 Bundle (If Sepsis/Septic Shock)
Implement Surviving Sepsis Campaign Hour-1 Bundle:
1. ✓ Measure lactate level
2. ✓ Obtain blood cultures before antibiotics
3. ✓ Administer broad-spectrum antibiotics
4. ✓ Begin 30 mL/kg crystalloid for hypotension or lactate ≥4
5. ✓ Apply vasopressors if hypotensive during/after fluid resuscitation

## ICU Monitoring
For admitted patients:
1. Use `calculate_rass` to assess sedation level
2. Use `calculate_cam_icu` to screen for delirium (requires RASS first)
3. Reassess SOFA every 24 hours

## Related Calculators
| Tool | Purpose |
|------|---------|
| calculate_qsofa | Quick bedside screening |
| calculate_sofa | Full organ dysfunction assessment |
| calculate_apache_ii | ICU mortality prediction |
| calculate_rass | Sedation assessment |
| calculate_cam_icu | Delirium screening |
| calculate_gcs | Consciousness assessment |
| calculate_news2 | Early warning score |

## References
- Singer M, et al. JAMA 2016 (Sepsis-3)
- Evans L, et al. Crit Care Med 2021 (SSC Guidelines)
"""

        @self._mcp.prompt()
        def preoperative_risk_assessment() -> str:
            """
            Preoperative Risk Assessment Workflow - 術前風險評估工作流程
            
            A structured approach to evaluate surgical risk before non-cardiac surgery.
            """
            return """# Preoperative Risk Assessment Workflow
術前風險評估工作流程

## Overview
This workflow helps evaluate perioperative risk for patients undergoing
non-cardiac surgery, following ACC/AHA guidelines.

## Step 1: ASA Physical Status Classification
First, determine the patient's overall health status:

```
Tool: calculate_asa_physical_status
Parameters:
  - patient_condition: Healthy/mild systemic/severe systemic/etc.
  - examples: Specific conditions like DM, HTN, ESRD, etc.
  - is_emergency: Boolean (adds "E" modifier)
```

**ASA Classes:**
- ASA I: Normal healthy patient
- ASA II: Mild systemic disease
- ASA III: Severe systemic disease (not incapacitating)
- ASA IV: Severe systemic disease (constant threat to life)
- ASA V: Moribund, not expected to survive without surgery
- ASA VI: Brain-dead organ donor

## Step 2: Cardiac Risk (RCRI)
Evaluate cardiac risk for major non-cardiac surgery:

```
Tool: calculate_rcri
Parameters (all boolean):
  - high_risk_surgery: Intraperitoneal, intrathoracic, or suprainguinal vascular
  - ischemic_heart_disease: History of MI, positive stress test, angina, nitrate use
  - congestive_heart_failure: History of CHF, pulmonary edema, S3, bilateral rales
  - cerebrovascular_disease: History of TIA or stroke
  - diabetes_on_insulin: Preoperative insulin use
  - creatinine_gt_2: Preoperative Cr >2.0 mg/dL
```

**Risk Interpretation:**
| RCRI Points | Major Cardiac Events |
|-------------|---------------------|
| 0 | 0.4% |
| 1 | 0.9% |
| 2 | 6.6% |
| ≥3 | 11% |

## Step 3: Airway Assessment
Predict difficult intubation:

```
Tool: calculate_mallampati
Parameters:
  - mallampati_class: 1-4 based on oropharyngeal visualization
  - neck_mobility: Normal, limited, or severely limited
  - thyromental_distance: cm (normal >6.5 cm)
  - mouth_opening: cm (normal >4 cm)
```

**Mallampati Classes:**
- Class I: Soft palate, uvula, fauces, pillars visible
- Class II: Soft palate, uvula, fauces visible
- Class III: Soft palate, base of uvula visible
- Class IV: Hard palate only visible

## Step 4: Additional Assessments (As Indicated)

### For Patients ≥65 or with Functional Limitations:
Consider frailty and functional capacity assessment

### For Major Surgery with Expected Blood Loss:
```
Tool: calculate_mabl
Parameters:
  - weight: kg
  - patient_type: adult_male, adult_female, infant, etc.
  - starting_hct: Current hematocrit (%)
  - minimum_hct: Acceptable minimum hematocrit (%)
```

### Renal Function:
```
Tool: calculate_ckd_epi_2021
Parameters:
  - creatinine: mg/dL
  - age: years
  - sex: male/female
```

## Decision Points

### Low Risk (ASA I-II, RCRI 0-1, Mallampati I-II):
- Proceed with standard anesthetic plan
- Routine perioperative monitoring

### Intermediate Risk (ASA III, RCRI 2):
- Consider cardiology consultation
- Optimize medical conditions
- May need additional cardiac testing

### High Risk (ASA IV+, RCRI ≥3):
- Mandatory specialist consultation
- Consider postponement for optimization
- Discuss risks/benefits with patient and family
- Plan for post-op ICU care

## Related Calculators
| Tool | Purpose |
|------|---------|
| calculate_asa_physical_status | Overall health classification |
| calculate_rcri | Cardiac risk prediction |
| calculate_mallampati | Airway difficulty prediction |
| calculate_ckd_epi_2021 | Renal function assessment |
| calculate_mabl | Blood loss tolerance |

## References
- Fleisher LA, et al. Circulation 2014 (ACC/AHA Guidelines)
- Lee TH, et al. Circulation 1999 (Original RCRI)
- ASA Physical Status Classification System
"""

        @self._mcp.prompt()
        def icu_daily_assessment() -> str:
            """
            ICU Daily Assessment Workflow - 加護病房每日評估工作流程
            
            A structured approach for daily ICU patient rounds.
            """
            return """# ICU Daily Assessment Workflow
加護病房每日評估工作流程

## Overview
This workflow provides a structured approach for daily ICU rounds,
covering key organ systems and standardized scoring.

## Morning Assessment Sequence

### 1. Sedation Assessment (RASS)
Always assess sedation FIRST before other neurologic evaluations:

```
Tool: calculate_rass
Parameters:
  - rass_score: -5 to +4
```

**RASS Scale:**
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

**Target RASS:** Usually 0 to -2 (per PADIS guidelines)

### 2. Delirium Screening (CAM-ICU)
Only valid if RASS ≥-3 (patient arousable):

```
Tool: calculate_cam_icu
Parameters:
  - rass_score: Current RASS (-5 to +4)
  - acute_onset_fluctuation: Acute change or fluctuating course?
  - inattention_score: ASE errors (0-10, ≥3 = positive)
  - altered_loc: RASS other than 0?
  - disorganized_thinking_errors: Command/question errors (0-5)
```

**CAM-ICU Positive = Delirium** if:
- Feature 1 (acute onset) + Feature 2 (inattention)
- AND either Feature 3 (altered LOC) OR Feature 4 (disorganized thinking)

### 3. Consciousness Assessment (GCS)
For non-sedated or neurologic patients:

```
Tool: calculate_gcs
Parameters:
  - eye_response: 1-4
  - verbal_response: 1-5 (or note if intubated)
  - motor_response: 1-6
  - is_intubated: Boolean
```

### 4. Organ Function Assessment (SOFA)
Daily SOFA to track trajectory:

```
Tool: calculate_sofa
(See sepsis workflow for full parameters)
```

**SOFA Trend Interpretation:**
- Decreasing: Improving, consider de-escalation
- Stable: Continue current management
- Increasing: Worsening, investigate and intensify

### 5. Early Warning Score (NEWS2)
For step-down or floor patients:

```
Tool: calculate_news2
Parameters:
  - respiratory_rate, spo2, on_supplemental_o2
  - temperature, systolic_bp, heart_rate
  - consciousness: A/V/P/U
```

## Daily Checklist Integration

### FAST HUG BID Mnemonic:
| Letter | Item | Related Calculator |
|--------|------|-------------------|
| F | Feeding | - |
| A | Analgesia | VAS/NRS |
| S | Sedation | calculate_rass |
| T | Thromboprophylaxis | - |
| H | Head of bed | - |
| U | Ulcer prophylaxis | - |
| G | Glucose control | - |
| B | Bowel care | - |
| I | Indwelling catheters | - |
| D | De-escalation | calculate_sofa (trending) |

### Ventilator Liberation Assessment:
If mechanically ventilated:
1. RASS at target?
2. CAM-ICU negative?
3. Adequate oxygenation (P/F ratio)?
4. Hemodynamically stable?
5. Ready for SAT/SBT?

## Related Calculators
| Tool | Purpose | Frequency |
|------|---------|-----------|
| calculate_rass | Sedation level | q4h or PRN |
| calculate_cam_icu | Delirium screening | q12h |
| calculate_gcs | Consciousness | Daily or PRN |
| calculate_sofa | Organ dysfunction | Daily |
| calculate_news2 | Early warning | q4-6h |
| calculate_apache_ii | Severity (admission) | Once |

## References
- Devlin JW, et al. Crit Care Med 2018 (PADIS Guidelines)
- Ely EW, et al. JAMA 2001 (CAM-ICU)
- Vincent JL, et al. Intensive Care Med 1996 (SOFA)
"""

        @self._mcp.prompt()
        def pediatric_drug_dosing() -> str:
            """
            Pediatric Drug Dosing Workflow - 兒科藥物劑量工作流程
            
            A structured approach for safe pediatric medication dosing.
            """
            return """# Pediatric Drug Dosing Workflow
兒科藥物劑量計算工作流程

## Overview
Pediatric dosing requires special attention to weight-based calculations
and maximum dose limits. This workflow ensures safe prescribing.

## Step 1: Obtain Accurate Weight
- Use actual measured weight (not estimated)
- Weigh in kg (convert from lbs: lbs × 0.453592 = kg)
- For neonates: use grams if <1 kg

## Step 2: Calculate Drug Dose

```
Tool: calculate_pediatric_dosing
Parameters:
  - drug_name: Name of medication (see available drugs below)
  - weight_kg: Patient weight in kilograms
  - indication: Optional - may affect dose selection
```

## Available Drugs

### Antibiotics
| Drug | Dose Range | Max Dose |
|------|-----------|----------|
| Amoxicillin | 25-50 mg/kg/day | 500mg/dose |
| Amoxicillin (high-dose) | 80-90 mg/kg/day | 2g/day |
| Amoxicillin-Clavulanate | 25-45 mg/kg/day | 875mg/dose |
| Azithromycin | 10 mg/kg day 1, then 5 mg/kg | 500mg day 1 |
| Cephalexin | 25-50 mg/kg/day | 500mg/dose |
| Ceftriaxone | 50-100 mg/kg/day | 2g/day |

### Analgesics/Antipyretics
| Drug | Dose Range | Max Dose |
|------|-----------|----------|
| Acetaminophen | 10-15 mg/kg/dose | 1g/dose |
| Ibuprofen | 5-10 mg/kg/dose | 400mg/dose |

### Antihistamines
| Drug | Dose Range | Max Dose |
|------|-----------|----------|
| Diphenhydramine | 1-1.25 mg/kg/dose | 50mg/dose |
| Cetirizine | 0.25 mg/kg/dose | 10mg/dose |

### Respiratory
| Drug | Dose Range | Max Dose |
|------|-----------|----------|
| Prednisolone | 1-2 mg/kg/day | 60mg/day |
| Albuterol (nebulized) | 0.15 mg/kg/dose | 5mg/dose |

## Step 3: Safety Checks

### Always Verify:
1. ✓ Calculated dose ≤ Maximum dose
2. ✓ Appropriate for age
3. ✓ Correct route of administration
4. ✓ Drug interactions checked
5. ✓ Allergies reviewed

### Red Flags:
⚠️ Calculated dose exceeds adult dose
⚠️ Weight seems inconsistent with age
⚠️ Off-label use requires additional verification

## Step 4: Blood Loss Considerations
For surgical patients, assess acceptable blood loss:

```
Tool: calculate_mabl
Parameters:
  - weight: kg
  - patient_type: infant, child, adolescent
  - starting_hct: Current hematocrit (%)
  - minimum_hct: Acceptable minimum (usually 25-30%)
```

**Estimated Blood Volumes:**
| Patient Type | EBV (mL/kg) |
|--------------|-------------|
| Preterm neonate | 90-100 |
| Term neonate | 85-90 |
| Infant (1-12 mo) | 80 |
| Child (1-12 yr) | 75 |
| Adolescent | 70 |

## Step 5: Transfusion Needs
If blood loss expected or anemia present:

```
Tool: calculate_transfusion
Parameters:
  - weight: kg
  - current_hgb: g/dL
  - target_hgb: g/dL
  - product_type: prbc, platelets, ffp
```

**Pediatric Transfusion Rules:**
- pRBC: 10-15 mL/kg raises Hgb ~2-3 g/dL
- Platelets: 10 mL/kg raises count ~50-100K
- FFP: 10-15 mL/kg for factor replacement

## Related Calculators
| Tool | Purpose |
|------|---------|
| calculate_pediatric_dosing | Drug dose calculation |
| calculate_mabl | Maximum blood loss |
| calculate_transfusion | Transfusion volume |

## References
- Harriet Lane Handbook (Pediatric Drug Dosing)
- AAP Clinical Practice Guidelines
- PALS Guidelines
"""

        @self._mcp.prompt()
        def acute_kidney_injury_assessment() -> str:
            """
            Acute Kidney Injury Assessment Workflow - 急性腎損傷評估工作流程
            
            A structured approach to evaluate and stage acute kidney injury.
            """
            return """# Acute Kidney Injury Assessment Workflow
急性腎損傷評估工作流程

## Overview
This workflow guides evaluation of acute kidney injury (AKI) using
KDIGO criteria and appropriate renal function calculators.

## Step 1: Baseline Renal Function
Establish baseline eGFR if not in AKI:

```
Tool: calculate_ckd_epi_2021
Parameters:
  - creatinine: mg/dL (baseline or most recent stable value)
  - age: years
  - sex: male or female
```

**CKD-EPI 2021 Features:**
- Race-neutral equation (2021 update)
- Most accurate for adults
- Returns GFR in mL/min/1.73m²

## Step 2: AKI Staging (KDIGO Criteria)

### Creatinine Criteria:
| Stage | Creatinine Change |
|-------|------------------|
| 1 | ↑ 0.3 mg/dL within 48h OR ↑ 1.5-1.9× baseline |
| 2 | ↑ 2.0-2.9× baseline |
| 3 | ↑ ≥3× baseline OR ≥4.0 mg/dL OR RRT initiation |

### Urine Output Criteria:
| Stage | Urine Output |
|-------|-------------|
| 1 | <0.5 mL/kg/h for 6-12 hours |
| 2 | <0.5 mL/kg/h for ≥12 hours |
| 3 | <0.3 mL/kg/h for ≥24h OR anuria ≥12h |

**Use the higher stage from either criterion**

## Step 3: Etiology Assessment

### Pre-renal (Most Common):
- Hypovolemia, heart failure, hepatorenal
- FENa <1%, BUN/Cr >20:1
- Usually reversible with fluid resuscitation

### Intrinsic Renal:
- ATN, AIN, glomerulonephritis
- FENa >2%, muddy brown casts
- May require specific therapy

### Post-renal:
- Obstruction (BPH, stones, tumor)
- Ultrasound shows hydronephrosis
- Requires decompression

## Step 4: Drug Dosing Adjustment
Adjust renally-cleared medications based on eGFR:

```
Tool: calculate_ckd_epi_2021
(Recalculate with current creatinine)
```

### Common Adjustments:
| eGFR | Common Drug Adjustments |
|------|------------------------|
| 30-59 | Reduce frequency of aminoglycosides |
| 15-29 | Avoid metformin, reduce opioid doses |
| <15 | Dialysis dosing, avoid nephrotoxins |

## Step 5: Monitor Organ Function
AKI often accompanies multi-organ dysfunction:

```
Tool: calculate_sofa
(Include renal component for comprehensive assessment)
```

## Prevention and Management

### Avoid Nephrotoxins:
- NSAIDs
- Aminoglycosides (if possible)
- IV contrast (or use iso-osmolar with hydration)
- ACE-I/ARBs in acute setting

### Supportive Care:
- Maintain euvolemia
- Avoid hyperglycemia
- Correct metabolic acidosis
- Treat hyperkalemia promptly

### RRT Indications (Urgent):
- Refractory hyperkalemia (K >6.5)
- Severe metabolic acidosis (pH <7.1)
- Uremic symptoms (pericarditis, encephalopathy)
- Refractory fluid overload
- Certain toxin ingestions

## Related Calculators
| Tool | Purpose |
|------|---------|
| calculate_ckd_epi_2021 | eGFR calculation |
| calculate_sofa | Multi-organ assessment |
| calculate_apache_ii | Severity scoring |

## References
- KDIGO Clinical Practice Guideline for AKI 2012
- CKD-EPI 2021 Equation (race-neutral)
"""
