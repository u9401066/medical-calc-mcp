"""
Modified Rankin Scale (mRS)

A standardized scale for measuring disability and dependence after stroke.

Reference:
    van Swieten JC, Koudstaal PJ, Visser MC, Schouten HJ, van Gijn J.
    Interobserver agreement for the assessment of handicap in stroke patients.
    Stroke. 1988;19(5):604-607.
    DOI: 10.1161/01.str.19.5.604
    PMID: 3363593

    Rankin J. Cerebral vascular accidents in patients over the age of 60.
    II. Prognosis.
    Scott Med J. 1957;2(5):200-215.
    PMID: 13432835
"""

from typing import Literal

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class ModifiedRankinScaleCalculator(BaseCalculator):
    """
    Modified Rankin Scale (mRS)

    Measures degree of disability or dependence in daily activities
    after a stroke or neurological disability.

    Scale:
    - 0: No symptoms at all
    - 1: No significant disability despite symptoms
    - 2: Slight disability; unable to carry out all previous activities
    - 3: Moderate disability; requires some help, able to walk
    - 4: Moderately severe disability; unable to walk/attend to needs
    - 5: Severe disability; bedridden, requires constant care
    - 6: Dead

    Favorable outcome typically defined as mRS 0-2.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="modified_rankin_scale",
                name="Modified Rankin Scale (mRS)",
                purpose="Assess disability and dependence after stroke",
                input_params=["mrs_score"],
                output_type="mRS grade (0-6) with functional status classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.NEUROLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.GERIATRICS,
                ),
                conditions=(
                    "Stroke",
                    "Ischemic Stroke",
                    "Hemorrhagic Stroke",
                    "TIA",
                    "Cerebrovascular Disease",
                    "Disability",
                    "Neurological Deficit",
                ),
                clinical_contexts=(
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.MONITORING,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "What is the mRS score?",
                    "What is the patient's functional status?",
                    "Is this a favorable outcome?",
                    "What is the disability level after stroke?",
                    "Can the patient live independently?",
                ),
                icd10_codes=(
                    "I63",  # Cerebral infarction
                    "I61",  # Intracerebral hemorrhage
                    "I64",  # Stroke, not specified
                    "G81",  # Hemiplegia
                ),
                keywords=(
                    "mRS",
                    "Rankin",
                    "modified Rankin scale",
                    "disability",
                    "stroke outcome",
                    "functional status",
                    "dependence",
                    "favorable outcome",
                    "handicap",
                ),
            ),
            references=(
                Reference(
                    citation="van Swieten JC, Koudstaal PJ, Visser MC, Schouten HJ, van Gijn J. "
                    "Interobserver agreement for the assessment of handicap in stroke patients. "
                    "Stroke. 1988;19(5):604-607.",
                    doi="10.1161/01.str.19.5.604",
                    pmid="3363593",
                    year=1988,
                ),
                Reference(
                    citation="Rankin J. Cerebral vascular accidents in patients over the age of 60. II. Prognosis. Scott Med J. 1957;2(5):200-215.",
                    pmid="13432835",
                    year=1957,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(self, mrs_score: Literal[0, 1, 2, 3, 4, 5, 6]) -> ScoreResult:
        """
        Record Modified Rankin Scale assessment.

        Args:
            mrs_score: Modified Rankin Scale grade
                - 0: No symptoms at all
                - 1: No significant disability; able to carry out all usual duties
                - 2: Slight disability; unable to carry out all previous activities,
                     but able to look after own affairs without assistance
                - 3: Moderate disability; requires some help, able to walk without assistance
                - 4: Moderately severe disability; unable to walk without assistance,
                     unable to attend to own bodily needs without assistance
                - 5: Severe disability; bedridden, incontinent, requires constant nursing care
                - 6: Dead

        Returns:
            ScoreResult with mRS grade and functional status interpretation
        """
        # Get interpretation based on score
        interpretation = self._get_interpretation(mrs_score)

        # Determine if favorable outcome
        favorable_outcome = mrs_score <= 2
        independent = mrs_score <= 2
        ambulatory = mrs_score <= 3

        return ScoreResult(
            value=float(mrs_score),
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={"mrs_score": mrs_score},
            calculation_details={
                "mrs_grade": mrs_score,
                "favorable_outcome": favorable_outcome,
                "independent": independent,
                "ambulatory": ambulatory,
                "category": self._get_category(mrs_score),
            },
            notes=self._get_notes(mrs_score),
        )

    def _get_category(self, score: int) -> str:
        """Get category name for mRS score"""
        categories = {
            0: "No symptoms",
            1: "No significant disability",
            2: "Slight disability",
            3: "Moderate disability",
            4: "Moderately severe disability",
            5: "Severe disability",
            6: "Dead",
        }
        return categories.get(score, "Unknown")

    def _get_interpretation(self, score: int) -> Interpretation:
        """Get clinical interpretation based on score"""

        if score == 0:
            return Interpretation(
                summary="mRS 0: No Symptoms",
                detail="No symptoms at all. Complete recovery.",
                severity=Severity.NORMAL,
                risk_level=RiskLevel.LOW,
                stage="Excellent Outcome",
                stage_description="mRS 0",
                recommendations=(
                    "Continue secondary stroke prevention",
                    "Risk factor modification",
                    "Regular follow-up",
                ),
                next_steps=(
                    "Maintain healthy lifestyle",
                    "Medication adherence for secondary prevention",
                ),
            )
        elif score == 1:
            return Interpretation(
                summary="mRS 1: No Significant Disability",
                detail="No significant disability despite symptoms. Able to carry out all usual duties and activities.",
                severity=Severity.NORMAL,
                risk_level=RiskLevel.LOW,
                stage="Favorable Outcome",
                stage_description="mRS 1 - Functional Independence",
                recommendations=(
                    "Continue secondary stroke prevention",
                    "Address any residual symptoms",
                    "May return to most activities including work",
                ),
                next_steps=(
                    "Outpatient neurology follow-up",
                    "Consider driving assessment if relevant",
                ),
            )
        elif score == 2:
            return Interpretation(
                summary="mRS 2: Slight Disability",
                detail="Slight disability. Unable to carry out all previous activities, but able to look after own affairs without assistance.",
                severity=Severity.MILD,
                risk_level=RiskLevel.LOW,
                stage="Favorable Outcome",
                stage_description="mRS 2 - Independent",
                recommendations=(
                    "Continue rehabilitation as needed",
                    "Occupational therapy for activity adaptation",
                    "Secondary stroke prevention",
                    "Assess for mood disorders",
                ),
                next_steps=(
                    "Outpatient rehabilitation",
                    "Support for lifestyle modifications",
                ),
            )
        elif score == 3:
            return Interpretation(
                summary="mRS 3: Moderate Disability",
                detail="Moderate disability. Requires some help but able to walk without assistance.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.INTERMEDIATE,
                stage="Moderate Outcome",
                stage_description="mRS 3 - Requires Assistance",
                recommendations=(
                    "Continued rehabilitation (PT, OT, Speech)",
                    "Home care assistance may be needed",
                    "Caregiver support and education",
                    "Falls risk assessment",
                    "Depression and anxiety screening",
                ),
                warnings=(
                    "At risk for caregiver burnout",
                    "Monitor for complications (DVT, pressure ulcers)",
                ),
                next_steps=(
                    "Inpatient rehabilitation or day program",
                    "Home safety assessment",
                    "Social work consultation",
                ),
            )
        elif score == 4:
            return Interpretation(
                summary="mRS 4: Moderately Severe Disability",
                detail="Moderately severe disability. Unable to walk without assistance and unable to attend to own bodily needs without assistance.",
                severity=Severity.MODERATE,
                risk_level=RiskLevel.HIGH,
                stage="Poor Outcome",
                stage_description="mRS 4 - Dependent",
                recommendations=(
                    "Inpatient rehabilitation or skilled nursing facility",
                    "24-hour supervision required",
                    "Physical therapy for mobility",
                    "Bowel and bladder management",
                    "Nutrition assessment (swallow evaluation)",
                    "Pressure ulcer prevention",
                ),
                warnings=(
                    "High risk for complications",
                    "Caregiver burden significant",
                    "Consider goals of care discussion",
                ),
                next_steps=(
                    "Rehabilitation placement",
                    "Family meeting for care planning",
                    "Consider long-term care options",
                ),
            )
        elif score == 5:
            return Interpretation(
                summary="mRS 5: Severe Disability",
                detail="Severe disability. Bedridden, incontinent, and requires constant nursing care and attention.",
                severity=Severity.SEVERE,
                risk_level=RiskLevel.VERY_HIGH,
                stage="Very Poor Outcome",
                stage_description="mRS 5 - Total Dependence",
                recommendations=(
                    "Skilled nursing facility or hospice care",
                    "Total care for all ADLs",
                    "Pressure ulcer prevention and skin care",
                    "Nutrition support (may need tube feeding)",
                    "Comfort measures",
                    "Goals of care/code status discussion",
                ),
                warnings=(
                    "High mortality risk",
                    "High complication rate",
                    "Consider palliative care consultation",
                ),
                next_steps=(
                    "Family meeting for goals of care",
                    "Consider advance directives",
                    "Palliative care involvement",
                ),
            )
        else:  # score == 6
            return Interpretation(
                summary="mRS 6: Dead",
                detail="Patient has died.",
                severity=Severity.CRITICAL,
                risk_level=None,
                stage="Death",
                stage_description="mRS 6",
                recommendations=(),
                next_steps=(),
            )

    def _get_notes(self, score: int) -> list[str]:
        """Get clinical notes"""
        notes = [
            "mRS is the most widely used outcome measure in stroke trials",
            "Favorable outcome typically defined as mRS 0-2",
        ]

        if score <= 2:
            notes.append("Patient achieved favorable functional outcome (mRS 0-2)")
        elif score == 3:
            notes.append("Ambulatory but not independent - often a gray zone in treatment trials")
        elif score >= 4:
            notes.append("Dependent for basic needs - consider rehabilitation potential and goals of care")

        if score >= 3:
            notes.append("Consider structured mRS assessment (rankin focused assessment) for consistency")

        return notes
