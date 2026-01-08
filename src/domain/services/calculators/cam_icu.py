"""
CAM-ICU (Confusion Assessment Method for ICU)

The CAM-ICU is a delirium screening instrument for ICU patients that
can be administered by non-psychiatric physicians and ICU nurses. It
is the most widely used delirium screening tool in critical care.

Reference (Original CAM):
    Inouye SK, van Dyck CH, Alessi CA, et al. Clarifying confusion: the
    confusion assessment method. A new method for detection of delirium.
    Ann Intern Med. 1990;113(12):941-948.
    DOI: 10.7326/0003-4819-113-12-941
    PMID: 2240918

Reference (CAM-ICU):
    Ely EW, Inouye SK, Bernard GR, et al. Delirium in mechanically
    ventilated patients: validity and reliability of the confusion
    assessment method for the intensive care unit (CAM-ICU).
    JAMA. 2001;286(21):2703-2710.
    DOI: 10.1001/jama.286.21.2703
    PMID: 11730446

Guideline:
    Devlin JW, Skrobik Y, Gélinas C, et al. Clinical Practice Guidelines
    for the Prevention and Management of Pain, Agitation/Sedation,
    Delirium, Immobility, and Sleep Disruption in Adult Patients in the
    ICU. Crit Care Med. 2018;46(9):e825-e873.
    DOI: 10.1097/CCM.0000000000003299
    PMID: 30113379
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class CamIcuCalculator(BaseCalculator):
    """
    CAM-ICU (Confusion Assessment Method for ICU) Calculator

    The CAM-ICU assesses four features:
    1. Feature 1: Acute onset or fluctuating course
    2. Feature 2: Inattention
    3. Feature 3: Altered level of consciousness
    4. Feature 4: Disorganized thinking

    CAM-ICU Positive (Delirium Present):
    - Feature 1 AND Feature 2 AND (Feature 3 OR Feature 4)

    Prerequisites:
    - Patient must be arousable (RASS ≥ -3)
    - If RASS is -4 or -5, patient is comatose and CAM-ICU cannot be assessed
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="cam_icu",
                name="CAM-ICU (Confusion Assessment Method for ICU)",
                purpose="Screen for delirium in ICU patients",
                input_params=["rass_score", "acute_onset_fluctuation", "inattention", "altered_loc", "disorganized_thinking"],
                output_type="Delirium status (Positive/Negative/Unable to Assess)",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CRITICAL_CARE,
                    Specialty.ANESTHESIOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.NEUROLOGY,
                    Specialty.PSYCHIATRY,
                ),
                conditions=(
                    "Delirium",
                    "ICU Delirium",
                    "Acute Confusional State",
                    "Encephalopathy",
                    "Altered Mental Status",
                    "Confusion",
                    "Agitation",
                ),
                clinical_contexts=(
                    ClinicalContext.DELIRIUM_ASSESSMENT,
                    ClinicalContext.ICU_MANAGEMENT,
                    ClinicalContext.SEDATION_ASSESSMENT,
                    ClinicalContext.MONITORING,
                    ClinicalContext.SCREENING,
                ),
                clinical_questions=(
                    "Does this patient have delirium?",
                    "Is this altered mental status from delirium or something else?",
                    "Should we screen for delirium?",
                    "Is the patient's confusion acute?",
                    "Is this patient at risk for prolonged ICU stay?",
                ),
                icd10_codes=("F05", "R41.0", "R41.82"),
                keywords=(
                    "CAM-ICU",
                    "delirium",
                    "confusion",
                    "ICU delirium",
                    "altered mental status",
                    "encephalopathy",
                    "inattention",
                    "acute confusion",
                    "screening",
                    "PADIS",
                ),
            ),
            references=(
                Reference(
                    citation="Ely EW, Inouye SK, Bernard GR, et al. Delirium in mechanically "
                    "ventilated patients: validity and reliability of the confusion "
                    "assessment method for the intensive care unit (CAM-ICU). "
                    "JAMA. 2001;286(21):2703-2710.",
                    doi="10.1001/jama.286.21.2703",
                    pmid="11730446",
                    year=2001,
                ),
                Reference(
                    citation="Inouye SK, van Dyck CH, Alessi CA, et al. Clarifying confusion: "
                    "the confusion assessment method. A new method for detection of "
                    "delirium. Ann Intern Med. 1990;113(12):941-948.",
                    doi="10.7326/0003-4819-113-12-941",
                    pmid="2240918",
                    year=1990,
                ),
                Reference(
                    citation="Devlin JW, Skrobik Y, Gélinas C, et al. Clinical Practice Guidelines "
                    "for the Prevention and Management of Pain, Agitation/Sedation, "
                    "Delirium, Immobility, and Sleep Disruption in Adult Patients in the "
                    "ICU. Crit Care Med. 2018;46(9):e825-e873.",
                    doi="10.1097/CCM.0000000000003299",
                    pmid="30113379",
                    year=2018,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        rass_score: int,
        acute_onset_fluctuation: bool,
        inattention_score: int,
        altered_loc: bool = False,
        disorganized_thinking_errors: int = 0,
    ) -> ScoreResult:
        """
        Calculate CAM-ICU delirium assessment.

        Args:
            rass_score: RASS score (-5 to +4)
                If RASS is -4 or -5, patient is comatose and CAM-ICU cannot be assessed
            acute_onset_fluctuation: Feature 1 - Acute change in mental status or
                fluctuating course over past 24 hours
            inattention_score: Feature 2 - Number of errors in Attention Screening
                Examination (ASE). ≥3 errors = inattention positive
            altered_loc: Feature 3 - Current RASS is not 0 (any RASS ≠ 0)
                If not provided, will be calculated from rass_score
            disorganized_thinking_errors: Feature 4 - Number of errors on 4 simple
                yes/no questions + command following. ≥2 errors = positive

        Returns:
            ScoreResult with delirium status
        """
        # Validate RASS
        if not -5 <= rass_score <= 4:
            raise ValueError("RASS must be between -5 and +4")
        if not 0 <= inattention_score <= 10:
            raise ValueError("Inattention score (ASE errors) must be between 0 and 10")
        if not 0 <= disorganized_thinking_errors <= 5:
            raise ValueError("Disorganized thinking errors must be between 0 and 5")

        # Check if patient is arousable
        if rass_score <= -4:
            return self._comatose_result(rass_score)

        # Evaluate features
        feature_1 = acute_onset_fluctuation
        feature_2 = inattention_score >= 3  # ≥3 errors on ASE = inattention
        feature_3 = rass_score != 0 or altered_loc  # RASS ≠ 0 = altered LOC
        feature_4 = disorganized_thinking_errors >= 2  # ≥2 errors

        # CAM-ICU algorithm
        # Positive if: Feature 1 AND Feature 2 AND (Feature 3 OR Feature 4)
        cam_icu_positive = feature_1 and feature_2 and (feature_3 or feature_4)

        # Get interpretation
        interpretation = self._get_interpretation(cam_icu_positive, feature_1, feature_2, feature_3, feature_4, rass_score)

        return ScoreResult(
            value=1 if cam_icu_positive else 0,
            unit=Unit.BINARY,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "rass_score": rass_score,
                "acute_onset_fluctuation": acute_onset_fluctuation,
                "inattention_score": inattention_score,
                "altered_loc": altered_loc,
                "disorganized_thinking_errors": disorganized_thinking_errors,
            },
            calculation_details={
                "feature_1_acute_onset": {"present": feature_1, "description": "Acute change or fluctuating course"},
                "feature_2_inattention": {
                    "present": feature_2,
                    "errors": inattention_score,
                    "description": f"ASE errors: {inattention_score} (≥3 = inattention)",
                },
                "feature_3_altered_loc": {"present": feature_3, "rass": rass_score, "description": f"RASS {rass_score} (≠0 = altered LOC)"},
                "feature_4_disorganized_thinking": {
                    "present": feature_4,
                    "errors": disorganized_thinking_errors,
                    "description": f"Errors: {disorganized_thinking_errors} (≥2 = positive)",
                },
                "algorithm": "Feature 1 AND Feature 2 AND (Feature 3 OR Feature 4)",
                "result": "POSITIVE (Delirium)" if cam_icu_positive else "NEGATIVE (No Delirium)",
            },
            formula_used="CAM-ICU+ = (Acute onset/Fluctuation) AND (Inattention) AND (Altered LOC OR Disorganized Thinking)",
        )

    def _comatose_result(self, rass_score: int) -> ScoreResult:
        """Return result for comatose patient (RASS -4 or -5)"""
        return ScoreResult(
            value=-1,  # Special value indicating unable to assess
            unit=Unit.BINARY,
            interpretation=Interpretation(
                summary="CAM-ICU: Unable to Assess - Patient Comatose",
                detail=f"Patient has RASS of {rass_score}, indicating coma or deep sedation. CAM-ICU cannot be performed. Reassess when RASS ≥ -3.",
                severity=Severity.CRITICAL,
                stage="Comatose",
                stage_description="Unable to assess - too sedated or comatose",
                recommendations=(
                    "CAM-ICU requires RASS ≥ -3 to perform",
                    "Reassess when sedation lightened or patient awakens",
                    "Consider if deep sedation is clinically indicated",
                    "If sedation can be reduced, attempt arousal and reassess",
                ),
                warnings=(
                    "Deep sedation/coma prevents delirium assessment",
                    "Prolonged sedation is associated with worse outcomes",
                ),
                next_steps=(
                    "Continue monitoring sedation level",
                    "Daily sedation interruption trial if appropriate",
                    "Reassess CAM-ICU when RASS improves to -3 or better",
                ),
            ),
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={"rass_score": rass_score},
            calculation_details={
                "rass_score": rass_score,
                "arousable": False,
                "result": "UNABLE TO ASSESS - COMATOSE",
            },
            formula_used="CAM-ICU requires RASS ≥ -3",
        )

    def _get_interpretation(self, positive: bool, f1: bool, f2: bool, f3: bool, f4: bool, rass: int) -> Interpretation:
        """Get interpretation based on CAM-ICU result"""

        features_present = []
        if f1:
            features_present.append("Acute onset/fluctuation")
        if f2:
            features_present.append("Inattention")
        if f3:
            features_present.append("Altered LOC")
        if f4:
            features_present.append("Disorganized thinking")

        features_text = ", ".join(features_present) if features_present else "None"

        if positive:
            # Determine delirium subtype
            if rass > 0:
                subtype = "Hyperactive delirium (agitated)"
            elif rass < 0:
                subtype = "Hypoactive delirium (quiet/withdrawn)"
            else:
                subtype = "Mixed delirium"

            return Interpretation(
                summary=f"CAM-ICU POSITIVE: Delirium Present ({subtype})",
                detail=f"Patient meets criteria for delirium. Features present: {features_text}. "
                f"RASS {rass} suggests {subtype}. "
                f"Delirium is associated with increased mortality, longer ICU stay, "
                f"and long-term cognitive impairment.",
                severity=Severity.MODERATE,
                stage="Positive",
                stage_description="Delirium present",
                recommendations=(
                    "Search for and treat underlying causes (THINK mnemonic):",
                    "- Toxic: medication review, especially sedatives, anticholinergics",
                    "- Hypoxemia, metabolic disturbances",
                    "- Infection/Inflammation: sepsis workup",
                    "- Nonpharmacologic interventions: sleep hygiene, early mobility",
                    "- K+ and electrolyte abnormalities",
                    "Follow PADIS guidelines for delirium management",
                    "Minimize sedation, prefer dexmedetomidine if needed",
                    "Avoid physical restraints if possible",
                    "Family involvement and reorientation",
                ),
                warnings=(
                    "Delirium increases ICU and hospital mortality",
                    "Associated with long-term cognitive impairment",
                    "Each day of delirium associated with 10% increase in mortality",
                    f"Subtype: {subtype}",
                ),
                next_steps=(
                    "Identify and treat precipitating causes",
                    "Review medication list for deliriogenic drugs",
                    "Optimize sleep-wake cycle",
                    "Early mobilization if safe",
                    "Reassess CAM-ICU every shift",
                ),
            )
        else:
            return Interpretation(
                summary="CAM-ICU NEGATIVE: No Delirium Detected",
                detail=f"Patient does not currently meet criteria for delirium. "
                f"Features present: {features_text}. "
                f"Continue routine screening as delirium can develop at any time.",
                severity=Severity.NORMAL,
                stage="Negative",
                stage_description="No delirium detected",
                recommendations=(
                    "Continue routine CAM-ICU screening (at least twice daily)",
                    "Maintain delirium prevention strategies:",
                    "- Minimize sedation",
                    "- Early mobilization",
                    "- Sleep hygiene",
                    "- Cognitive stimulation",
                    "- Reorient patient frequently",
                ),
                next_steps=(
                    "Continue CAM-ICU screening every shift",
                    "Maintain prevention bundle",
                    "Monitor for changes in mental status",
                ),
            )
