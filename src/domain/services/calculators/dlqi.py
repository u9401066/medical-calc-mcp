"""
DLQI (Dermatology Life Quality Index)

The DLQI is the most widely used dermatology-specific quality of life
measure. It consists of 10 questions covering symptoms, daily activities,
leisure, work, relationships, and treatment impact.

Reference (Original Development):
    Finlay AY, Khan GK. Dermatology Life Quality Index (DLQI) - a simple
    practical measure for routine clinical use. Clin Exp Dermatol.
    1994;19(3):210-216.
    PMID: 8033378

Reference (DLQI Banding):
    Hongbo Y, Thomas CL, Harrison MA, et al. Translating the science of
    quality of life into practice: What do dermatology life quality index
    scores mean? J Invest Dermatol. 2005;125(4):659-664.
    PMID: 16185263
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


class DLQICalculator(BaseCalculator):
    """
    DLQI (Dermatology Life Quality Index) Calculator

    10-question quality of life measure for skin conditions.
    Each question scored 0-3 (not at all/not relevant = 0,
    a little = 1, a lot = 2, very much = 3).
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="dlqi",
                name="DLQI (Dermatology Life Quality Index)",
                purpose="Assess quality of life impact of skin disease",
                input_params=[
                    "symptoms_feelings",
                    "embarrassment",
                    "daily_activities",
                    "clothing",
                    "leisure_social",
                    "sport_exercise",
                    "work_study",
                    "relationships",
                    "sexual_difficulties",
                    "treatment_burden",
                ],
                output_type="Score 0-30 with QoL impact classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.DERMATOLOGY,
                    Specialty.RHEUMATOLOGY,
                    Specialty.ALLERGY_IMMUNOLOGY,
                ),
                conditions=(
                    "Psoriasis",
                    "Atopic Dermatitis",
                    "Acne",
                    "Eczema",
                    "Hidradenitis Suppurativa",
                    "Chronic Urticaria",
                    "Vitiligo",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "How does this skin condition affect quality of life?",
                    "Does this patient qualify for biologic therapy?",
                    "What is the DLQI score?",
                    "Assess dermatology quality of life",
                ),
                keywords=(
                    "DLQI",
                    "quality of life",
                    "dermatology QoL",
                    "skin disease impact",
                    "biologic eligibility",
                ),
            ),
            references=(
                Reference(
                    citation="Finlay AY, Khan GK. Dermatology Life Quality Index (DLQI) - a simple practical measure for routine clinical use. Clin Exp Dermatol. 1994;19(3):210-216.",
                    pmid="8033378",
                    doi="10.1111/j.1365-2230.1994.tb01167.x",
                    year=1994,
                ),
                Reference(
                    citation="Hongbo Y, Thomas CL, Harrison MA, et al. Translating the science of quality of life into practice: What do DLQI scores mean? J Invest Dermatol. 2005;125(4):659-664.",
                    pmid="16185263",
                    doi="10.1111/j.0022-202X.2005.23621.x",
                    year=2005,
                ),
            ),
        )

    def calculate(self, **params) -> ScoreResult:
        """
        Calculate DLQI score.

        Args:
            symptoms_feelings: Q1 - Itchy, sore, painful, stinging (0-3)
            embarrassment: Q2 - Embarrassed or self-conscious (0-3)
            daily_activities: Q3 - Interfered with shopping, housework (0-3)
            clothing: Q4 - Influenced clothes worn (0-3)
            leisure_social: Q5 - Affected social or leisure activities (0-3)
            sport_exercise: Q6 - Made it difficult to do sport (0-3)
            work_study: Q7 - Prevented working or studying (0-3)
            relationships: Q8 - Problems with partner, friends, relatives (0-3)
            sexual_difficulties: Q9 - Caused sexual difficulties (0-3)
            treatment_burden: Q10 - Treatment has been a problem (0-3)

        Returns:
            ScoreResult with DLQI score and impact classification
        """
        # Extract parameters
        q1 = int(params.get("symptoms_feelings", 0))
        q2 = int(params.get("embarrassment", 0))
        q3 = int(params.get("daily_activities", 0))
        q4 = int(params.get("clothing", 0))
        q5 = int(params.get("leisure_social", 0))
        q6 = int(params.get("sport_exercise", 0))
        q7 = int(params.get("work_study", 0))
        q8 = int(params.get("relationships", 0))
        q9 = int(params.get("sexual_difficulties", 0))
        q10 = int(params.get("treatment_burden", 0))

        # Validation
        scores = [
            (q1, "symptoms_feelings"),
            (q2, "embarrassment"),
            (q3, "daily_activities"),
            (q4, "clothing"),
            (q5, "leisure_social"),
            (q6, "sport_exercise"),
            (q7, "work_study"),
            (q8, "relationships"),
            (q9, "sexual_difficulties"),
            (q10, "treatment_burden"),
        ]

        for score, name in scores:
            if not 0 <= score <= 3:
                raise ValueError(f"{name} must be 0-3")

        # Calculate total
        total_dlqi = q1 + q2 + q3 + q4 + q5 + q6 + q7 + q8 + q9 + q10

        # Calculate domain scores
        symptoms_domain = q1 + q2  # Symptoms and feelings (0-6)
        daily_domain = q3 + q4  # Daily activities (0-6)
        leisure_domain = q5 + q6  # Leisure (0-6)
        work_domain = q7  # Work and school (0-3)
        relationships_domain = q8 + q9  # Personal relationships (0-6)
        treatment_domain = q10  # Treatment (0-3)

        # Determine impact level (DLQI banding)
        if total_dlqi <= 1:
            severity = Severity.NORMAL
            impact_text = "No effect on patient's life"
            stage = "No effect"
        elif total_dlqi <= 5:
            severity = Severity.MILD
            impact_text = "Small effect on patient's life"
            stage = "Small effect"
        elif total_dlqi <= 10:
            severity = Severity.MODERATE
            impact_text = "Moderate effect on patient's life"
            stage = "Moderate effect"
        elif total_dlqi <= 20:
            severity = Severity.SEVERE
            impact_text = "Very large effect on patient's life"
            stage = "Very large effect"
        else:
            severity = Severity.CRITICAL
            impact_text = "Extremely large effect on patient's life"
            stage = "Extremely large effect"

        # Treatment recommendations
        recommendations = []
        if total_dlqi <= 5:
            recommendations.append("Continue current management")
        elif total_dlqi <= 10:
            recommendations.append("Consider treatment escalation")
            recommendations.append("Address specific impacted domains")
        else:
            recommendations.append("Significant QoL impairment - optimize treatment")
            recommendations.append("DLQI ≥10 often used as threshold for systemic/biologic therapy")
            recommendations.append("Consider psychological support")

        # Biologic eligibility (commonly DLQI ≥10)
        biologic_eligible = total_dlqi >= 10

        warnings = []
        if total_dlqi >= 20:
            warnings.append("Extremely high QoL impact - urgent treatment optimization needed")
        if relationships_domain >= 4:
            warnings.append("Significant relationship impact - consider psychosocial support")

        next_steps = [
            "Combine with disease severity score (PASI, SCORAD)",
            "Reassess DLQI after treatment change",
            "Address highest-scoring domains specifically",
        ]

        return ScoreResult(
            value=total_dlqi,
            unit=Unit.SCORE,
            interpretation=Interpretation(
                summary=f"DLQI = {total_dlqi}: {impact_text}",
                detail=(
                    f"DLQI {total_dlqi}/30 indicates {impact_text.lower()}. "
                    f"Domain scores: Symptoms/feelings {symptoms_domain}/6, "
                    f"Daily activities {daily_domain}/6, Leisure {leisure_domain}/6, "
                    f"Work {work_domain}/3, Relationships {relationships_domain}/6, "
                    f"Treatment {treatment_domain}/3."
                ),
                severity=severity,
                stage=stage,
                stage_description=impact_text,
                recommendations=recommendations,
                warnings=warnings,
                next_steps=next_steps,
            ),
            references=self.metadata.references,
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "total_dlqi": total_dlqi,
                "symptoms_feelings_domain": symptoms_domain,
                "daily_activities_domain": daily_domain,
                "leisure_domain": leisure_domain,
                "work_domain": work_domain,
                "relationships_domain": relationships_domain,
                "treatment_domain": treatment_domain,
                "biologic_eligible": biologic_eligible,
                "impact_band": stage,
            },
        )
