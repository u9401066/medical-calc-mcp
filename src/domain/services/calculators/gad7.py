"""
GAD-7 (Generalized Anxiety Disorder 7-item scale)

The GAD-7 is a 7-item self-administered screening tool for generalized
anxiety disorder. It scores anxiety symptoms on a 0-3 scale.

Reference (Original Development):
    Spitzer RL, Kroenke K, Williams JB, Löwe B. A brief measure for assessing
    generalized anxiety disorder: the GAD-7. Arch Intern Med. 2006;166(10):1092-1097.
    PMID: 16717171

Reference (Validation):
    Löwe B, Decker O, Müller S, et al. Validation and standardization of the
    Generalized Anxiety Disorder Screener (GAD-7) in the general population.
    Med Care. 2008;46(3):266-274.
    PMID: 18388841
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


class GAD7Calculator(BaseCalculator):
    """
    GAD-7 (Generalized Anxiety Disorder 7-item scale) Calculator

    7-item self-report questionnaire for anxiety screening and severity.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="gad7",
                name="GAD-7 (Generalized Anxiety Disorder 7-item)",
                purpose="Screen for anxiety and assess severity",
                input_params=[
                    "feeling_nervous",
                    "cant_stop_worrying",
                    "worrying_too_much",
                    "trouble_relaxing",
                    "restless",
                    "easily_annoyed",
                    "feeling_afraid",
                ],
                output_type="Score 0-21 with anxiety severity",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.PSYCHIATRY,
                    Specialty.FAMILY_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Generalized Anxiety Disorder",
                    "GAD",
                    "Anxiety",
                    "Panic Disorder",
                ),
                clinical_contexts=(
                    ClinicalContext.SCREENING,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "Is this patient anxious?",
                    "How severe is the anxiety?",
                    "Screen for anxiety",
                    "GAD-7 score",
                ),
                keywords=("GAD-7", "anxiety screening", "generalized anxiety disorder"),
            ),
            references=(
                Reference(
                    citation="Spitzer RL, Kroenke K, Williams JB, Löwe B. A brief measure for assessing generalized anxiety disorder: the GAD-7. Arch Intern Med. 2006;166(10):1092-1097.",
                    pmid="16717171",
                    doi="10.1001/archinte.166.10.1092",
                    year=2006,
                ),
                Reference(
                    citation="Löwe B, Decker O, Müller S, et al. Validation and standardization of the Generalized Anxiety Disorder Screener (GAD-7) in the general population. Med Care. 2008;46(3):266-274.",
                    pmid="18388841",
                    doi="10.1097/MLR.0b013e318160d093",
                    year=2008,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        feeling_nervous: int,
        cant_stop_worrying: int,
        worrying_too_much: int,
        trouble_relaxing: int,
        restless: int,
        easily_annoyed: int,
        feeling_afraid: int,
    ) -> ScoreResult:
        """
        Calculate GAD-7 anxiety score.

        All items scored 0-3:
        0 = Not at all
        1 = Several days
        2 = More than half the days
        3 = Nearly every day

        Args:
            feeling_nervous: Feeling nervous, anxious, or on edge
            cant_stop_worrying: Not being able to stop or control worrying
            worrying_too_much: Worrying too much about different things
            trouble_relaxing: Trouble relaxing
            restless: Being so restless that it's hard to sit still
            easily_annoyed: Becoming easily annoyed or irritable
            feeling_afraid: Feeling afraid as if something awful might happen

        Returns:
            ScoreResult with GAD-7 score and anxiety severity
        """
        items = {
            "feeling_nervous": feeling_nervous,
            "cant_stop_worrying": cant_stop_worrying,
            "worrying_too_much": worrying_too_much,
            "trouble_relaxing": trouble_relaxing,
            "restless": restless,
            "easily_annoyed": easily_annoyed,
            "feeling_afraid": feeling_afraid,
        }

        # Validate inputs
        for name, value in items.items():
            if not isinstance(value, int) or value < 0 or value > 3:
                raise ValueError(f"{name} must be an integer between 0 and 3")

        total_score = sum(items.values())
        interpretation = self._get_interpretation(total_score)

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
                "max_score": 21,
                "screen_positive": total_score >= 10,
            },
        )

    def _get_interpretation(self, score: int) -> Interpretation:
        """Generate interpretation based on GAD-7 score"""

        if score <= 4:
            return Interpretation(
                summary=f"GAD-7 {score}/21: Minimal anxiety",
                detail="Score 0-4 indicates minimal anxiety symptoms.",
                severity=Severity.NORMAL,
                stage="Minimal",
                stage_description="GAD-7 0-4: Minimal anxiety",
                recommendations=("No specific treatment indicated", "Continue routine screening"),
                next_steps=("Reassess if symptoms develop",),
            )
        elif score <= 9:
            return Interpretation(
                summary=f"GAD-7 {score}/21: Mild anxiety",
                detail="Score 5-9 indicates mild anxiety.",
                severity=Severity.MILD,
                stage="Mild",
                stage_description="GAD-7 5-9: Mild anxiety",
                recommendations=(
                    "Watchful waiting",
                    "Consider supportive counseling",
                    "Relaxation techniques may help",
                ),
                next_steps=("Reassess in 2-4 weeks",),
            )
        elif score <= 14:
            return Interpretation(
                summary=f"GAD-7 {score}/21: Moderate anxiety",
                detail="Score 10-14 indicates moderate anxiety. Treatment should be considered.",
                severity=Severity.MODERATE,
                stage="Moderate",
                stage_description="GAD-7 10-14: Moderate anxiety",
                recommendations=(
                    "Treatment warranted",
                    "Consider psychotherapy (CBT)",
                    "Consider pharmacotherapy if appropriate",
                ),
                next_steps=(
                    "Further diagnostic evaluation",
                    "Discuss treatment options",
                ),
            )
        else:  # score >= 15
            return Interpretation(
                summary=f"GAD-7 {score}/21: Severe anxiety",
                detail="Score 15-21 indicates severe anxiety. Active treatment is recommended.",
                severity=Severity.SEVERE,
                stage="Severe",
                stage_description="GAD-7 15-21: Severe anxiety",
                recommendations=(
                    "Active treatment recommended",
                    "Consider combined therapy (CBT + medication)",
                    "Psychiatric consultation may be warranted",
                ),
                warnings=("Severe anxiety - assess functional impairment",),
                next_steps=(
                    "Initiate treatment",
                    "Consider psychiatric referral",
                ),
            )
