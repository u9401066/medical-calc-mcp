"""
ECOG Performance Status

The Eastern Cooperative Oncology Group (ECOG) Performance Status is a scale
used to assess how a patient's disease is progressing, how the disease affects
daily living abilities, and to determine appropriate treatment and prognosis.

Reference (Original):
    Oken MM, Creech RH, Tormey DC, et al. Toxicity and response criteria
    of the Eastern Cooperative Oncology Group.
    Am J Clin Oncol. 1982;5(6):649-655.
    PMID: 7165009

Note:
    The ECOG scale maps approximately to the Karnofsky Performance Scale:
    - ECOG 0 = KPS 100
    - ECOG 1 = KPS 80-90
    - ECOG 2 = KPS 60-70
    - ECOG 3 = KPS 40-50
    - ECOG 4 = KPS 10-30
    - ECOG 5 = KPS 0 (Dead)
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class ECOGPerformanceStatusCalculator(BaseCalculator):
    """
    ECOG Performance Status Calculator

    Grade 0: Fully active, able to carry on all pre-disease performance
             without restriction
    Grade 1: Restricted in physically strenuous activity but ambulatory and
             able to carry out work of a light or sedentary nature
    Grade 2: Ambulatory and capable of all selfcare but unable to carry out
             any work activities. Up and about more than 50% of waking hours
    Grade 3: Capable of only limited selfcare, confined to bed or chair
             more than 50% of waking hours
    Grade 4: Completely disabled. Cannot carry on any selfcare. Totally
             confined to bed or chair
    Grade 5: Dead
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="ecog_performance_status",
                name="ECOG Performance Status",
                purpose="Assess functional status and prognosis in cancer patients",
                input_params=["ecog_grade"],
                output_type="Grade (0-5) with functional description",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.ONCOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.GERIATRICS,
                ),
                conditions=(
                    "Cancer",
                    "Malignancy",
                    "Oncologic Disease",
                    "Advanced Cancer",
                    "Metastatic Disease",
                ),
                clinical_contexts=(
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.SCREENING,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "What is this patient's performance status?",
                    "Is this patient fit for chemotherapy?",
                    "Can this patient tolerate aggressive treatment?",
                    "What is the functional status for clinical trial eligibility?",
                    "How do I document performance status?",
                ),
                icd10_codes=("Z89.9", "C80.1"),
                keywords=(
                    "ECOG",
                    "performance status",
                    "PS",
                    "functional status",
                    "oncology",
                    "cancer",
                    "chemotherapy eligibility",
                    "WHO performance status",
                    "Zubrod scale",
                ),
            ),
            references=(
                Reference(
                    citation="Oken MM, Creech RH, Tormey DC, et al. Toxicity and response "
                    "criteria of the Eastern Cooperative Oncology Group. "
                    "Am J Clin Oncol. 1982;5(6):649-655.",
                    pmid="7165009",
                    year=1982,
                ),
                Reference(
                    citation="Simcock R, Wright J. Beyond Performance Status. Clin Oncol (R Coll Radiol). 2020;32(9):553-561.",
                    doi="10.1016/j.clon.2020.06.016",
                    pmid="32684503",
                    year=2020,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        fully_active: bool = False,
        restricted_strenuous: bool = False,
        ambulatory_no_work: bool = False,
        limited_selfcare: bool = False,
        completely_disabled: bool = False,
        ecog_grade: int | None = None,
    ) -> ScoreResult:
        """
        Calculate ECOG Performance Status.

        Can be called two ways:
        1. With individual boolean descriptors (system determines grade)
        2. With explicit ecog_grade (0-5)

        Args:
            fully_active: Grade 0 - Fully active, no restrictions
            restricted_strenuous: Grade 1 - Restricted in strenuous activity only
            ambulatory_no_work: Grade 2 - Ambulatory, selfcare, but unable to work
            limited_selfcare: Grade 3 - Limited selfcare, >50% of time in bed/chair
            completely_disabled: Grade 4 - Completely disabled, no selfcare
            ecog_grade: Direct grade input (0-5), overrides boolean inputs

        Returns:
            ScoreResult with ECOG grade and interpretation
        """
        # Determine grade
        if ecog_grade is not None:
            if not 0 <= ecog_grade <= 5:
                raise ValueError("ECOG grade must be between 0 and 5")
            grade = ecog_grade
        else:
            # Determine from boolean inputs (highest applicable grade)
            if completely_disabled:
                grade = 4
            elif limited_selfcare:
                grade = 3
            elif ambulatory_no_work:
                grade = 2
            elif restricted_strenuous:
                grade = 1
            elif fully_active:
                grade = 0
            else:
                raise ValueError("Either ecog_grade or at least one boolean descriptor must be provided")

        # Grade descriptions
        descriptions = {
            0: "Fully active, able to carry on all pre-disease performance without restriction",
            1: "Restricted in physically strenuous activity but ambulatory and able to carry out work of a light or sedentary nature",
            2: "Ambulatory and capable of all selfcare but unable to carry out any work activities; up and about more than 50% of waking hours",
            3: "Capable of only limited selfcare, confined to bed or chair more than 50% of waking hours",
            4: "Completely disabled; cannot carry on any selfcare; totally confined to bed or chair",
            5: "Dead",
        }

        # Karnofsky equivalents
        kps_equivalents = {
            0: "100%",
            1: "80-90%",
            2: "60-70%",
            3: "40-50%",
            4: "10-30%",
            5: "0%",
        }

        # Get interpretation
        interpretation = self._get_interpretation(grade, descriptions[grade], kps_equivalents[grade])

        return ScoreResult(
            value=grade,
            unit=Unit.GRADE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "ecog_grade": ecog_grade,
                "fully_active": fully_active,
                "restricted_strenuous": restricted_strenuous,
                "ambulatory_no_work": ambulatory_no_work,
                "limited_selfcare": limited_selfcare,
                "completely_disabled": completely_disabled,
            },
            calculation_details={
                "grade": grade,
                "description": descriptions[grade],
                "karnofsky_equivalent": kps_equivalents[grade],
                "grade_definitions": descriptions,
            },
            formula_used="ECOG PS grade assigned based on functional status description",
        )

    def _get_interpretation(self, grade: int, description: str, kps_equivalent: str) -> Interpretation:
        """Get interpretation based on ECOG grade"""

        if grade == 0:
            return Interpretation(
                summary="ECOG PS 0: Fully Active",
                detail=f"{description}. Equivalent to Karnofsky {kps_equivalent}. Patient can tolerate any treatment intensity.",
                severity=Severity.NORMAL,
                stage="Grade 0",
                stage_description="Fully active",
                recommendations=(
                    "Patient suitable for any treatment intensity",
                    "Eligible for most clinical trials",
                    "No restrictions on treatment choice based on PS",
                ),
                next_steps=(
                    "Proceed with standard treatment planning",
                    "Document PS for clinical records",
                ),
            )
        elif grade == 1:
            return Interpretation(
                summary="ECOG PS 1: Restricted in Strenuous Activity",
                detail=f"{description}. Equivalent to Karnofsky {kps_equivalent}. Good candidate for most cancer treatments.",
                severity=Severity.MILD,
                stage="Grade 1",
                stage_description="Restricted in strenuous activity only",
                recommendations=(
                    "Generally suitable for standard-dose chemotherapy",
                    "Eligible for most clinical trials",
                    "Consider patient preferences and treatment goals",
                    "Monitor for deterioration during treatment",
                ),
                next_steps=(
                    "Proceed with planned treatment",
                    "Regular PS reassessment during therapy",
                ),
            )
        elif grade == 2:
            return Interpretation(
                summary="ECOG PS 2: Ambulatory, Unable to Work",
                detail=f"{description}. Equivalent to Karnofsky {kps_equivalent}. May benefit from treatment but with increased toxicity risk.",
                severity=Severity.MODERATE,
                stage="Grade 2",
                stage_description="Ambulatory, selfcare capable, unable to work",
                recommendations=(
                    "Carefully consider risk-benefit of aggressive treatment",
                    "May need dose modifications or less intensive regimens",
                    "Some clinical trials may exclude PS 2",
                    "Consider palliative care consultation",
                    "Discuss treatment goals and preferences",
                ),
                warnings=(
                    "Higher risk of treatment-related toxicity",
                    "Reduced benefit from aggressive chemotherapy in some cancers",
                    "Quality of life considerations important",
                ),
                next_steps=(
                    "Multidisciplinary discussion of treatment options",
                    "Consider less toxic alternatives if available",
                    "Ensure adequate supportive care",
                ),
            )
        elif grade == 3:
            return Interpretation(
                summary="ECOG PS 3: Limited Selfcare, >50% in Bed/Chair",
                detail=f"{description}. Equivalent to Karnofsky {kps_equivalent}. Limited treatment options; focus on symptom control.",
                severity=Severity.SEVERE,
                stage="Grade 3",
                stage_description="Limited selfcare, confined >50% of time",
                recommendations=(
                    "Aggressive chemotherapy generally not recommended",
                    "Consider targeted therapy or immunotherapy if tolerable",
                    "Focus on symptom management and quality of life",
                    "Palliative care should be integrated",
                    "Hospice referral may be appropriate",
                ),
                warnings=(
                    "High risk of treatment-related mortality with aggressive therapy",
                    "Most clinical trials exclude PS 3",
                    "Goals of care discussion essential",
                ),
                next_steps=(
                    "Goals of care conversation",
                    "Palliative care consultation",
                    "Optimize symptom management",
                    "Consider less toxic treatment options",
                ),
            )
        elif grade == 4:
            return Interpretation(
                summary="ECOG PS 4: Completely Disabled",
                detail=f"{description}. Equivalent to Karnofsky {kps_equivalent}. Active anticancer treatment generally contraindicated.",
                severity=Severity.CRITICAL,
                stage="Grade 4",
                stage_description="Completely disabled, bedridden",
                recommendations=(
                    "Focus entirely on comfort and symptom control",
                    "Anticancer treatment generally not appropriate",
                    "Hospice care strongly recommended",
                    "Family support and counseling",
                    "Ensure advance directives are in place",
                ),
                warnings=(
                    "Any systemic treatment likely to cause harm",
                    "Life expectancy limited",
                    "Prognosis is poor regardless of cancer type",
                ),
                next_steps=(
                    "Hospice referral",
                    "Comfort measures only",
                    "Family meeting and support",
                ),
            )
        else:  # grade == 5
            return Interpretation(
                summary="ECOG PS 5: Dead",
                detail="Patient has died.",
                severity=Severity.CRITICAL,
                stage="Grade 5",
                stage_description="Dead",
                recommendations=(),
                next_steps=(),
            )
