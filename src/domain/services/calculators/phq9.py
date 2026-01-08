"""
PHQ-9 (Patient Health Questionnaire-9)

The PHQ-9 is a 9-item self-administered screening tool for depression.
It scores each of the 9 DSM-IV criteria for major depressive disorder
on a 0-3 scale, with total scores ranging from 0 to 27.

Reference (Original Development):
    Kroenke K, Spitzer RL, Williams JB. The PHQ-9: validity of a brief
    depression severity measure. J Gen Intern Med. 2001;16(9):606-613.
    PMID: 11556941

Reference (Validation):
    Gilbody S, Richards D, Brealey S, Hewitt C. Screening for depression
    in medical settings with the Patient Health Questionnaire (PHQ): a
    diagnostic meta-analysis. J Gen Intern Med. 2007;22(11):1596-1602.
    PMID: 17874169
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


class PHQ9Calculator(BaseCalculator):
    """
    PHQ-9 (Patient Health Questionnaire-9) Calculator

    9-item self-report questionnaire for depression screening and severity.
    Item 9 specifically assesses suicidal ideation.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="phq9",
                name="PHQ-9 (Patient Health Questionnaire-9)",
                purpose="Screen for depression and assess severity",
                input_params=[
                    "interest_pleasure",
                    "feeling_down",
                    "sleep_problems",
                    "fatigue",
                    "appetite_changes",
                    "feeling_bad",
                    "concentration",
                    "psychomotor",
                    "suicidal_thoughts",
                ],
                output_type="Score 0-27 with depression severity",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.PSYCHIATRY,
                    Specialty.FAMILY_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.GERIATRICS,
                ),
                conditions=(
                    "Depression",
                    "Major Depressive Disorder",
                    "MDD",
                    "Depressive Episode",
                ),
                clinical_contexts=(
                    ClinicalContext.SCREENING,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.MONITORING,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "Is this patient depressed?",
                    "How severe is the depression?",
                    "Screen for depression",
                    "PHQ-9 score",
                ),
                keywords=(
                    "PHQ-9",
                    "depression screening",
                    "depression severity",
                    "patient health questionnaire",
                ),
            ),
            references=(
                Reference(
                    citation="Kroenke K, Spitzer RL, Williams JB. The PHQ-9: validity of a brief depression severity measure. J Gen Intern Med. 2001;16(9):606-613.",
                    pmid="11556941",
                    doi="10.1046/j.1525-1497.2001.016009606.x",
                    year=2001,
                ),
                Reference(
                    citation="Gilbody S, Richards D, Brealey S, Hewitt C. Screening for depression in medical settings with the Patient Health Questionnaire (PHQ): a diagnostic meta-analysis. J Gen Intern Med. 2007;22(11):1596-1602.",
                    pmid="17874169",
                    doi="10.1007/s11606-007-0333-y",
                    year=2007,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        interest_pleasure: int,
        feeling_down: int,
        sleep_problems: int,
        fatigue: int,
        appetite_changes: int,
        feeling_bad: int,
        concentration: int,
        psychomotor: int,
        suicidal_thoughts: int,
    ) -> ScoreResult:
        """
        Calculate PHQ-9 depression score.

        All items scored 0-3:
        0 = Not at all
        1 = Several days
        2 = More than half the days
        3 = Nearly every day

        Args:
            interest_pleasure: Little interest or pleasure in doing things
            feeling_down: Feeling down, depressed, or hopeless
            sleep_problems: Trouble falling/staying asleep, or sleeping too much
            fatigue: Feeling tired or having little energy
            appetite_changes: Poor appetite or overeating
            feeling_bad: Feeling bad about yourself - failure, let down family
            concentration: Trouble concentrating on things
            psychomotor: Moving/speaking slowly, or fidgety/restless
            suicidal_thoughts: Thoughts of being better off dead or self-harm (ITEM 9)

        Returns:
            ScoreResult with PHQ-9 score and depression severity
        """
        items = {
            "interest_pleasure": interest_pleasure,
            "feeling_down": feeling_down,
            "sleep_problems": sleep_problems,
            "fatigue": fatigue,
            "appetite_changes": appetite_changes,
            "feeling_bad": feeling_bad,
            "concentration": concentration,
            "psychomotor": psychomotor,
            "suicidal_thoughts": suicidal_thoughts,
        }

        # Validate inputs
        for name, value in items.items():
            if not isinstance(value, int) or value < 0 or value > 3:
                raise ValueError(f"{name} must be an integer between 0 and 3")

        # Calculate total score (max = 27)
        total_score = sum(items.values())

        # Get interpretation
        interpretation = self._get_interpretation(total_score, suicidal_thoughts)

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs=items,
            calculation_details={
                "total_score": total_score,
                "max_score": 27,
                "item_scores": items,
                "suicidal_ideation_level": suicidal_thoughts,
                "cardinal_symptoms": interest_pleasure + feeling_down,
            },
        )

    def _get_interpretation(self, score: int, suicidal_thoughts: int) -> Interpretation:
        """Generate interpretation based on PHQ-9 score"""

        # Warning for suicidal ideation
        warnings: tuple[str, ...] = ()
        if suicidal_thoughts >= 1:
            warnings = (
                "⚠️ SUICIDAL IDEATION PRESENT - Requires immediate safety assessment",
                "Ask about specific plans, means, and intent",
                "Consider psychiatric consultation or referral",
            )

        if score <= 4:
            return Interpretation(
                summary=f"PHQ-9 {score}/27: Minimal depression",
                detail="Score 0-4 indicates minimal or no depression symptoms.",
                severity=Severity.NORMAL,
                stage="Minimal",
                stage_description="PHQ-9 0-4: Minimal depression",
                recommendations=(
                    "No specific treatment indicated",
                    "Continue routine screening",
                ),
                warnings=warnings,
                next_steps=("Reassess if symptoms develop",),
            )
        elif score <= 9:
            return Interpretation(
                summary=f"PHQ-9 {score}/27: Mild depression",
                detail="Score 5-9 indicates mild depression. Watchful waiting and supportive counseling may be appropriate.",
                severity=Severity.MILD,
                stage="Mild",
                stage_description="PHQ-9 5-9: Mild depression",
                recommendations=(
                    "Watchful waiting with follow-up",
                    "Consider supportive counseling",
                    "Lifestyle modifications (exercise, sleep hygiene)",
                ),
                warnings=warnings,
                next_steps=(
                    "Schedule follow-up in 2-4 weeks",
                    "Reassess PHQ-9",
                ),
            )
        elif score <= 14:
            return Interpretation(
                summary=f"PHQ-9 {score}/27: Moderate depression",
                detail="Score 10-14 indicates moderate depression. Treatment with psychotherapy and/or pharmacotherapy should be considered.",
                severity=Severity.MODERATE,
                stage="Moderate",
                stage_description="PHQ-9 10-14: Moderate depression",
                recommendations=(
                    "Treatment warranted",
                    "Consider antidepressant medication",
                    "Consider psychotherapy (CBT, IPT)",
                ),
                warnings=warnings,
                next_steps=(
                    "Initiate treatment discussion",
                    "Schedule follow-up in 2 weeks",
                ),
            )
        elif score <= 19:
            return Interpretation(
                summary=f"PHQ-9 {score}/27: Moderately severe depression",
                detail="Score 15-19 indicates moderately severe depression. Active treatment with medication and/or psychotherapy is recommended.",
                severity=Severity.SEVERE,
                stage="Moderately Severe",
                stage_description="PHQ-9 15-19: Moderately severe depression",
                recommendations=(
                    "Active treatment strongly recommended",
                    "Antidepressant medication indicated",
                    "Psychotherapy (CBT, IPT) recommended",
                ),
                warnings=warnings,
                next_steps=(
                    "Initiate pharmacotherapy and/or psychotherapy",
                    "Consider psychiatric referral",
                ),
            )
        else:  # score >= 20
            return Interpretation(
                summary=f"PHQ-9 {score}/27: Severe depression",
                detail="Score 20-27 indicates severe depression. Immediate treatment initiation and psychiatric consultation is recommended.",
                severity=Severity.CRITICAL,
                stage="Severe",
                stage_description="PHQ-9 20-27: Severe depression",
                recommendations=(
                    "Immediate treatment initiation required",
                    "Psychiatric consultation recommended",
                    "Assess need for hospitalization",
                ),
                warnings=warnings
                + (
                    "High severity - close monitoring essential",
                    "Assess functional impairment and safety",
                ),
                next_steps=(
                    "Psychiatric referral recommended",
                    "Initiate treatment immediately",
                    "Safety planning",
                ),
            )
