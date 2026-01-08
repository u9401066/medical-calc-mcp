"""
HAM-D (Hamilton Depression Rating Scale)

The HAM-D (Hamilton Depression Rating Scale), also known as HDRS or HRSD,
is a clinician-administered 17-item scale for assessing depression severity.

Reference (Original):
    Hamilton M. A rating scale for depression. J Neurol Neurosurg Psychiatry.
    1960;23:56-62.
    PMID: 14399272

Reference (Scoring Guidelines):
    Zimmerman M, Martinez JH, Young D, et al. Severity classification on the
    Hamilton Depression Rating Scale. J Affect Disord. 2013;150(2):384-388.
    PMID: 23759278
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


class HAMDCalculator(BaseCalculator):
    """
    HAM-D17 (Hamilton Depression Rating Scale, 17-item) Calculator

    Clinician-administered scale for depression severity.
    Commonly used as primary outcome in clinical trials.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="hamd",
                name="HAM-D17 (Hamilton Depression Rating Scale)",
                purpose="Assess depression severity (clinician-rated)",
                input_params=[
                    "depressed_mood",
                    "guilt",
                    "suicide",
                    "insomnia_early",
                    "insomnia_middle",
                    "insomnia_late",
                    "work_activities",
                    "retardation",
                    "agitation",
                    "anxiety_psychic",
                    "anxiety_somatic",
                    "somatic_gi",
                    "somatic_general",
                    "genital",
                    "hypochondriasis",
                    "weight_loss",
                    "insight",
                ],
                output_type="Score 0-52 with depression severity",
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
                    "HAM-D score",
                    "Hamilton depression scale",
                    "Is the patient in remission?",
                ),
                keywords=("HAM-D", "HDRS", "Hamilton depression", "depression severity"),
            ),
            references=(
                Reference(
                    citation="Hamilton M. A rating scale for depression. J Neurol Neurosurg Psychiatry. 1960;23:56-62.",
                    pmid="14399272",
                    year=1960,
                ),
                Reference(
                    citation="Zimmerman M, Martinez JH, Young D, et al. Severity classification on the Hamilton Depression Rating Scale. J Affect Disord. 2013;150(2):384-388.",
                    pmid="23759278",
                    year=2013,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        depressed_mood: int,
        guilt: int,
        suicide: int,
        insomnia_early: int,
        insomnia_middle: int,
        insomnia_late: int,
        work_activities: int,
        retardation: int,
        agitation: int,
        anxiety_psychic: int,
        anxiety_somatic: int,
        somatic_gi: int,
        somatic_general: int,
        genital: int,
        hypochondriasis: int,
        weight_loss: int,
        insight: int,
    ) -> ScoreResult:
        """
        Calculate HAM-D17 score.

        Scoring varies by item:
        - Items 1,2,3,7,8: 0-4
        - Items 4,5,6,9-17: 0-2

        Args:
            depressed_mood: Depressed mood (0-4)
            guilt: Feelings of guilt (0-4)
            suicide: Suicide (0-4)
            insomnia_early: Insomnia early (0-2)
            insomnia_middle: Insomnia middle (0-2)
            insomnia_late: Insomnia late (0-2)
            work_activities: Work and activities (0-4)
            retardation: Retardation (0-4)
            agitation: Agitation (0-2)
            anxiety_psychic: Anxiety - psychic (0-4)
            anxiety_somatic: Anxiety - somatic (0-4)
            somatic_gi: Somatic symptoms - GI (0-2)
            somatic_general: Somatic symptoms - general (0-2)
            genital: Genital symptoms (0-2)
            hypochondriasis: Hypochondriasis (0-4)
            weight_loss: Loss of weight (0-2)
            insight: Insight (0-2)

        Returns:
            ScoreResult with HAM-D score and interpretation
        """
        # Define max scores for each item
        items_0_4 = {
            "depressed_mood": depressed_mood,
            "guilt": guilt,
            "suicide": suicide,
            "work_activities": work_activities,
            "retardation": retardation,
            "anxiety_psychic": anxiety_psychic,
            "anxiety_somatic": anxiety_somatic,
            "hypochondriasis": hypochondriasis,
        }
        items_0_2 = {
            "insomnia_early": insomnia_early,
            "insomnia_middle": insomnia_middle,
            "insomnia_late": insomnia_late,
            "agitation": agitation,
            "somatic_gi": somatic_gi,
            "somatic_general": somatic_general,
            "genital": genital,
            "weight_loss": weight_loss,
            "insight": insight,
        }

        # Validate inputs
        for name, value in items_0_4.items():
            if not isinstance(value, int) or value < 0 or value > 4:
                raise ValueError(f"{name} must be an integer between 0 and 4")
        for name, value in items_0_2.items():
            if not isinstance(value, int) or value < 0 or value > 2:
                raise ValueError(f"{name} must be an integer between 0 and 2")

        all_items = {**items_0_4, **items_0_2}
        total_score = sum(all_items.values())

        interpretation = self._get_interpretation(total_score, suicide)

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs=all_items,
            calculation_details={
                "total_score": total_score,
                "max_score": 52,
                "in_remission": total_score <= 7,
                "suicide_item": suicide,
            },
        )

    def _get_interpretation(self, score: int, suicide: int) -> Interpretation:
        """Generate interpretation based on HAM-D score"""

        warnings: tuple[str, ...] = ()
        if suicide >= 3:
            warnings = ("⚠️ SIGNIFICANT SUICIDAL IDEATION - Immediate safety assessment required",)

        if score <= 7:
            return Interpretation(
                summary=f"HAM-D {score}/52: Remission",
                detail="Score ≤7 indicates remission. Treatment target achieved.",
                severity=Severity.NORMAL,
                stage="Remission",
                stage_description="HAM-D ≤7: Remission",
                recommendations=(
                    "Remission achieved",
                    "Continue maintenance therapy",
                    "Monitor for relapse",
                ),
                warnings=warnings,
                next_steps=("Continue current treatment", "Reassess periodically"),
            )
        elif score <= 17:
            return Interpretation(
                summary=f"HAM-D {score}/52: Mild depression",
                detail="Score 8-17 indicates mild depression.",
                severity=Severity.MILD,
                stage="Mild",
                stage_description="HAM-D 8-17: Mild depression",
                recommendations=(
                    "Treatment response partial",
                    "Consider optimization",
                ),
                warnings=warnings,
                next_steps=("Optimize treatment", "Reassess in 2-4 weeks"),
            )
        elif score <= 24:
            return Interpretation(
                summary=f"HAM-D {score}/52: Moderate depression",
                detail="Score 18-24 indicates moderate depression.",
                severity=Severity.MODERATE,
                stage="Moderate",
                stage_description="HAM-D 18-24: Moderate depression",
                recommendations=(
                    "Active treatment required",
                    "Consider treatment adjustment",
                ),
                warnings=warnings,
                next_steps=("Adjust treatment", "Close monitoring"),
            )
        else:  # score >= 25
            return Interpretation(
                summary=f"HAM-D {score}/52: Severe depression",
                detail="Score ≥25 indicates severe depression.",
                severity=Severity.SEVERE,
                stage="Severe",
                stage_description="HAM-D ≥25: Severe depression",
                recommendations=(
                    "Intensive treatment required",
                    "Consider hospitalization if indicated",
                ),
                warnings=warnings + ("Severe depression - assess safety",),
                next_steps=("Intensive monitoring", "Consider hospitalization"),
            )
