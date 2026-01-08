"""
4AT - Rapid Assessment Test for Delirium

The 4AT is a rapid, practical, and validated screening tool for delirium
designed for use in hospital settings by any healthcare professional without
special training. It takes less than 2 minutes to administer.

Reference (Original):
    Bellelli G, Morandi A, Davis DH, et al. Validation of the 4AT, a new
    instrument for rapid delirium screening: a study in 234 hospitalised
    older people. Age Ageing. 2014;43(4):496-502.
    DOI: 10.1093/ageing/afu021
    PMID: 24590568

Reference (Meta-analysis):
    Tieges Z, Maclullich AMJ, Anand A, et al. Diagnostic accuracy of the
    4AT for delirium detection in older adults: systematic review and
    meta-analysis. Age Ageing. 2021;50(3):733-743.
    DOI: 10.1093/ageing/afaa224
    PMID: 33951145
"""

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class FourATCalculator(BaseCalculator):
    """
    4AT Rapid Delirium Assessment Calculator

    Four components:
    1. Alertness (observed, no testing needed): 0-4 points
    2. AMT4 (Abbreviated Mental Test): 0-2 points
    3. Attention (Months backwards): 0-2 points
    4. Acute change or fluctuation: 0-4 points

    Score interpretation:
    - 0: Delirium or severe cognitive impairment unlikely
    - 1-3: Possible cognitive impairment
    - ≥4: Possible delirium ± cognitive impairment
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="four_at",
                name="4AT (Rapid Assessment Test for Delirium)",
                purpose="Rapid delirium screening in hospital settings",
                input_params=["alertness", "amt4_score", "attention_score", "acute_change_fluctuation"],
                output_type="Score (0-12) with delirium probability",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.GERIATRICS,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.EMERGENCY_MEDICINE,
                    Specialty.SURGERY,
                    Specialty.NEUROLOGY,
                ),
                conditions=(
                    "Delirium",
                    "Acute Confusional State",
                    "Altered Mental Status",
                    "Cognitive Impairment",
                    "Dementia",
                    "Encephalopathy",
                ),
                clinical_contexts=(
                    ClinicalContext.DELIRIUM_ASSESSMENT,
                    ClinicalContext.SCREENING,
                    ClinicalContext.EMERGENCY,
                    ClinicalContext.PREOPERATIVE_ASSESSMENT,
                ),
                clinical_questions=(
                    "Does this patient have delirium?",
                    "How do I quickly screen for delirium?",
                    "Is this confusion new or chronic?",
                    "Should I do further delirium workup?",
                ),
                icd10_codes=("F05", "R41.0", "R41.82"),
                keywords=(
                    "4AT",
                    "delirium",
                    "confusion",
                    "screening",
                    "rapid assessment",
                    "altered mental status",
                    "cognitive impairment",
                    "elderly",
                    "geriatric",
                ),
            ),
            references=(
                Reference(
                    citation="Bellelli G, Morandi A, Davis DH, et al. Validation of the 4AT, "
                    "a new instrument for rapid delirium screening: a study in 234 "
                    "hospitalised older people. Age Ageing. 2014;43(4):496-502.",
                    doi="10.1093/ageing/afu021",
                    pmid="24590568",
                    year=2014,
                ),
                Reference(
                    citation="Tieges Z, Maclullich AMJ, Anand A, et al. Diagnostic accuracy of "
                    "the 4AT for delirium detection in older adults: systematic review "
                    "and meta-analysis. Age Ageing. 2021;50(3):733-743.",
                    doi="10.1093/ageing/afaa224",
                    pmid="33951145",
                    year=2021,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        alertness: int,
        amt4_errors: int,
        attention_score: int,
        acute_change_fluctuation: bool,
    ) -> ScoreResult:
        """
        Calculate 4AT score.

        Args:
            alertness: Item 1 - Alertness (0 = normal, 4 = abnormal/drowsy/agitated)
                - 0: Normal (fully alert, not agitated through assessment)
                - 4: Clearly abnormal AND/OR abnormal - drowsy (eyes closing)
                     or agitated/hyperactive
            amt4_errors: Item 2 - AMT4 errors (0-4)
                AMT4 questions: Age, Date of birth, Place, Current year
                - 0: No errors = score 0
                - 1-2 errors = score 1
                - 3-4 errors or untestable = score 2
            attention_score: Item 3 - Attention (months backwards from December)
                - 0: Achieves 7 months or more correctly
                - 1: Starts but scores <7 months, or refuses to start
                - 2: Untestable (cannot start because unwell, drowsy, inattentive)
            acute_change_fluctuation: Item 4 - Acute change or fluctuating course
                Evidence of significant change or fluctuation in alertness, cognition,
                or other mental function (e.g., paranoia, hallucinations)
                - False (0): No acute change
                - True (4): Acute change present

        Returns:
            ScoreResult with 4AT score and interpretation
        """
        # Validate inputs
        if alertness not in (0, 4):
            raise ValueError("Alertness must be 0 (normal) or 4 (abnormal)")
        if not 0 <= amt4_errors <= 4:
            raise ValueError("AMT4 errors must be between 0 and 4")
        if attention_score not in (0, 1, 2):
            raise ValueError("Attention score must be 0, 1, or 2")

        # Convert AMT4 errors to score
        if amt4_errors == 0:
            amt4_score = 0
        elif amt4_errors <= 2:
            amt4_score = 1
        else:
            amt4_score = 2

        # Item 4 score
        acute_score = 4 if acute_change_fluctuation else 0

        # Total score
        total_score = alertness + amt4_score + attention_score + acute_score

        # Determine category
        if total_score >= 4:
            category = "Possible Delirium"
        elif total_score >= 1:
            category = "Possible Cognitive Impairment"
        else:
            category = "Unlikely Delirium"

        # Get interpretation
        interpretation = self._get_interpretation(total_score, category, alertness, amt4_score, attention_score, acute_score)

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "alertness": alertness,
                "amt4_errors": amt4_errors,
                "attention_score": attention_score,
                "acute_change_fluctuation": acute_change_fluctuation,
            },
            calculation_details={
                "items": {
                    "1_alertness": {"score": alertness, "description": "Normal (0)" if alertness == 0 else "Abnormal (4)"},
                    "2_amt4": {"score": amt4_score, "errors": amt4_errors, "description": f"{amt4_errors} errors"},
                    "3_attention": {"score": attention_score, "description": ["≥7 months correct", "<7 months or refused", "Untestable"][attention_score]},
                    "4_acute_change": {"score": acute_score, "present": acute_change_fluctuation, "description": "Yes" if acute_change_fluctuation else "No"},
                },
                "total_score": total_score,
                "max_score": 12,
                "category": category,
            },
            formula_used="4AT = Alertness (0/4) + AMT4 (0-2) + Attention (0-2) + Acute change (0/4)",
        )

    def _get_interpretation(self, score: int, category: str, alertness: int, amt4: int, attention: int, acute: int) -> Interpretation:
        """Get interpretation based on 4AT score"""

        component_text = f"Alertness={alertness}, AMT4={amt4}, Attention={attention}, Acute={acute}"

        if score >= 4:
            return Interpretation(
                summary=f"4AT Score {score}: Possible Delirium",
                detail=f"Score ≥4 suggests possible delirium ± underlying cognitive impairment. "
                f"Components: {component_text}. "
                f"Sensitivity 88%, Specificity 88% for delirium detection.",
                severity=Severity.MODERATE,
                stage="Possible Delirium",
                stage_description="Score ≥4: Possible delirium",
                recommendations=(
                    "Urgent: Investigate for underlying cause of delirium",
                    "Common causes to consider:",
                    "- Infection (UTI, pneumonia, sepsis)",
                    "- Medications (sedatives, anticholinergics, opioids)",
                    "- Metabolic disturbance (electrolytes, glucose, renal/hepatic)",
                    "- Urinary retention/fecal impaction",
                    "- Pain",
                    "- Hypoxia",
                    "- Alcohol/substance withdrawal",
                    "Review medication list for deliriogenic drugs",
                    "Non-pharmacological management first",
                    "Consider specialist referral (geriatrics, neurology)",
                ),
                warnings=(
                    "Delirium is a medical emergency requiring investigation",
                    "May mask underlying serious illness",
                    "Associated with increased mortality and morbidity",
                    "4AT does not distinguish delirium from dementia",
                ),
                next_steps=(
                    "Full delirium workup",
                    "Blood tests (FBC, U&E, LFT, glucose, CRP)",
                    "Urinalysis",
                    "Chest X-ray if indicated",
                    "Consider CT head if focal neurology or head injury",
                    "Implement delirium prevention/management strategies",
                ),
            )
        elif score >= 1:
            return Interpretation(
                summary=f"4AT Score {score}: Possible Cognitive Impairment",
                detail=f"Score 1-3 suggests possible cognitive impairment but does not "
                f"indicate delirium. Components: {component_text}. "
                f"May indicate underlying dementia or other cognitive disorder.",
                severity=Severity.MILD,
                stage="Cognitive Impairment",
                stage_description="Score 1-3: Possible cognitive impairment",
                recommendations=(
                    "Further cognitive assessment may be warranted",
                    "Consider baseline cognitive status (known dementia?)",
                    "Rule out delirium superimposed on dementia",
                    "If acute change noted by family/carers, treat as possible delirium",
                    "Consider MMSE or MOCA for detailed cognitive assessment",
                ),
                warnings=(
                    "Does not exclude delirium, especially if any acute change",
                    "Pre-existing dementia increases delirium risk",
                ),
                next_steps=(
                    "Clarify baseline cognitive status",
                    "Monitor for changes suggesting delirium",
                    "Consider referral for cognitive assessment if new finding",
                ),
            )
        else:
            return Interpretation(
                summary="4AT Score 0: Delirium Unlikely",
                detail=f"Score 0 suggests delirium or severe cognitive impairment unlikely. Components: {component_text}. High negative predictive value.",
                severity=Severity.NORMAL,
                stage="Unlikely",
                stage_description="Score 0: Delirium unlikely",
                recommendations=(
                    "Delirium unlikely at present",
                    "Continue to monitor for any acute changes",
                    "Rescreen if clinical concern develops",
                    "Does not exclude mild cognitive impairment",
                ),
                next_steps=(
                    "Routine care",
                    "Rescreen if mental status changes",
                ),
            )
