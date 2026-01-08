"""
HAM-A (Hamilton Anxiety Rating Scale)

The HAM-A is a clinician-administered 14-item scale for assessing
anxiety severity.

Reference (Original):
    Hamilton M. The assessment of anxiety states by rating.
    Br J Med Psychol. 1959;32(1):50-55.
    PMID: 13638508

Reference (Psychometric Properties):
    Maier W, Buller R, Philipp M, Heuser I. The Hamilton Anxiety Scale:
    reliability, validity and sensitivity to change in anxiety and
    depressive disorders. J Affect Disord. 1988;14(1):61-68.
    PMID: 2963053
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


class HAMACalculator(BaseCalculator):
    """
    HAM-A (Hamilton Anxiety Rating Scale) Calculator

    Clinician-administered 14-item scale for anxiety severity.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="hama",
                name="HAM-A (Hamilton Anxiety Rating Scale)",
                purpose="Assess anxiety severity (clinician-rated)",
                input_params=[
                    "anxious_mood",
                    "tension",
                    "fears",
                    "insomnia",
                    "intellectual",
                    "depressed_mood",
                    "somatic_muscular",
                    "somatic_sensory",
                    "cardiovascular",
                    "respiratory",
                    "gastrointestinal",
                    "genitourinary",
                    "autonomic",
                    "behavior_interview",
                ],
                output_type="Score 0-56 with anxiety severity",
            ),
            high_level=HighLevelKey(
                specialties=(Specialty.PSYCHIATRY,),
                conditions=(
                    "Anxiety",
                    "Generalized Anxiety Disorder",
                    "GAD",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "How severe is the anxiety?",
                    "HAM-A score",
                    "Hamilton anxiety scale",
                ),
                keywords=("HAM-A", "Hamilton anxiety", "anxiety severity"),
            ),
            references=(
                Reference(
                    citation="Hamilton M. The assessment of anxiety states by rating. Br J Med Psychol. 1959;32(1):50-55.",
                    pmid="13638508",
                    year=1959,
                ),
                Reference(
                    citation="Maier W, Buller R, Philipp M, Heuser I. The Hamilton Anxiety Scale: reliability, validity and sensitivity to change in anxiety and depressive disorders. J Affect Disord. 1988;14(1):61-68.",
                    pmid="2963053",
                    year=1988,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        anxious_mood: int,
        tension: int,
        fears: int,
        insomnia: int,
        intellectual: int,
        depressed_mood: int,
        somatic_muscular: int,
        somatic_sensory: int,
        cardiovascular: int,
        respiratory: int,
        gastrointestinal: int,
        genitourinary: int,
        autonomic: int,
        behavior_interview: int,
    ) -> ScoreResult:
        """
        Calculate HAM-A score.

        All items scored 0-4:
        0 = Not present
        1 = Mild
        2 = Moderate
        3 = Severe
        4 = Very severe

        Args:
            anxious_mood: Worries, anticipation of worst (0-4)
            tension: Feelings of tension, fatigability (0-4)
            fears: Fear of dark, strangers, being alone, animals, traffic (0-4)
            insomnia: Difficulty in falling asleep, broken sleep (0-4)
            intellectual: Difficulty concentrating, poor memory (0-4)
            depressed_mood: Loss of interest, lack of pleasure (0-4)
            somatic_muscular: Aches, twitching, stiffness (0-4)
            somatic_sensory: Tinnitus, blurring of vision (0-4)
            cardiovascular: Tachycardia, palpitations, chest pain (0-4)
            respiratory: Pressure on chest, choking feelings (0-4)
            gastrointestinal: Swallowing difficulties, nausea (0-4)
            genitourinary: Frequency, urgency, amenorrhea (0-4)
            autonomic: Dry mouth, flushing, sweating (0-4)
            behavior_interview: Fidgeting, restlessness, tremor (0-4)

        Returns:
            ScoreResult with HAM-A score and interpretation
        """
        items = {
            "anxious_mood": anxious_mood,
            "tension": tension,
            "fears": fears,
            "insomnia": insomnia,
            "intellectual": intellectual,
            "depressed_mood": depressed_mood,
            "somatic_muscular": somatic_muscular,
            "somatic_sensory": somatic_sensory,
            "cardiovascular": cardiovascular,
            "respiratory": respiratory,
            "gastrointestinal": gastrointestinal,
            "genitourinary": genitourinary,
            "autonomic": autonomic,
            "behavior_interview": behavior_interview,
        }

        # Validate inputs
        for name, value in items.items():
            if not isinstance(value, int) or value < 0 or value > 4:
                raise ValueError(f"{name} must be an integer between 0 and 4")

        total_score = sum(items.values())

        # Subscores: Psychic (1-6) and Somatic (7-14)
        psychic = anxious_mood + tension + fears + insomnia + intellectual + depressed_mood
        somatic = somatic_muscular + somatic_sensory + cardiovascular + respiratory + gastrointestinal + genitourinary + autonomic + behavior_interview

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
                "max_score": 56,
                "psychic_subscore": psychic,
                "somatic_subscore": somatic,
            },
        )

    def _get_interpretation(self, score: int) -> Interpretation:
        """Generate interpretation based on HAM-A score"""

        if score < 17:
            return Interpretation(
                summary=f"HAM-A {score}/56: Mild anxiety",
                detail="Score <17 indicates mild anxiety.",
                severity=Severity.MILD,
                stage="Mild",
                stage_description="HAM-A <17: Mild anxiety",
                recommendations=("Continue monitoring", "Treatment may not be necessary"),
                next_steps=("Reassess if symptoms worsen",),
            )
        elif score < 25:
            return Interpretation(
                summary=f"HAM-A {score}/56: Mild to moderate anxiety",
                detail="Score 17-24 indicates mild to moderate anxiety.",
                severity=Severity.MODERATE,
                stage="Mild-Moderate",
                stage_description="HAM-A 17-24: Mild-moderate anxiety",
                recommendations=("Treatment may be beneficial",),
                next_steps=("Consider treatment options",),
            )
        elif score < 30:
            return Interpretation(
                summary=f"HAM-A {score}/56: Moderate to severe anxiety",
                detail="Score 25-29 indicates moderate to severe anxiety.",
                severity=Severity.MODERATE,
                stage="Moderate-Severe",
                stage_description="HAM-A 25-29: Moderate-severe anxiety",
                recommendations=("Active treatment recommended",),
                next_steps=("Initiate treatment",),
            )
        else:  # score >= 30
            return Interpretation(
                summary=f"HAM-A {score}/56: Severe anxiety",
                detail="Score ≥30 indicates severe anxiety.",
                severity=Severity.SEVERE,
                stage="Severe",
                stage_description="HAM-A ≥30: Severe anxiety",
                recommendations=("Intensive treatment required",),
                warnings=("Severe anxiety - close monitoring needed",),
                next_steps=("Intensive treatment", "Consider referral"),
            )
