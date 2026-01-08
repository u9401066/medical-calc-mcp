"""
CAPS-5 (Clinician-Administered PTSD Scale for DSM-5)

The CAPS-5 is the gold standard for PTSD assessment.

Reference (Development):
    Weathers FW, Bovin MJ, Lee DJ, et al. The Clinician-Administered
    PTSD Scale for DSM-5 (CAPS-5): Development and initial psychometric
    evaluation in military veterans. Psychol Assess. 2018;30(3):383-395.
    PMID: 28493729

Cochrane Reference:
    Bisson JI, Roberts NP, Andrew M, Cooper R, Lewis C. Psychological
    therapies for chronic post-traumatic stress disorder (PTSD) in adults.
    Cochrane Database Syst Rev. 2013;(12):CD003388.
    PMID: 24338345
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


class CAPS5Calculator(BaseCalculator):
    """
    CAPS-5 (Clinician-Administered PTSD Scale for DSM-5) Calculator

    Gold standard structured interview for PTSD diagnosis.
    Assesses 20 DSM-5 PTSD symptoms across 4 clusters.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="caps5",
                name="CAPS-5 (Clinician-Administered PTSD Scale for DSM-5)",
                purpose="Gold standard diagnostic assessment for PTSD",
                input_params=[
                    "b1_intrusive_memories",
                    "b2_distressing_dreams",
                    "b3_flashbacks",
                    "b4_psychological_distress",
                    "b5_physiological_reactions",
                    "c1_avoidance_thoughts",
                    "c2_avoidance_external",
                    "d1_dissociative_amnesia",
                    "d2_negative_beliefs",
                    "d3_distorted_blame",
                    "d4_negative_emotional_state",
                    "d5_diminished_interest",
                    "d6_detachment",
                    "d7_inability_positive_emotions",
                    "e1_irritability",
                    "e2_reckless_behavior",
                    "e3_hypervigilance",
                    "e4_exaggerated_startle",
                    "e5_concentration_problems",
                    "e6_sleep_disturbance",
                    "duration_over_1_month",
                    "functional_impairment",
                ],
                output_type="CAPS-5 score 0-80 with DSM-5 diagnostic status",
            ),
            high_level=HighLevelKey(
                specialties=(Specialty.PSYCHIATRY,),
                conditions=(
                    "PTSD",
                    "Post-Traumatic Stress Disorder",
                    "Trauma",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "Does this patient meet criteria for PTSD?",
                    "How severe is the PTSD?",
                    "CAPS-5 score",
                ),
                keywords=("CAPS-5", "PTSD diagnosis", "trauma assessment"),
            ),
            references=(
                Reference(
                    citation="Weathers FW, Bovin MJ, Lee DJ, et al. The Clinician-Administered PTSD Scale for DSM-5 (CAPS-5): Development and initial psychometric evaluation in military veterans. Psychol Assess. 2018;30(3):383-395.",
                    pmid="28493729",
                    doi="10.1037/pas0000486",
                    year=2018,
                ),
                Reference(
                    citation="Bisson JI, Roberts NP, Andrew M, Cooper R, Lewis C. Psychological therapies for chronic post-traumatic stress disorder (PTSD) in adults. Cochrane Database Syst Rev. 2013;(12):CD003388.",
                    pmid="24338345",
                    year=2013,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        b1_intrusive_memories: int,
        b2_distressing_dreams: int,
        b3_flashbacks: int,
        b4_psychological_distress: int,
        b5_physiological_reactions: int,
        c1_avoidance_thoughts: int,
        c2_avoidance_external: int,
        d1_dissociative_amnesia: int,
        d2_negative_beliefs: int,
        d3_distorted_blame: int,
        d4_negative_emotional_state: int,
        d5_diminished_interest: int,
        d6_detachment: int,
        d7_inability_positive_emotions: int,
        e1_irritability: int,
        e2_reckless_behavior: int,
        e3_hypervigilance: int,
        e4_exaggerated_startle: int,
        e5_concentration_problems: int,
        e6_sleep_disturbance: int,
        duration_over_1_month: bool = True,
        functional_impairment: bool = True,
    ) -> ScoreResult:
        """
        Calculate CAPS-5 score.

        All symptom items scored 0-4:
        0 = Absent
        1 = Mild/subthreshold
        2 = Moderate/threshold
        3 = Severe
        4 = Extreme

        Symptom counts as present if severity ≥ 2.

        DSM-5 Diagnosis requires:
        - ≥1 Cluster B symptom
        - ≥1 Cluster C symptom
        - ≥2 Cluster D symptoms
        - ≥2 Cluster E symptoms
        - Duration >1 month
        - Functional impairment

        Args:
            All b/c/d/e items: Individual symptom severity (0-4)
            duration_over_1_month: Symptoms present >1 month
            functional_impairment: Clinically significant distress/impairment

        Returns:
            ScoreResult with CAPS-5 score and diagnostic status
        """
        cluster_b = [
            b1_intrusive_memories,
            b2_distressing_dreams,
            b3_flashbacks,
            b4_psychological_distress,
            b5_physiological_reactions,
        ]
        cluster_c = [c1_avoidance_thoughts, c2_avoidance_external]
        cluster_d = [
            d1_dissociative_amnesia,
            d2_negative_beliefs,
            d3_distorted_blame,
            d4_negative_emotional_state,
            d5_diminished_interest,
            d6_detachment,
            d7_inability_positive_emotions,
        ]
        cluster_e = [
            e1_irritability,
            e2_reckless_behavior,
            e3_hypervigilance,
            e4_exaggerated_startle,
            e5_concentration_problems,
            e6_sleep_disturbance,
        ]

        all_items = cluster_b + cluster_c + cluster_d + cluster_e

        # Validate
        for idx, val in enumerate(all_items):
            if not isinstance(val, int) or val < 0 or val > 4:
                raise ValueError(f"Item {idx + 1} must be an integer between 0 and 4")

        # Calculate scores
        total_score = sum(all_items)

        # Count symptoms at threshold
        b_count = sum(1 for x in cluster_b if x >= 2)
        c_count = sum(1 for x in cluster_c if x >= 2)
        d_count = sum(1 for x in cluster_d if x >= 2)
        e_count = sum(1 for x in cluster_e if x >= 2)

        # Check criteria
        criterion_b = b_count >= 1
        criterion_c = c_count >= 1
        criterion_d = d_count >= 2
        criterion_e = e_count >= 2

        all_criteria_met = criterion_b and criterion_c and criterion_d and criterion_e and duration_over_1_month and functional_impairment

        interpretation = self._get_interpretation(total_score, all_criteria_met, b_count, c_count, d_count, e_count)

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
                "duration_over_1_month": duration_over_1_month,
                "functional_impairment": functional_impairment,
            },
            calculation_details={
                "total_score": total_score,
                "max_score": 80,
                "cluster_b_score": sum(cluster_b),
                "cluster_c_score": sum(cluster_c),
                "cluster_d_score": sum(cluster_d),
                "cluster_e_score": sum(cluster_e),
                "dsm5_criteria_met": all_criteria_met,
            },
        )

    def _get_interpretation(
        self,
        score: int,
        criteria_met: bool,
        b_count: int,
        c_count: int,
        d_count: int,
        e_count: int,
    ) -> Interpretation:
        """Generate interpretation based on CAPS-5 score and diagnostic criteria"""

        if criteria_met:
            if score <= 25:
                severity = Severity.MILD
                severity_text = "Mild"
            elif score <= 50:
                severity = Severity.MODERATE
                severity_text = "Moderate"
            else:
                severity = Severity.SEVERE
                severity_text = "Severe"

            return Interpretation(
                summary=f"CAPS-5 {score}/80: PTSD DIAGNOSIS MET - {severity_text}",
                detail=f"Patient meets DSM-5 criteria for PTSD. Symptom clusters: B={b_count}/5, C={c_count}/2, D={d_count}/7, E={e_count}/6.",
                severity=severity,
                stage=f"PTSD - {severity_text}",
                stage_description=f"DSM-5 PTSD criteria met with {severity_text.lower()} severity",
                recommendations=(
                    "Evidence-based treatments: CPT, PE, or EMDR",
                    "Consider pharmacotherapy if indicated",
                ),
                next_steps=("Initiate treatment", "Follow-up assessment"),
            )
        else:
            return Interpretation(
                summary=f"CAPS-5 {score}/80: PTSD DIAGNOSIS NOT MET",
                detail=f"Does not meet DSM-5 PTSD criteria. Symptom clusters: B={b_count}/5, C={c_count}/2, D={d_count}/7, E={e_count}/6.",
                severity=Severity.MILD if score > 10 else Severity.NORMAL,
                stage="Subthreshold/No PTSD",
                stage_description="DSM-5 PTSD criteria not met",
                recommendations=(
                    "Consider other diagnoses",
                    "Monitor symptoms",
                ),
                next_steps=("Further evaluation if indicated",),
            )
