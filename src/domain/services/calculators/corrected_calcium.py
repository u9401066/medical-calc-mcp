"""
Albumin-Corrected Calcium Calculator

Corrects total calcium for albumin concentration to estimate
physiologically active ionized calcium when direct measurement unavailable.

References:
    Payne RB, Little AJ, Williams RB, Milner JR. Interpretation of serum
    calcium in patients with abnormal serum proteins.
    Br Med J. 1973;4(5893):643-646.
    DOI: 10.1136/bmj.4.5893.643
    PMID: 4758544

    Bushinsky DA, Monk RD. Electrolyte quintet: Calcium.
    Lancet. 1998;352(9124):306-311.
    DOI: 10.1016/S0140-6736(97)12331-5
    PMID: 9690425

    James MT, Zhang J, Lyon AW, Bhatta S, Bhattarai B, Chen G, Hemmelgarn
    BR. Derivation and internal validation of an equation for albumin-
    adjusted calcium. BMC Clin Pathol. 2008;8:12.
    DOI: 10.1186/1472-6890-8-12
    PMID: 19059239
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import (
    ClinicalContext,
    HighLevelKey,
    LowLevelKey,
    Specialty,
)
from ...value_objects.units import Unit
from ..base import BaseCalculator


class CorrectedCalciumCalculator(BaseCalculator):
    """
    Albumin-Corrected Calcium Calculator

    Corrects total calcium for hypoalbuminemia to estimate true calcium status.

    Formula (Payne 1973):
        Corrected Ca = Measured Ca + 0.8 × (4.0 - Albumin)

    Alternative formulas:
        - Original Payne (g/L): Ca + 0.02 × (40 - Albumin g/L)
        - Some institutions use 0.025 instead of 0.02

    Physiology:
        - ~40% calcium is protein-bound (mainly albumin)
        - ~50% is ionized (physiologically active)
        - ~10% is complexed with anions
        - Low albumin → artificially low total calcium

    Clinical Use:
        - Hypoalbuminemia (malnutrition, liver disease, nephrotic syndrome)
        - Critically ill patients
        - When ionized calcium not available

    Limitations:
        - Less accurate in acid-base disturbances
        - Less accurate in critically ill patients
        - Ionized calcium preferred if available
        - Formula validated at albumin 2.5-4.5 g/dL
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="corrected_calcium",
                name="Albumin-Corrected Calcium",
                purpose="Correct total calcium for hypoalbuminemia",
                input_params=["calcium_mg_dl", "albumin_g_dl"],
                output_type="Corrected calcium (mg/dL) with interpretation",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.CRITICAL_CARE,
                    Specialty.NEPHROLOGY,
                    Specialty.ENDOCRINOLOGY,
                    Specialty.ONCOLOGY,
                    Specialty.HEPATOLOGY,
                    Specialty.GERIATRICS,
                ),
                conditions=(
                    "Hypocalcemia",
                    "Hypercalcemia",
                    "Hypoalbuminemia",
                    "Malnutrition",
                    "Cirrhosis",
                    "Nephrotic syndrome",
                    "Critical illness",
                    "Malignancy",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.MONITORING,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "What is the true calcium level?",
                    "How do I correct calcium for low albumin?",
                    "Is this hypocalcemia real or from low albumin?",
                    "Should I treat this low calcium?",
                    "What is the corrected calcium in liver disease?",
                ),
                icd10_codes=(
                    "E83.51",  # Hypocalcemia
                    "E83.52",  # Hypercalcemia
                    "E44",  # Protein-calorie malnutrition
                    "K74",  # Cirrhosis
                    "N04",  # Nephrotic syndrome
                ),
            ),
            references=(
                Reference(
                    citation=(
                        "Payne RB, Little AJ, Williams RB, Milner JR. Interpretation of "
                        "serum calcium in patients with abnormal serum proteins. "
                        "Br Med J. 1973;4(5893):643-646."
                    ),
                    doi="10.1136/bmj.4.5893.643",
                    pmid="4758544",
                    year=1973,
                ),
                Reference(
                    citation=("Bushinsky DA, Monk RD. Electrolyte quintet: Calcium. Lancet. 1998;352(9124):306-311."),
                    doi="10.1016/S0140-6736(97)12331-5",
                    pmid="9690425",
                    year=1998,
                ),
                Reference(
                    citation=(
                        "James MT, Zhang J, Lyon AW, et al. Derivation and internal "
                        "validation of an equation for albumin-adjusted calcium. "
                        "BMC Clin Pathol. 2008;8:12."
                    ),
                    doi="10.1186/1472-6890-8-12",
                    pmid="19059239",
                    year=2008,
                ),
            ),
        )

    def calculate(
        self,
        calcium_mg_dl: float,
        albumin_g_dl: float,
        normal_albumin: float = 4.0,
    ) -> ScoreResult:
        """
        Calculate albumin-corrected calcium.

        Args:
            calcium_mg_dl: Total serum calcium in mg/dL (4.0-16.0)
            albumin_g_dl: Serum albumin in g/dL (1.0-6.0)
            normal_albumin: Reference normal albumin (default 4.0 g/dL)

        Returns:
            ScoreResult with corrected calcium in mg/dL

        Raises:
            ValueError: If parameters are out of valid range
        """
        # Validate inputs
        if not 4.0 <= calcium_mg_dl <= 16.0:
            raise ValueError(f"Calcium must be 4.0-16.0 mg/dL, got {calcium_mg_dl}")
        if not 1.0 <= albumin_g_dl <= 6.0:
            raise ValueError(f"Albumin must be 1.0-6.0 g/dL, got {albumin_g_dl}")
        if not 3.5 <= normal_albumin <= 5.0:
            raise ValueError(f"Normal albumin must be 3.5-5.0 g/dL, got {normal_albumin}")

        # Calculate corrected calcium
        # Payne formula: for each 1 g/dL albumin below 4.0, add 0.8 mg/dL to calcium
        correction = 0.8 * (normal_albumin - albumin_g_dl)
        corrected_ca = calcium_mg_dl + correction

        # Get interpretation
        interpretation = self._get_interpretation(calcium_mg_dl, albumin_g_dl, corrected_ca)

        return ScoreResult(
            tool_id=self.tool_id,
            tool_name=self.name,
            value=float(round(corrected_ca, 1)),
            unit=Unit.MG_DL,
            interpretation=interpretation,
            references=list(self.references),
            calculation_details={
                "measured_calcium_mg_dl": calcium_mg_dl,
                "albumin_g_dl": albumin_g_dl,
                "normal_albumin_g_dl": normal_albumin,
                "correction_factor": 0.8,
                "correction_applied_mg_dl": round(correction, 2),
                "corrected_calcium_mg_dl": round(corrected_ca, 1),
                "formula": f"Corrected Ca = {calcium_mg_dl} + 0.8 × ({normal_albumin} - {albumin_g_dl})",
                "reference_ranges": {
                    "normal_total_calcium": "8.5-10.5 mg/dL",
                    "hypocalcemia": "<8.5 mg/dL",
                    "hypercalcemia": ">10.5 mg/dL",
                    "severe_hypercalcemia": ">14.0 mg/dL",
                },
                "hypoalbuminemia_present": albumin_g_dl < 3.5,
            },
        )

    def _get_interpretation(self, measured_ca: float, albumin: float, corrected_ca: float) -> Interpretation:
        """Generate interpretation based on corrected calcium value"""
        recommendations: tuple[str, ...]
        warnings: tuple[str, ...]

        hypoalb = albumin < 3.5
        correction_direction = "up" if corrected_ca > measured_ca else "down"

        # Classify corrected calcium
        if corrected_ca < 7.0:
            level = "Severe hypocalcemia"
            severity = Severity.CRITICAL
            recommendations = (
                "URGENT: Assess for symptoms (tetany, seizures, arrhythmia)",
                "IV calcium gluconate 1-2g if symptomatic",
                "Check ionized calcium to confirm",
                "Evaluate for hypoparathyroidism, vitamin D deficiency",
                "Check magnesium (hypomagnesemia impairs PTH)",
                "Continuous cardiac monitoring",
            )
            warnings = (
                "Life-threatening if symptomatic",
                "Risk of QT prolongation and arrhythmia",
                "IV calcium can cause tissue necrosis if extravasated",
            )
        elif corrected_ca < 8.5:
            level = "Hypocalcemia"
            severity = Severity.MODERATE
            recommendations = (
                "Assess for symptoms (paresthesias, muscle cramps)",
                "Check ionized calcium for confirmation",
                "Evaluate cause: vitamin D, PTH, magnesium",
                "Oral calcium and vitamin D if mild and asymptomatic",
                "IV calcium if symptomatic",
            )
            warnings = (
                "Confirm with ionized calcium if available",
                "Correction formula less accurate in critical illness",
            )
        elif corrected_ca <= 10.5:
            level = "Normal calcium"
            severity = Severity.NORMAL
            recommendations = (
                "No calcium intervention needed",
                "If hypoalbuminemia present, address underlying cause",
                "Routine monitoring as clinically indicated",
            )
            warnings = ()
        elif corrected_ca <= 12.0:
            level = "Mild hypercalcemia"
            severity = Severity.MILD
            recommendations = (
                "Investigate cause: primary hyperparathyroidism, malignancy",
                "Check PTH, PTHrP, vitamin D levels",
                "Encourage hydration",
                "Review medications (thiazides, lithium, vitamin D/A)",
                "Repeat to confirm if unexpected",
            )
            warnings = (
                "May be asymptomatic",
                "Chronic hypercalcemia can cause nephrocalcinosis",
            )
        elif corrected_ca <= 14.0:
            level = "Moderate hypercalcemia"
            severity = Severity.MODERATE
            recommendations = (
                "Aggressive IV hydration (normal saline)",
                "Urgent workup: PTH, PTHrP, malignancy screen",
                "Consider bisphosphonates if malignancy-related",
                "Monitor renal function and urine output",
                "Avoid thiazides and calcium supplements",
            )
            warnings = (
                "Symptoms common: polyuria, constipation, confusion",
                "Risk of AKI from volume depletion",
                "Malignancy is common cause at this level",
            )
        else:
            level = "Severe hypercalcemia"
            severity = Severity.CRITICAL
            recommendations = (
                "URGENT: Aggressive IV saline resuscitation",
                "Calcitonin for rapid initial lowering",
                "Bisphosphonate (zoledronic acid or pamidronate)",
                "Consider dialysis if refractory or AKI",
                "Cardiac monitoring (risk of arrhythmia)",
                "Urgent oncology/endocrinology consultation",
            )
            warnings = (
                "Life-threatening: cardiac arrhythmia, coma",
                "Often malignancy-related at this level",
                "Requires ICU-level care",
            )

        hypoalb_note = ""
        if hypoalb and correction_direction == "up":
            hypoalb_note = f" Measured calcium ({measured_ca} mg/dL) was falsely low due to hypoalbuminemia (albumin {albumin} g/dL)."

        return Interpretation(
            summary=f"Corrected Ca: {corrected_ca:.1f} mg/dL - {level}",
            detail=(
                f"Albumin-corrected calcium: {corrected_ca:.1f} mg/dL. "
                f"Measured: {measured_ca} mg/dL, Albumin: {albumin} g/dL.{hypoalb_note} "
                f"Correction adds 0.8 mg/dL for each 1 g/dL albumin below 4.0."
            ),
            severity=severity,
            stage=level,
            stage_description=f"Corrected Ca {corrected_ca:.1f} mg/dL",
            recommendations=recommendations,
            warnings=warnings
            + (
                "Ionized calcium is more accurate when available",
                "Formula less reliable in pH disturbances and critical illness",
            )
            if corrected_ca < 8.5 or corrected_ca > 10.5
            else ("Ionized calcium is gold standard but often not needed if corrected is normal",),
            next_steps=(
                "Check ionized calcium if available and clinical concern",
                "Address underlying cause of albumin abnormality",
                "Monitor and repeat as clinically indicated",
            ),
        )
