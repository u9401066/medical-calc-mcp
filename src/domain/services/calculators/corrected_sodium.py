"""
Corrected Sodium Calculator

Calculates the corrected sodium level for hyperglycemia.
High glucose causes osmotic shift of water from intracellular to extracellular space,
diluting serum sodium.

Reference:
    Katz MA. Hyperglycemia-induced hyponatremia—calculation of expected serum
    sodium depression. N Engl J Med. 1973;289(16):843-844.
    DOI: 10.1056/NEJM197310182891607
    PMID: 4763428

    Hillier TA, Abbott RD, Barrett EJ. Hyponatremia: evaluating the correction
    factor for hyperglycemia. Am J Med. 1999;106(4):399-403.
    DOI: 10.1016/S0002-9343(99)00055-8
    PMID: 10225241
"""

from typing import Literal

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class CorrectedSodiumCalculator(BaseCalculator):
    """
    Corrected Sodium Calculator for Hyperglycemia

    Hyperglycemia causes an osmotic shift of water from ICF to ECF,
    diluting the serum sodium. The corrected sodium estimates what
    the sodium would be if glucose were normal.

    Formulas:
        Katz (1973): Corrected Na = Measured Na + 1.6 × ((Glucose - 100) / 100)
        Hillier (1999): Corrected Na = Measured Na + 2.4 × ((Glucose - 100) / 100)

    Note:
        - Katz formula: Standard, most widely used
        - Hillier formula: May be more accurate at very high glucose (>400 mg/dL)

    Clinical Application:
        - DKA (Diabetic Ketoacidosis)
        - HHS (Hyperosmolar Hyperglycemic State)
        - Hyperglycemic emergencies
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="corrected_sodium",
                name="Corrected Sodium for Hyperglycemia",
                purpose="Calculate true sodium level corrected for hyperglycemic dilution",
                input_params=["measured_sodium", "glucose", "formula (optional)"],
                output_type="Corrected Sodium (mEq/L)",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CRITICAL_CARE,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.ENDOCRINOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.NEPHROLOGY,
                ),
                conditions=(
                    "Diabetic Ketoacidosis",
                    "DKA",
                    "Hyperosmolar Hyperglycemic State",
                    "HHS",
                    "Hyperglycemia",
                    "Hyponatremia",
                    "Pseudohyponatremia",
                    "Diabetes Mellitus",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.ICU_MANAGEMENT,
                    ClinicalContext.MONITORING,
                    ClinicalContext.FLUID_MANAGEMENT,
                ),
                clinical_questions=(
                    "What is the true sodium level in this hyperglycemic patient?",
                    "Is this hyponatremia real or due to hyperglycemia?",
                    "What sodium level should I expect when glucose normalizes?",
                    "Does this DKA patient have true sodium derangement?",
                ),
                icd10_codes=("E10.10", "E11.10", "E11.00", "E87.1", "E13.00"),
                keywords=(
                    "corrected sodium",
                    "hyperglycemia",
                    "DKA",
                    "HHS",
                    "pseudohyponatremia",
                    "sodium correction",
                    "glucose",
                    "dilutional hyponatremia",
                ),
            ),
            references=(
                Reference(
                    citation="Katz MA. Hyperglycemia-induced hyponatremia—calculation of expected serum sodium depression. N Engl J Med. 1973;289(16):843-844.",
                    doi="10.1056/NEJM197310182891607",
                    pmid="4763428",
                    year=1973,
                ),
                Reference(
                    citation="Hillier TA, Abbott RD, Barrett EJ. Hyponatremia: evaluating the "
                    "correction factor for hyperglycemia. Am J Med. 1999;106(4):399-403.",
                    doi="10.1016/S0002-9343(99)00055-8",
                    pmid="10225241",
                    year=1999,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        measured_sodium: float,
        glucose: float,
        formula: Literal["katz", "hillier"] = "katz",
        glucose_unit: Literal["mg/dL", "mmol/L"] = "mg/dL",
    ) -> ScoreResult:
        """
        Calculate corrected sodium for hyperglycemia.

        Args:
            measured_sodium: Measured serum sodium in mEq/L (100-180)
            glucose: Blood glucose level
            formula: "katz" (1.6 factor) or "hillier" (2.4 factor)
            glucose_unit: "mg/dL" or "mmol/L"

        Returns:
            ScoreResult with corrected sodium and interpretation
        """
        # Validate measured sodium
        if not 100 <= measured_sodium <= 180:
            raise ValueError("Measured sodium must be between 100 and 180 mEq/L")

        # Convert glucose to mg/dL if needed
        if glucose_unit == "mmol/L":
            glucose_mgdl = glucose * 18.0  # Convert mmol/L to mg/dL
        else:
            glucose_mgdl = glucose

        # Validate glucose
        if not 70 <= glucose_mgdl <= 2000:
            raise ValueError("Glucose must be between 70 and 2000 mg/dL (or 3.9-111 mmol/L)")

        # Calculate correction
        if formula == "katz":
            correction_factor = 1.6
        else:  # hillier
            correction_factor = 2.4

        # Correction formula: Na_corrected = Na_measured + factor × ((Glucose - 100) / 100)
        glucose_excess = (glucose_mgdl - 100) / 100
        sodium_correction = correction_factor * glucose_excess
        corrected_sodium = measured_sodium + sodium_correction

        # Round results
        corrected_sodium = round(corrected_sodium, 1)
        sodium_correction = round(sodium_correction, 1)

        # Get interpretation
        interpretation = self._get_interpretation(measured_sodium, corrected_sodium, sodium_correction, glucose_mgdl)

        return ScoreResult(
            value=corrected_sodium,
            unit=Unit.MEQ_L,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "measured_sodium": measured_sodium,
                "glucose": glucose,
                "glucose_unit": glucose_unit,
                "formula": formula,
            },
            calculation_details={
                "measured_sodium": measured_sodium,
                "glucose_mg_dl": round(glucose_mgdl, 1),
                "correction_factor": correction_factor,
                "sodium_correction": sodium_correction,
                "corrected_sodium": corrected_sodium,
                "formula_used": formula,
            },
            formula_used=f"Corrected Na = Measured Na + {correction_factor} × ((Glucose - 100) / 100)",
        )

    def _get_interpretation(self, measured_na: float, corrected_na: float, correction: float, glucose: float) -> Interpretation:
        """Get clinical interpretation based on corrected sodium"""

        # Determine glucose severity
        if glucose >= 600:
            glucose_severity = "severe hyperglycemia (consider HHS)"
        elif glucose >= 400:
            glucose_severity = "significant hyperglycemia"
        elif glucose >= 250:
            glucose_severity = "moderate hyperglycemia"
        else:
            glucose_severity = "mild hyperglycemia"

        # Interpret corrected sodium
        if corrected_na < 130:
            # True hyponatremia
            if corrected_na < 120:
                severity = Severity.CRITICAL
                na_status = "severe hyponatremia"
            elif corrected_na < 125:
                severity = Severity.SEVERE
                na_status = "moderate hyponatremia"
            else:
                severity = Severity.MODERATE
                na_status = "mild hyponatremia"

            return Interpretation(
                summary=f"True Hyponatremia: Corrected Na = {corrected_na} mEq/L ({na_status})",
                detail=f"After correcting for {glucose_severity} (glucose {glucose} mg/dL), "
                f"the patient has true hyponatremia. Measured Na: {measured_na}, "
                f"Correction: +{correction} mEq/L. "
                f"The hyponatremia is NOT solely due to hyperglycemia.",
                severity=severity,
                stage=na_status.title(),
                stage_description=f"True {na_status}",
                recommendations=(
                    "Evaluate for other causes of hyponatremia",
                    "Treat hyperglycemia AND hyponatremia",
                    "Monitor sodium closely during glucose correction",
                    "Avoid rapid sodium correction (>10-12 mEq/L per 24h risk of ODS)",
                ),
                warnings=(
                    "True hyponatremia present - not just dilutional from glucose",
                    "Risk of overcorrection as glucose normalizes",
                )
                if corrected_na < 125
                else ("True hyponatremia present",),
                next_steps=(
                    "Calculate free water excess",
                    "Plan fluid strategy accounting for both glucose and Na",
                    "Frequent electrolyte monitoring (q2-4h)",
                ),
            )
        elif corrected_na > 145:
            # Hypernatremia
            if corrected_na > 160:
                severity = Severity.CRITICAL
                na_status = "severe hypernatremia"
            elif corrected_na > 150:
                severity = Severity.SEVERE
                na_status = "moderate hypernatremia"
            else:
                severity = Severity.MODERATE
                na_status = "mild hypernatremia"

            return Interpretation(
                summary=f"Hypernatremia: Corrected Na = {corrected_na} mEq/L ({na_status})",
                detail=f"After correcting for {glucose_severity} (glucose {glucose} mg/dL), "
                f"the patient has hypernatremia. Measured Na: {measured_na}, "
                f"Correction: +{correction} mEq/L. "
                f"This indicates significant free water deficit.",
                severity=severity,
                stage=na_status.title(),
                stage_description=na_status,
                recommendations=(
                    "Calculate free water deficit",
                    "Correct hypernatremia gradually (max 10 mEq/L per 24h)",
                    "Use hypotonic fluids for correction",
                    "Monitor for cerebral edema during correction",
                ),
                warnings=(
                    "Significant free water deficit",
                    "Common in HHS - patient is severely dehydrated",
                    "Sodium will rise further as glucose is corrected with insulin",
                ),
                next_steps=(
                    "Calculate free water deficit",
                    "Plan fluid resuscitation with appropriate Na content",
                    "Frequent monitoring (q2-4h)",
                ),
            )
        else:
            # Normal corrected sodium
            return Interpretation(
                summary=f"Normal Corrected Sodium: {corrected_na} mEq/L",
                detail=f"After correcting for {glucose_severity} (glucose {glucose} mg/dL), "
                f"sodium is within normal range. Measured Na: {measured_na}, "
                f"Correction: +{correction} mEq/L. "
                f"The low measured sodium is primarily due to hyperglycemic dilution.",
                severity=Severity.NORMAL if correction < 5 else Severity.MILD,
                stage="Normal (corrected)",
                stage_description="Normal sodium after correction",
                recommendations=(
                    "Focus on treating hyperglycemia",
                    "Expect sodium to rise as glucose normalizes",
                    "Use isotonic saline for initial resuscitation",
                    "Monitor sodium during treatment",
                ),
                next_steps=(
                    "Treat underlying hyperglycemia (insulin, fluids)",
                    "Sodium should normalize with glucose correction",
                    "Recheck electrolytes in 2-4 hours",
                ),
            )
