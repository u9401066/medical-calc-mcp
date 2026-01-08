"""
MADRS (Montgomery-Åsberg Depression Rating Scale)

The MADRS is a clinician-administered rating scale for assessing
depression severity. Particularly sensitive to change with treatment.

Reference (Original):
    Montgomery SA, Asberg M. A new depression scale designed to be
    sensitive to change. Br J Psychiatry. 1979;134:382-389.
    PMID: 444788

Reference (Scoring guidelines):
    Snaith RP, Harrop FM, Newby DA, Teale C. Grade scores of the
    Montgomery-Asberg Depression and the Clinical Anxiety Scales.
    Br J Psychiatry. 1986;148:599-601.
    PMID: 3779233
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


class MADRSCalculator(BaseCalculator):
    """
    MADRS (Montgomery-Åsberg Depression Rating Scale) Calculator

    Clinician-administered 10-item scale for depression severity.
    Particularly sensitive to treatment changes.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="madrs",
                name="MADRS (Montgomery-Åsberg Depression Rating Scale)",
                purpose="Assess depression severity with focus on treatment response",
                input_params=[
                    "apparent_sadness",
                    "reported_sadness",
                    "inner_tension",
                    "reduced_sleep",
                    "reduced_appetite",
                    "concentration_difficulties",
                    "lassitude",
                    "inability_to_feel",
                    "pessimistic_thoughts",
                    "suicidal_thoughts",
                ],
                output_type="Score 0-60 with depression severity",
            ),
            high_level=HighLevelKey(
                specialties=(Specialty.PSYCHIATRY,),
                conditions=(
                    "Depression",
                    "Major Depressive Disorder",
                    "MDD",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.MONITORING,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "How severe is the depression?",
                    "Is the patient responding to treatment?",
                    "MADRS score",
                ),
                keywords=("MADRS", "Montgomery Asberg", "depression severity"),
            ),
            references=(
                Reference(
                    citation="Montgomery SA, Asberg M. A new depression scale designed to be sensitive to change. Br J Psychiatry. 1979;134:382-389.",
                    pmid="444788",
                    doi="10.1192/bjp.134.4.382",
                    year=1979,
                ),
                Reference(
                    citation="Snaith RP, Harrop FM, Newby DA, Teale C. Grade scores of the Montgomery-Asberg Depression and the Clinical Anxiety Scales. Br J Psychiatry. 1986;148:599-601.",
                    pmid="3779233",
                    year=1986,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        apparent_sadness: int,
        reported_sadness: int,
        inner_tension: int,
        reduced_sleep: int,
        reduced_appetite: int,
        concentration_difficulties: int,
        lassitude: int,
        inability_to_feel: int,
        pessimistic_thoughts: int,
        suicidal_thoughts: int,
    ) -> ScoreResult:
        """
        Calculate MADRS score.

        All items scored 0-6 (anchors at even numbers, odd for intermediate):
        0 = No abnormality
        2 = Mild
        4 = Moderate
        6 = Severe

        Args:
            apparent_sadness: Visible despondency in expression, posture (0-6)
            reported_sadness: Subjective reports of depressed mood (0-6)
            inner_tension: Feelings of discomfort, tension, panic (0-6)
            reduced_sleep: Reduced duration or depth of sleep (0-6)
            reduced_appetite: Loss of appetite (0-6)
            concentration_difficulties: Difficulties collecting thoughts (0-6)
            lassitude: Difficulty getting started, slowness (0-6)
            inability_to_feel: Reduced interest, anhedonia (0-6)
            pessimistic_thoughts: Guilt, inferiority, self-reproach (0-6)
            suicidal_thoughts: Feeling life not worth living (0-6)

        Returns:
            ScoreResult with MADRS score and interpretation
        """
        items = {
            "apparent_sadness": apparent_sadness,
            "reported_sadness": reported_sadness,
            "inner_tension": inner_tension,
            "reduced_sleep": reduced_sleep,
            "reduced_appetite": reduced_appetite,
            "concentration_difficulties": concentration_difficulties,
            "lassitude": lassitude,
            "inability_to_feel": inability_to_feel,
            "pessimistic_thoughts": pessimistic_thoughts,
            "suicidal_thoughts": suicidal_thoughts,
        }

        # Validate inputs
        for name, value in items.items():
            if not isinstance(value, int) or value < 0 or value > 6:
                raise ValueError(f"{name} must be an integer between 0 and 6")

        total_score = sum(items.values())
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
                "max_score": 60,
                "in_remission": total_score <= 10,
                "suicidal_ideation_level": suicidal_thoughts,
            },
        )

    def _get_interpretation(self, score: int, suicidal_thoughts: int) -> Interpretation:
        """Generate interpretation based on MADRS score"""

        warnings: tuple[str, ...] = ()
        if suicidal_thoughts >= 4:
            warnings = ("⚠️ SIGNIFICANT SUICIDAL IDEATION - Immediate safety assessment required",)

        if score <= 6:
            return Interpretation(
                summary=f"MADRS {score}/60: Normal/symptom absent",
                detail="Score 0-6 indicates absence of depression symptoms.",
                severity=Severity.NORMAL,
                stage="Normal",
                stage_description="MADRS 0-6: Normal",
                recommendations=("No treatment indicated",),
                warnings=warnings,
                next_steps=("Continue monitoring",),
            )
        elif score <= 19:
            return Interpretation(
                summary=f"MADRS {score}/60: Mild depression",
                detail="Score 7-19 indicates mild depression.",
                severity=Severity.MILD,
                stage="Mild",
                stage_description="MADRS 7-19: Mild depression",
                recommendations=("Consider psychotherapy", "Monitor symptoms"),
                warnings=warnings,
                next_steps=("Reassess in 2-4 weeks",),
            )
        elif score <= 34:
            return Interpretation(
                summary=f"MADRS {score}/60: Moderate depression",
                detail="Score 20-34 indicates moderate depression.",
                severity=Severity.MODERATE,
                stage="Moderate",
                stage_description="MADRS 20-34: Moderate depression",
                recommendations=("Treatment indicated", "Consider combination therapy"),
                warnings=warnings,
                next_steps=("Initiate treatment", "Close monitoring"),
            )
        else:  # score >= 35
            return Interpretation(
                summary=f"MADRS {score}/60: Severe depression",
                detail="Score ≥35 indicates severe depression.",
                severity=Severity.SEVERE,
                stage="Severe",
                stage_description="MADRS ≥35: Severe depression",
                recommendations=(
                    "Intensive treatment required",
                    "Consider hospitalization",
                ),
                warnings=warnings + ("Severe depression - close monitoring essential",),
                next_steps=("Intensive treatment", "Safety assessment"),
            )
