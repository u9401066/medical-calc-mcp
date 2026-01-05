"""
KDIGO AKI Staging Calculator

Classifies acute kidney injury (AKI) severity based on serum creatinine
and/or urine output criteria.

Primary Reference:
    Kidney Disease: Improving Global Outcomes (KDIGO) Acute Kidney Injury
    Work Group. KDIGO Clinical Practice Guideline for Acute Kidney Injury.
    Kidney Int Suppl. 2012;2(1):1-138.
    doi:10.1038/kisup.2012.1.

Supporting References:
    Kellum JA, Lameire N; KDIGO AKI Guideline Work Group. Diagnosis,
    evaluation, and management of acute kidney injury: a KDIGO summary
    (Part 1). Crit Care. 2013;17(1):204.
    doi:10.1186/cc11454. PMID: 23394211.

    Khwaja A. KDIGO Clinical Practice Guidelines for Acute Kidney Injury.
    Nephron Clin Pract. 2012;120(4):c179-c184.
    doi:10.1159/000339789. PMID: 22890468.
"""

from typing import Optional

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import (
    ClinicalContext,
    HighLevelKey,
    LowLevelKey,
    Specialty,
)
from ...value_objects.units import Unit
from ..base import BaseCalculator


class KdigoAkiCalculator(BaseCalculator):
    """
    KDIGO AKI Staging Calculator

    AKI Definition (any of the following):
    - Increase in serum creatinine ≥0.3 mg/dL within 48 hours
    - Increase in serum creatinine ≥1.5x baseline within 7 days
    - Urine output <0.5 mL/kg/h for 6 hours

    KDIGO AKI Staging:

    | Stage | Serum Creatinine Criteria | Urine Output Criteria |
    |-------|---------------------------|----------------------|
    | 1     | 1.5-1.9x baseline OR      | <0.5 mL/kg/h for     |
    |       | ≥0.3 mg/dL increase       | 6-12 hours           |
    | 2     | 2.0-2.9x baseline         | <0.5 mL/kg/h for     |
    |       |                           | ≥12 hours            |
    | 3     | ≥3.0x baseline OR         | <0.3 mL/kg/h for     |
    |       | ≥4.0 mg/dL OR             | ≥24 hours OR         |
    |       | Initiation of RRT         | Anuria for ≥12 hours |

    Clinical implications:
    - Stage 1: Mild AKI - close monitoring, identify/treat cause
    - Stage 2: Moderate AKI - aggressive management, nephrology consult
    - Stage 3: Severe AKI - high mortality, likely RRT candidate
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="kdigo_aki",
                name="KDIGO AKI Staging",
                purpose="Classify acute kidney injury severity by KDIGO criteria",
                input_params=[
                    "current_creatinine",
                    "baseline_creatinine",
                    "creatinine_increase_48h",
                    "urine_output_ml_kg_h",
                    "urine_output_duration_hours",
                    "on_rrt",
                ],
                output_type="AKI Stage 1-3 with management recommendations"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.NEPHROLOGY,
                    Specialty.CRITICAL_CARE,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.EMERGENCY_MEDICINE,
                ),
                conditions=(
                    "acute kidney injury",
                    "AKI",
                    "acute renal failure",
                    "ARF",
                    "renal impairment",
                    "kidney injury",
                    "oliguria",
                    "anuria",
                    "creatinine elevation",
                ),
                clinical_contexts=(
                    ClinicalContext.STAGING,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "What stage of AKI does this patient have?",
                    "How severe is this patient's kidney injury?",
                    "Does this patient meet criteria for AKI?",
                    "Does this patient need dialysis?",
                    "Should I consult nephrology for this creatinine?",
                    "How should I manage this AKI?",
                ),
                icd10_codes=(
                    "N17.0",  # Acute kidney failure with tubular necrosis
                    "N17.1",  # Acute kidney failure with acute cortical necrosis
                    "N17.2",  # Acute kidney failure with medullary necrosis
                    "N17.8",  # Other acute kidney failure
                    "N17.9",  # Acute kidney failure, unspecified
                ),
                keywords=(
                    "KDIGO",
                    "AKI staging",
                    "acute kidney injury",
                    "renal failure staging",
                    "creatinine increase",
                    "oliguria staging",
                    "RIFLE",
                    "AKIN",
                    "kidney injury criteria",
                )
            ),
            references=(
                Reference(
                    citation="Kidney Disease: Improving Global Outcomes (KDIGO) "
                             "Acute Kidney Injury Work Group. KDIGO Clinical Practice "
                             "Guideline for Acute Kidney Injury. "
                             "Kidney Int Suppl. 2012;2(1):1-138.",
                    doi="10.1038/kisup.2012.1",
                    year=2012,
                ),
                Reference(
                    citation="Kellum JA, Lameire N; KDIGO AKI Guideline Work Group. "
                             "Diagnosis, evaluation, and management of acute kidney injury: "
                             "a KDIGO summary (Part 1). Crit Care. 2013;17(1):204.",
                    doi="10.1186/cc11454",
                    pmid="23394211",
                    year=2013,
                ),
                Reference(
                    citation="Khwaja A. KDIGO Clinical Practice Guidelines for Acute "
                             "Kidney Injury. Nephron Clin Pract. 2012;120(4):c179-c184.",
                    doi="10.1159/000339789",
                    pmid="22890468",
                    year=2012,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        current_creatinine: float,
        baseline_creatinine: Optional[float] = None,
        creatinine_increase_48h: Optional[float] = None,
        urine_output_ml_kg_h: Optional[float] = None,
        urine_output_duration_hours: Optional[float] = None,
        on_rrt: bool = False,
    ) -> ScoreResult:
        """
        Calculate KDIGO AKI stage.

        Args:
            current_creatinine: Current serum creatinine in mg/dL
            baseline_creatinine: Baseline creatinine in mg/dL (if known).
                If unknown, can estimate from age/sex or use admission value.
            creatinine_increase_48h: Absolute creatinine increase in 48h (mg/dL).
                Only needed if ≥0.3 mg/dL increase suspected.
            urine_output_ml_kg_h: Average urine output in mL/kg/hour.
                If oliguria/anuria present.
            urine_output_duration_hours: Duration of reduced urine output in hours.
            on_rrt: Currently on renal replacement therapy (dialysis/CRRT)?
                Automatically Stage 3 if true.

        Returns:
            ScoreResult with AKI stage and management recommendations
        """
        # Determine AKI stage based on creatinine criteria
        cr_stage = self._stage_by_creatinine(
            current_creatinine, baseline_creatinine, creatinine_increase_48h
        )

        # Determine AKI stage based on urine output criteria
        uo_stage = self._stage_by_urine_output(
            urine_output_ml_kg_h, urine_output_duration_hours
        )

        # RRT automatically means Stage 3
        if on_rrt:
            final_stage = 3
        else:
            # Take the higher (worse) stage
            final_stage = max(cr_stage, uo_stage)

        # Check if AKI criteria met
        has_aki = final_stage > 0

        # Generate interpretation
        interpretation = self._interpret_stage(
            final_stage, cr_stage, uo_stage,
            current_creatinine, baseline_creatinine, on_rrt
        )

        # Calculation details
        components = {
            "Current Creatinine": f"{current_creatinine} mg/dL",
            "Baseline Creatinine": f"{baseline_creatinine} mg/dL" if baseline_creatinine else "Unknown",
            "Creatinine Ratio": f"{current_creatinine/baseline_creatinine:.2f}x" if baseline_creatinine else "N/A",
            "48h Creatinine Increase": f"+{creatinine_increase_48h} mg/dL" if creatinine_increase_48h else "N/A",
            "Creatinine-based Stage": cr_stage if cr_stage > 0 else "No AKI by Cr",
            "Urine Output": f"{urine_output_ml_kg_h} mL/kg/h × {urine_output_duration_hours}h" if urine_output_ml_kg_h else "N/A",
            "UO-based Stage": uo_stage if uo_stage > 0 else "No AKI by UO",
            "On RRT": "Yes (auto Stage 3)" if on_rrt else "No",
            "AKI Present": "Yes" if has_aki else "No",
            "Final KDIGO Stage": final_stage if has_aki else "No AKI",
        }

        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=final_stage,
            unit=Unit.SCORE,  # Using SCORE for staging (0-3)
            interpretation=interpretation,
            calculation_details=components,
            references=list(self.references),
        )

    def _stage_by_creatinine(
        self,
        current: float,
        baseline: Optional[float],
        increase_48h: Optional[float],
    ) -> int:
        """Determine AKI stage by creatinine criteria"""
        stage = 0

        # Check 48h absolute increase (≥0.3 mg/dL = Stage 1)
        if increase_48h is not None and increase_48h >= 0.3:
            stage = max(stage, 1)

        # Check ratio to baseline
        if baseline is not None and baseline > 0:
            ratio = current / baseline

            if ratio >= 3.0:
                stage = 3
            elif ratio >= 2.0:
                stage = max(stage, 2)
            elif ratio >= 1.5:
                stage = max(stage, 1)

        # Absolute creatinine ≥4.0 mg/dL = Stage 3
        if current >= 4.0:
            stage = 3

        return stage

    def _stage_by_urine_output(
        self,
        uo_ml_kg_h: Optional[float],
        duration_hours: Optional[float],
    ) -> int:
        """Determine AKI stage by urine output criteria"""
        if uo_ml_kg_h is None or duration_hours is None:
            return 0

        # Anuria (essentially 0) for ≥12 hours = Stage 3
        if uo_ml_kg_h < 0.1 and duration_hours >= 12:
            return 3

        # <0.3 mL/kg/h for ≥24 hours = Stage 3
        if uo_ml_kg_h < 0.3 and duration_hours >= 24:
            return 3

        # <0.5 mL/kg/h for ≥12 hours = Stage 2
        if uo_ml_kg_h < 0.5 and duration_hours >= 12:
            return 2

        # <0.5 mL/kg/h for 6-12 hours = Stage 1
        if uo_ml_kg_h < 0.5 and duration_hours >= 6:
            return 1

        return 0

    def _interpret_stage(
        self,
        stage: int,
        cr_stage: int,
        uo_stage: int,
        current_cr: float,
        baseline_cr: Optional[float],
        on_rrt: bool,
    ) -> Interpretation:
        """Generate interpretation based on KDIGO AKI stage"""

        if stage == 0:
            # No AKI
            severity = Severity.NORMAL
            risk_level = RiskLevel.LOW
            summary = "No AKI: Does not meet KDIGO AKI criteria"
            detail = (
                "Current creatinine and urine output do not meet KDIGO criteria "
                "for acute kidney injury. Continue monitoring if risk factors present."
            )
            recommendations = [
                "No AKI by current criteria",
                "Continue monitoring creatinine if at risk",
                "Maintain adequate hydration and perfusion",
                "Avoid nephrotoxic medications when possible",
            ]
            next_steps = [
                "Repeat creatinine in 24-48h if concern persists",
                "Monitor urine output",
                "Address any identified risk factors",
            ]
            warnings = []

        elif stage == 1:
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            summary = "KDIGO AKI Stage 1: Mild acute kidney injury"
            detail = (
                "Stage 1 AKI: Creatinine 1.5-1.9x baseline OR ≥0.3 mg/dL increase "
                "OR urine output <0.5 mL/kg/h for 6-12 hours. "
                "Most Stage 1 AKI resolves with supportive care."
            )
            recommendations = [
                "Identify and treat underlying cause (sepsis, hypovolemia, obstruction, nephrotoxins)",
                "Optimize volume status - avoid both hypovolemia and hypervolemia",
                "Discontinue or dose-adjust nephrotoxic medications",
                "Avoid contrast if possible; if needed, use minimal iso-osmolar contrast with hydration",
                "Monitor creatinine every 24-48 hours",
            ]
            next_steps = [
                "Serial creatinine monitoring",
                "Medication review for nephrotoxins",
                "Consider urinalysis and urine electrolytes",
                "Renal ultrasound if obstruction suspected",
                "Nephrology consult if no clear cause or not improving",
            ]
            warnings = [
                "Stage 1 AKI can progress to higher stages if cause not addressed."
            ]

        elif stage == 2:
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            summary = "KDIGO AKI Stage 2: Moderate acute kidney injury"
            detail = (
                "Stage 2 AKI: Creatinine 2.0-2.9x baseline OR urine output "
                "<0.5 mL/kg/h for ≥12 hours. Significant injury requiring "
                "aggressive intervention and close monitoring."
            )
            recommendations = [
                "Urgent identification of AKI etiology",
                "Consider nephrology consultation",
                "Aggressive hemodynamic optimization",
                "Stop all nephrotoxic agents",
                "Renal-dose adjust all medications",
                "Avoid hyperkalemia, acidosis, fluid overload",
                "Monitor for uremic symptoms",
            ]
            next_steps = [
                "Nephrology consultation recommended",
                "Daily (or more frequent) creatinine monitoring",
                "Check electrolytes, acid-base status",
                "Renal ultrasound if not done",
                "Consider urinary catheter for accurate output measurement",
                "Prepare for potential RRT if deteriorating",
            ]
            warnings = [
                "Stage 2 AKI carries significant mortality risk.",
                "May progress to Stage 3 requiring dialysis.",
                "Watch for hyperkalemia, severe acidosis, volume overload as RRT indications.",
            ]

        else:  # Stage 3
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH

            if on_rrt:
                summary = "KDIGO AKI Stage 3: Severe AKI on renal replacement therapy"
                detail = (
                    "Stage 3 AKI by RRT criterion. Patient already receiving dialysis "
                    "or CRRT. Continue RRT and supportive care while addressing "
                    "underlying cause. Monitor for renal recovery."
                )
            else:
                summary = "KDIGO AKI Stage 3: Severe acute kidney injury"
                detail = (
                    "Stage 3 AKI: Creatinine ≥3.0x baseline OR ≥4.0 mg/dL OR "
                    "urine output <0.3 mL/kg/h for ≥24h OR anuria for ≥12h. "
                    "Severe injury with high mortality. May require RRT."
                )

            recommendations = [
                "Urgent nephrology involvement essential",
                "Evaluate for RRT indications:",
                "  - Refractory hyperkalemia (K >6.5 despite medical therapy)",
                "  - Severe metabolic acidosis (pH <7.1)",
                "  - Refractory volume overload/pulmonary edema",
                "  - Uremic complications (encephalopathy, pericarditis, bleeding)",
                "  - Toxic ingestion requiring dialysis",
                "ICU-level monitoring if not already",
                "Complete medication reconciliation for renal dosing",
            ]
            next_steps = [
                "Immediate nephrology consult if not done",
                "Prepare for RRT (dialysis catheter access planning)",
                "Strict I/O monitoring",
                "Frequent electrolyte and acid-base monitoring",
                "Assess for RRT indications at least twice daily",
                "Daily reassessment of renal recovery potential",
            ]
            warnings = [
                "Stage 3 AKI has high mortality (40-60% in critically ill).",
                "RRT indications are ABSOLUTE - do not delay if present.",
                "Continue to address underlying cause even while on RRT.",
                "Some patients may recover; monitor for return of urine output.",
            ]

        # Add additional context
        stage_criteria = {
            0: "Does not meet AKI criteria",
            1: "Cr 1.5-1.9x baseline OR +0.3 mg/dL OR UO <0.5 mL/kg/h × 6-12h",
            2: "Cr 2.0-2.9x baseline OR UO <0.5 mL/kg/h × ≥12h",
            3: "Cr ≥3.0x baseline OR ≥4.0 mg/dL OR UO <0.3 mL/kg/h × ≥24h OR anuria ≥12h OR RRT",
        }

        return Interpretation(
            summary=summary,
            severity=severity,
            detail=detail,
            stage=f"KDIGO AKI Stage {stage}" if stage > 0 else "No AKI",
            stage_description=stage_criteria[stage],
            risk_level=risk_level,
            recommendations=tuple(recommendations),
            next_steps=tuple(next_steps),
            warnings=tuple(warnings) if warnings else (),
        )
