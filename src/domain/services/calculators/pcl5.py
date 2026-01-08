"""
PCL-5 (PTSD Checklist for DSM-5)

The PCL-5 is a 20-item self-report measure for DSM-5 PTSD symptoms.

Reference (Development):
    Blevins CA, Weathers FW, Davis MT, Witte TK, Domino JL. The
    Posttraumatic Stress Disorder Checklist for DSM-5 (PCL-5):
    Development and Initial Psychometric Evaluation. J Trauma Stress.
    2015;28(6):489-498.
    PMID: 26606250

Reference (Validation):
    Bovin MJ, Marx BP, Weathers FW, et al. Psychometric properties of
    the PTSD Checklist for Diagnostic and Statistical Manual of Mental
    Disorders-Fifth Edition (PCL-5) in veterans. Psychol Assess.
    2016;28(11):1379-1391.
    PMID: 26653052
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


class PCL5Calculator(BaseCalculator):
    """
    PCL-5 (PTSD Checklist for DSM-5) Calculator

    Self-report measure of DSM-5 PTSD symptoms (20 items).
    Screening cutoff: 31-33 (varies by setting).
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="pcl5",
                name="PCL-5 (PTSD Checklist for DSM-5)",
                purpose="Self-report screening and monitoring for PTSD",
                input_params=[
                    "item1_intrusive_memories",
                    "item2_distressing_dreams",
                    "item3_flashbacks",
                    "item4_upset_reminders",
                    "item5_physical_reactions",
                    "item6_avoid_thoughts",
                    "item7_avoid_external",
                    "item8_trouble_remembering",
                    "item9_negative_beliefs",
                    "item10_blame",
                    "item11_negative_feelings",
                    "item12_loss_interest",
                    "item13_feeling_distant",
                    "item14_trouble_positive",
                    "item15_irritability",
                    "item16_risk_taking",
                    "item17_hypervigilance",
                    "item18_easily_startled",
                    "item19_concentration",
                    "item20_sleep_trouble",
                ],
                output_type="PCL-5 score 0-80 with screening status",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.PSYCHIATRY,
                    Specialty.FAMILY_MEDICINE,
                ),
                conditions=(
                    "PTSD",
                    "Post-Traumatic Stress Disorder",
                    "Trauma",
                ),
                clinical_contexts=(
                    ClinicalContext.SCREENING,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "Screen for PTSD",
                    "PTSD severity",
                    "PCL-5 score",
                ),
                keywords=("PCL-5", "PTSD screening", "PTSD checklist"),
            ),
            references=(
                Reference(
                    citation="Blevins CA, Weathers FW, Davis MT, Witte TK, Domino JL. The Posttraumatic Stress Disorder Checklist for DSM-5 (PCL-5): Development and Initial Psychometric Evaluation. J Trauma Stress. 2015;28(6):489-498.",
                    pmid="26606250",
                    doi="10.1002/jts.22059",
                    year=2015,
                ),
                Reference(
                    citation="Bovin MJ, Marx BP, Weathers FW, et al. Psychometric properties of the PTSD Checklist for Diagnostic and Statistical Manual of Mental Disorders-Fifth Edition (PCL-5) in veterans. Psychol Assess. 2016;28(11):1379-1391.",
                    pmid="26653052",
                    doi="10.1037/pas0000254",
                    year=2016,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        item1_intrusive_memories: int,
        item2_distressing_dreams: int,
        item3_flashbacks: int,
        item4_upset_reminders: int,
        item5_physical_reactions: int,
        item6_avoid_thoughts: int,
        item7_avoid_external: int,
        item8_trouble_remembering: int,
        item9_negative_beliefs: int,
        item10_blame: int,
        item11_negative_feelings: int,
        item12_loss_interest: int,
        item13_feeling_distant: int,
        item14_trouble_positive: int,
        item15_irritability: int,
        item16_risk_taking: int,
        item17_hypervigilance: int,
        item18_easily_startled: int,
        item19_concentration: int,
        item20_sleep_trouble: int,
        screening_cutoff: int = 31,
    ) -> ScoreResult:
        """
        Calculate PCL-5 score.

        All items rated 0-4:
        0 = Not at all
        1 = A little bit
        2 = Moderately
        3 = Quite a bit
        4 = Extremely

        Args:
            All items: Individual symptom severity (0-4)
            screening_cutoff: Cutoff for positive screen (default 31)

        Returns:
            ScoreResult with PCL-5 score and screening status
        """
        cluster_b = [
            item1_intrusive_memories,
            item2_distressing_dreams,
            item3_flashbacks,
            item4_upset_reminders,
            item5_physical_reactions,
        ]
        cluster_c = [item6_avoid_thoughts, item7_avoid_external]
        cluster_d = [
            item8_trouble_remembering,
            item9_negative_beliefs,
            item10_blame,
            item11_negative_feelings,
            item12_loss_interest,
            item13_feeling_distant,
            item14_trouble_positive,
        ]
        cluster_e = [
            item15_irritability,
            item16_risk_taking,
            item17_hypervigilance,
            item18_easily_startled,
            item19_concentration,
            item20_sleep_trouble,
        ]

        all_items = cluster_b + cluster_c + cluster_d + cluster_e

        # Validate
        for idx, val in enumerate(all_items):
            if not isinstance(val, int) or val < 0 or val > 4:
                raise ValueError(f"Item {idx + 1} must be an integer between 0 and 4")

        total_score = sum(all_items)
        screen_positive = total_score >= screening_cutoff

        interpretation = self._get_interpretation(total_score, screen_positive, screening_cutoff)

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "cluster_b_items": cluster_b,
                "cluster_c_items": cluster_c,
                "cluster_d_items": cluster_d,
                "cluster_e_items": cluster_e,
                "screening_cutoff": screening_cutoff,
            },
            calculation_details={
                "total_score": total_score,
                "max_score": 80,
                "cluster_b_score": sum(cluster_b),
                "cluster_c_score": sum(cluster_c),
                "cluster_d_score": sum(cluster_d),
                "cluster_e_score": sum(cluster_e),
                "screen_positive": screen_positive,
            },
        )

    def _get_interpretation(self, score: int, screen_positive: bool, cutoff: int) -> Interpretation:
        """Generate interpretation based on PCL-5 score"""

        if score < 20:
            severity = Severity.NORMAL
            severity_text = "Minimal"
        elif score < 31:
            severity = Severity.MILD
            severity_text = "Mild"
        elif score < 50:
            severity = Severity.MODERATE
            severity_text = "Moderate"
        else:
            severity = Severity.SEVERE
            severity_text = "Severe"

        if screen_positive:
            return Interpretation(
                summary=f"PCL-5 {score}/80: POSITIVE SCREEN",
                detail=f"Score ≥{cutoff} suggests probable PTSD. {severity_text} symptom level.",
                severity=severity,
                stage=f"Positive Screen - {severity_text}",
                stage_description=f"PCL-5 ≥{cutoff}: Positive screen",
                recommendations=(
                    "Clinical interview recommended (CAPS-5)",
                    "Consider evidence-based treatments if confirmed",
                ),
                next_steps=("Diagnostic evaluation", "CAPS-5 assessment"),
            )
        else:
            return Interpretation(
                summary=f"PCL-5 {score}/80: NEGATIVE SCREEN",
                detail=f"Score <{cutoff} suggests low likelihood of PTSD. {severity_text} symptoms.",
                severity=severity,
                stage=f"Negative Screen - {severity_text}",
                stage_description=f"PCL-5 <{cutoff}: Negative screen",
                recommendations=("Reassess if clinical concern persists",),
                next_steps=("Continue monitoring if indicated",),
            )
