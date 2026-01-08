"""
Karnofsky Performance Scale (KPS)

The Karnofsky Performance Scale is a standard measure of functional status
in oncology patients. It ranges from 0 (dead) to 100 (normal, no complaints).

Reference (Original):
    Karnofsky DA, Burchenal JH. The Clinical Evaluation of Chemotherapeutic
    Agents in Cancer. In: MacLeod CM, ed. Evaluation of Chemotherapeutic
    Agents. New York, NY: Columbia University Press; 1949:191-205.

Reference (Validation):
    Mor V, Laliberte L, Morris JN, Wiemann M. The Karnofsky Performance
    Status Scale. An examination of its reliability and validity in a
    research setting. Cancer. 1984;53(9):2002-2007.
    PMID: 6704925

Note:
    KPS maps approximately to ECOG Performance Status:
    - KPS 100 = ECOG 0
    - KPS 80-90 = ECOG 1
    - KPS 60-70 = ECOG 2
    - KPS 40-50 = ECOG 3
    - KPS 10-30 = ECOG 4
    - KPS 0 = ECOG 5 (Dead)
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class KarnofskyPerformanceScaleCalculator(BaseCalculator):
    """
    Karnofsky Performance Scale (KPS) Calculator

    Scale from 0-100 in increments of 10:
    - 100: Normal, no complaints, no evidence of disease
    - 90: Able to carry on normal activity; minor signs/symptoms of disease
    - 80: Normal activity with effort; some signs/symptoms of disease
    - 70: Cares for self; unable to carry on normal activity or active work
    - 60: Requires occasional assistance, but able to care for most needs
    - 50: Requires considerable assistance and frequent medical care
    - 40: Disabled; requires special care and assistance
    - 30: Severely disabled; hospitalization indicated, death not imminent
    - 20: Very sick; hospitalization necessary; active supportive treatment
    - 10: Moribund; fatal processes progressing rapidly
    - 0: Dead
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="karnofsky_performance_scale",
                name="Karnofsky Performance Scale (KPS)",
                purpose="Quantify functional status and prognosis in cancer and other diseases",
                input_params=["kps_score"],
                output_type="Score (0-100%) with functional description",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.ONCOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.GERIATRICS,
                    Specialty.NEUROLOGY,
                ),
                conditions=(
                    "Cancer",
                    "Malignancy",
                    "Advanced Disease",
                    "Brain Tumor",
                    "Chronic Illness",
                    "Hospice Eligibility",
                ),
                clinical_contexts=(
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.SCREENING,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "What is this patient's Karnofsky score?",
                    "Is this patient eligible for hospice?",
                    "Can this patient tolerate treatment?",
                    "What is the patient's functional status?",
                ),
                icd10_codes=("Z89.9", "C80.1"),
                keywords=(
                    "Karnofsky",
                    "KPS",
                    "performance status",
                    "functional status",
                    "oncology",
                    "hospice eligibility",
                    "prognosis",
                ),
            ),
            references=(
                Reference(
                    citation="Karnofsky DA, Burchenal JH. The Clinical Evaluation of "
                    "Chemotherapeutic Agents in Cancer. In: MacLeod CM, ed. "
                    "Evaluation of Chemotherapeutic Agents. Columbia University Press; "
                    "1949:191-205.",
                    year=1949,
                ),
                Reference(
                    citation="Mor V, Laliberte L, Morris JN, Wiemann M. The Karnofsky "
                    "Performance Status Scale: An examination of its reliability and "
                    "validity in a research setting. Cancer. 1984;53(9):2002-2007.",
                    pmid="6704925",
                    year=1984,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        kps_score: int,
    ) -> ScoreResult:
        """
        Calculate Karnofsky Performance Scale assessment.

        Args:
            kps_score: KPS score (0-100, increments of 10)

        Returns:
            ScoreResult with KPS interpretation
        """
        # Validate score
        if kps_score < 0 or kps_score > 100:
            raise ValueError("KPS must be between 0 and 100")
        if kps_score % 10 != 0:
            raise ValueError("KPS must be in increments of 10 (0, 10, 20, ... 100)")

        # Score descriptions
        descriptions = {
            100: "Normal, no complaints, no evidence of disease",
            90: "Able to carry on normal activity; minor signs/symptoms of disease",
            80: "Normal activity with effort; some signs/symptoms of disease",
            70: "Cares for self; unable to carry on normal activity or active work",
            60: "Requires occasional assistance, but able to care for most needs",
            50: "Requires considerable assistance and frequent medical care",
            40: "Disabled; requires special care and assistance",
            30: "Severely disabled; hospitalization indicated, death not imminent",
            20: "Very sick; hospitalization necessary; active supportive treatment needed",
            10: "Moribund; fatal processes progressing rapidly",
            0: "Dead",
        }

        # Categories
        categories = {
            100: "Able to carry on normal activity",
            90: "Able to carry on normal activity",
            80: "Able to carry on normal activity",
            70: "Unable to work; able to live at home, care for most personal needs",
            60: "Unable to work; able to live at home, care for most personal needs",
            50: "Unable to work; able to live at home, care for most personal needs",
            40: "Unable to care for self; requires institutional or hospital care",
            30: "Unable to care for self; requires institutional or hospital care",
            20: "Unable to care for self; requires institutional or hospital care",
            10: "Unable to care for self; requires institutional or hospital care",
            0: "Dead",
        }

        # ECOG equivalent
        ecog_mapping = {
            100: 0,
            90: 1,
            80: 1,
            70: 2,
            60: 2,
            50: 3,
            40: 3,
            30: 4,
            20: 4,
            10: 4,
            0: 5,
        }

        # Get interpretation
        interpretation = self._get_interpretation(kps_score, descriptions[kps_score], categories[kps_score], ecog_mapping[kps_score])

        return ScoreResult(
            value=kps_score,
            unit=Unit.PERCENT,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={"kps_score": kps_score},
            calculation_details={
                "kps_score": kps_score,
                "description": descriptions[kps_score],
                "category": categories[kps_score],
                "ecog_equivalent": ecog_mapping[kps_score],
                "all_descriptions": descriptions,
            },
            formula_used="KPS score assigned based on functional status assessment",
        )

    def _get_interpretation(self, score: int, description: str, category: str, ecog: int) -> Interpretation:
        """Get interpretation based on KPS score"""

        if score >= 80:
            return Interpretation(
                summary=f"KPS {score}%: {description}",
                detail=f"Category: {category}. Equivalent to ECOG {ecog}. Patient can generally tolerate standard treatment intensity.",
                severity=Severity.NORMAL if score == 100 else Severity.MILD,
                stage=f"KPS {score}",
                stage_description=category,
                recommendations=(
                    "Patient suitable for standard treatment",
                    "No restrictions based on performance status",
                    "Continue routine monitoring",
                ),
                next_steps=(
                    "Proceed with planned treatment",
                    "Document performance status",
                ),
            )
        elif score >= 60:
            return Interpretation(
                summary=f"KPS {score}%: {description}",
                detail=f"Category: {category}. Equivalent to ECOG {ecog}. Patient may tolerate treatment but with modifications.",
                severity=Severity.MODERATE,
                stage=f"KPS {score}",
                stage_description=category,
                recommendations=(
                    "Consider treatment modifications based on functional status",
                    "Balance treatment efficacy with quality of life",
                    "Evaluate supportive care needs",
                    "Consider palliative care consultation",
                ),
                warnings=(
                    "Higher risk of treatment-related complications",
                    "May not tolerate aggressive treatment regimens",
                ),
                next_steps=(
                    "Discuss treatment goals with patient/family",
                    "Consider less intensive treatment options",
                    "Ensure adequate supportive care",
                ),
            )
        elif score >= 40:
            return Interpretation(
                summary=f"KPS {score}%: {description}",
                detail=f"Category: {category}. Equivalent to ECOG {ecog}. Limited treatment options; focus on comfort and palliation.",
                severity=Severity.SEVERE,
                stage=f"KPS {score}",
                stage_description=category,
                recommendations=(
                    "Focus on comfort-oriented care",
                    "Palliative care consultation recommended",
                    "KPS <50% often meets hospice eligibility criteria",
                    "Discuss goals of care and advance directives",
                    "Minimize aggressive interventions",
                ),
                warnings=(
                    "Poor prognosis with KPS <50%",
                    "Aggressive treatment generally not recommended",
                    "High risk of treatment-related mortality",
                ),
                next_steps=(
                    "Goals of care discussion",
                    "Hospice evaluation if appropriate",
                    "Focus on symptom management",
                ),
            )
        elif score >= 10:
            return Interpretation(
                summary=f"KPS {score}%: {description}",
                detail=f"Category: {category}. Equivalent to ECOG {ecog}. Very poor prognosis; focus on comfort measures.",
                severity=Severity.CRITICAL,
                stage=f"KPS {score}",
                stage_description=category,
                recommendations=(
                    "Comfort measures only recommended",
                    "Hospice care strongly indicated",
                    "Family support and counseling",
                    "Ensure advance directives in place",
                    "Do not attempt aggressive treatments",
                ),
                warnings=(
                    "KPS ≤30% associated with very limited survival",
                    "Any treatment intervention may hasten death",
                ),
                next_steps=(
                    "Immediate hospice referral",
                    "Focus on comfort and dignity",
                    "Family meeting and support",
                ),
            )
        else:  # score == 0
            return Interpretation(
                summary="KPS 0%: Dead",
                detail="Patient has died.",
                severity=Severity.CRITICAL,
                stage="KPS 0",
                stage_description="Dead",
                recommendations=(),
                next_steps=(),
            )
