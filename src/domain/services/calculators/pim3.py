"""
Pediatric Index of Mortality 3 (PIM3) Calculator

Predicts mortality risk for children admitted to PICU based on data
available at the time of first face-to-face contact with ICU physician.

Clinical Application:
- PICU quality benchmarking (risk-adjusted mortality)
- Resource allocation
- Research standardization
- NOT for individual patient prognosis communication

Scoring:
- Uses logistic regression with 10 variables
- Probability of death = 1 / (1 + e^(-logit))

Key Variables:
1. Elective admission
2. Recovery post-procedure
3. Cardiac bypass
4. High-risk diagnosis (spontaneous cerebral hemorrhage, cardiomyopathy, etc.)
5. Low-risk diagnosis (asthma, bronchiolitis, croup, etc.)
6. Very high-risk diagnosis (cardiac arrest, leukemia/lymphoma after first induction)
7. Pupillary reaction
8. Mechanical ventilation in first hour
9. Base excess (absolute, most abnormal)
10. Systolic blood pressure at admission

References:
    Straney L, Clements A, Parslow RC, et al. Paediatric Index of Mortality 3:
    An Updated Model for Predicting Mortality in Pediatric Intensive Care.
    Pediatr Crit Care Med. 2013;14(7):673-681. PMID: 23863821

    Slater A, Shann F, Pearson G; PIM Study Group. PIM2: a revised version
    of the Paediatric Index of Mortality.
    Intensive Care Med. 2003;29(2):278-285. PMID: 12541154
"""

import math
from typing import Optional

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class PIM3Calculator(BaseCalculator):
    """
    Pediatric Index of Mortality 3 (PIM3) Calculator

    Predicts PICU mortality using admission data.
    Variables collected at first face-to-face ICU contact.
    """

    # PIM3 coefficients (Straney 2013)
    COEFFICIENTS = {
        "intercept": -5.3553,
        "pupillary_both_fixed": 3.8233,
        "elective_admission": -0.5378,
        "mechanical_ventilation": 0.9763,
        "base_excess_absolute": 0.0671,
        "sbp_squared": -0.0431,  # (SBP/100)^2
        "recovery_post_procedure": -1.3766,
        "cardiac_bypass": -1.3431,
        "high_risk_dx": 1.7588,
        "low_risk_dx": -2.1561,
        "very_high_risk_dx": 2.1760,
    }

    # High-risk diagnoses (PIM3 category)
    HIGH_RISK_DIAGNOSES = [
        "spontaneous_cerebral_hemorrhage",
        "cardiomyopathy_myocarditis",
        "hypoplastic_left_heart",
        "neurodegenerative_disease",
        "necrotizing_enterocolitis",
    ]

    # Low-risk diagnoses (PIM3 category)
    LOW_RISK_DIAGNOSES = [
        "asthma",
        "bronchiolitis",
        "croup",
        "obstructive_sleep_apnea",
        "diabetic_ketoacidosis",
        "seizure_disorder",
    ]

    # Very high-risk diagnoses (PIM3 category)
    VERY_HIGH_RISK_DIAGNOSES = [
        "cardiac_arrest_preceding",
        "severe_combined_immunodeficiency",
        "leukemia_lymphoma_first_induction",
        "bone_marrow_transplant_recipient",
        "liver_failure_primary_reason",
    ]

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="pim3",
                name="Pediatric Index of Mortality 3 (PIM3)",
                purpose="Predict PICU mortality for quality benchmarking",
                input_params=[
                    "systolic_bp", "pupillary_reaction", "mechanical_ventilation",
                    "base_excess", "elective_admission", "recovery_post_procedure",
                    "cardiac_bypass", "diagnosis_category"
                ],
                output_type="Predicted mortality probability (%)"
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.PEDIATRICS,
                    Specialty.CRITICAL_CARE,
                    Specialty.PEDIATRIC_CRITICAL_CARE,
                ),
                conditions=(
                    "PICU admission",
                    "Mortality prediction",
                    "Quality benchmarking",
                    "Risk stratification",
                ),
                clinical_contexts=(
                    ClinicalContext.ICU_ASSESSMENT,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.QUALITY_IMPROVEMENT,
                ),
            ),
            references=(
                Reference(
                    citation="Straney L, et al. PIM3: An Updated Model for Predicting Mortality in PICU. Pediatr Crit Care Med. 2013;14(7):673-681.",
                    doi="10.1097/PCC.0b013e31829760cf",
                    pmid="23863821",
                    year=2013
                ),
                Reference(
                    citation="Slater A, Shann F, Pearson G; PIM Study Group. PIM2: a revised version. Intensive Care Med. 2003;29(2):278-285.",
                    pmid="12541154",
                    year=2003
                ),
            ),
        )

    def calculate(
        self,
        systolic_bp: float,
        pupillary_reaction: str,
        mechanical_ventilation: bool,
        base_excess: float,
        elective_admission: bool = False,
        recovery_post_procedure: bool = False,
        cardiac_bypass: bool = False,
        high_risk_diagnosis: bool = False,
        low_risk_diagnosis: bool = False,
        very_high_risk_diagnosis: bool = False,
        diagnosis_name: Optional[str] = None
    ) -> ScoreResult:
        """
        Calculate PIM3 predicted mortality.

        Args:
            systolic_bp: Systolic blood pressure at admission (mmHg)
                Use 0 if cardiac arrest, 30 if too low to measure,
                120 if not measured
            pupillary_reaction: Pupil response to light
                "both_react" = Both pupils react (>3mm, react to light)
                "one_fixed" = One pupil fixed
                "both_fixed" = Both pupils fixed
            mechanical_ventilation: Mechanical ventilation in first hour of ICU
            base_excess: Arterial or capillary base excess (mEq/L, most abnormal in first hour)
                Use 0 if not measured
            elective_admission: Planned admission following elective surgery
            recovery_post_procedure: Admitted for postoperative recovery
            cardiac_bypass: Cardiac bypass during surgery for principal procedure
            high_risk_diagnosis: Has PIM3 high-risk diagnosis
            low_risk_diagnosis: Has PIM3 low-risk diagnosis
            very_high_risk_diagnosis: Has PIM3 very high-risk diagnosis
            diagnosis_name: Optional specific diagnosis name

        Returns:
            ScoreResult with predicted mortality probability
        """
        # Validate inputs
        if systolic_bp < 0 or systolic_bp > 300:
            raise ValueError("systolic_bp must be 0-300 mmHg")

        valid_pupils = ["both_react", "one_fixed", "both_fixed"]
        if pupillary_reaction not in valid_pupils:
            raise ValueError(f"pupillary_reaction must be one of: {valid_pupils}")

        if base_excess < -30 or base_excess > 30:
            raise ValueError("base_excess must be between -30 and 30")

        # Cannot have multiple diagnosis categories
        dx_count = sum([high_risk_diagnosis, low_risk_diagnosis, very_high_risk_diagnosis])
        if dx_count > 1:
            raise ValueError("Patient can only belong to one diagnosis category")

        # Calculate logit
        logit = self.COEFFICIENTS["intercept"]

        # Pupillary reaction
        if pupillary_reaction == "both_fixed":
            logit += self.COEFFICIENTS["pupillary_both_fixed"]

        # Admission type
        if elective_admission:
            logit += self.COEFFICIENTS["elective_admission"]

        # Mechanical ventilation
        if mechanical_ventilation:
            logit += self.COEFFICIENTS["mechanical_ventilation"]

        # Base excess (absolute value)
        logit += self.COEFFICIENTS["base_excess_absolute"] * abs(base_excess)

        # Systolic BP (squared, scaled)
        sbp_scaled = systolic_bp / 100
        logit += self.COEFFICIENTS["sbp_squared"] * (sbp_scaled ** 2)

        # Recovery post-procedure
        if recovery_post_procedure:
            logit += self.COEFFICIENTS["recovery_post_procedure"]

        # Cardiac bypass
        if cardiac_bypass:
            logit += self.COEFFICIENTS["cardiac_bypass"]

        # Diagnosis categories
        if high_risk_diagnosis:
            logit += self.COEFFICIENTS["high_risk_dx"]
        elif low_risk_diagnosis:
            logit += self.COEFFICIENTS["low_risk_dx"]
        elif very_high_risk_diagnosis:
            logit += self.COEFFICIENTS["very_high_risk_dx"]

        # Calculate probability
        probability = 1 / (1 + math.exp(-logit))
        mortality_percent = probability * 100

        # Determine severity category
        if mortality_percent < 1:
            severity = Severity.NORMAL
            risk_category = "Low Risk"
        elif mortality_percent < 5:
            severity = Severity.MILD
            risk_category = "Low-Moderate Risk"
        elif mortality_percent < 15:
            severity = Severity.MODERATE
            risk_category = "Moderate Risk"
        elif mortality_percent < 30:
            severity = Severity.SEVERE
            risk_category = "High Risk"
        else:
            severity = Severity.CRITICAL
            risk_category = "Very High Risk"

        # Build risk factors list
        risk_factors = []
        if pupillary_reaction == "both_fixed":
            risk_factors.append("Both pupils fixed")
        if mechanical_ventilation:
            risk_factors.append("Mechanical ventilation")
        if abs(base_excess) > 10:
            risk_factors.append(f"Severe metabolic derangement (BE: {base_excess})")
        if systolic_bp < 60:
            risk_factors.append(f"Severe hypotension (SBP: {systolic_bp})")
        if very_high_risk_diagnosis:
            risk_factors.append("Very high-risk diagnosis category")
        elif high_risk_diagnosis:
            risk_factors.append("High-risk diagnosis category")

        protective_factors = []
        if elective_admission:
            protective_factors.append("Elective admission")
        if recovery_post_procedure:
            protective_factors.append("Post-procedure recovery")
        if low_risk_diagnosis:
            protective_factors.append("Low-risk diagnosis category")

        interpretation = Interpretation(
            severity=severity,
            summary=f"PIM3 Predicted Mortality: {mortality_percent:.1f}%",
            detail=(
                f"Risk Category: {risk_category}\n"
                f"Logit value: {logit:.3f}\n"
                + (f"Risk factors: {', '.join(risk_factors)}\n" if risk_factors else "")
                + (f"Protective factors: {', '.join(protective_factors)}" if protective_factors else "")
            ),
            recommendations=(
                "PIM3 is for PICU quality benchmarking, not individual prognosis. "
                "Standardized mortality ratio (SMR) = observed/expected deaths.",
            )
        )

        details = {
            "predicted_mortality_percent": round(mortality_percent, 2),
            "logit": round(logit, 4),
            "risk_category": risk_category,
            "risk_factors": risk_factors if risk_factors else None,
            "protective_factors": protective_factors if protective_factors else None,
            "input_summary": {
                "systolic_bp": systolic_bp,
                "pupils": pupillary_reaction,
                "mechanical_vent": mechanical_ventilation,
                "base_excess": base_excess,
                "elective": elective_admission,
                "post_procedure": recovery_post_procedure,
                "bypass": cardiac_bypass,
            },
            "note": "For quality benchmarking only. Do not use for individual patient decisions.",
            "next_step": "Calculate SMR = observed deaths / sum of predicted probabilities"
        }

        return ScoreResult(
            value=round(mortality_percent, 2),
            unit=Unit.PERCENT,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "systolic_bp": systolic_bp,
                "pupillary_reaction": pupillary_reaction,
                "mechanical_ventilation": mechanical_ventilation,
                "base_excess": base_excess,
                "elective_admission": elective_admission,
                "recovery_post_procedure": recovery_post_procedure,
                "cardiac_bypass": cardiac_bypass,
                "high_risk_diagnosis": high_risk_diagnosis,
                "low_risk_diagnosis": low_risk_diagnosis,
                "very_high_risk_diagnosis": very_high_risk_diagnosis,
                "diagnosis_name": diagnosis_name,
            },
            calculation_details=details
        )
