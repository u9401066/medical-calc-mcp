"""
EPDS (Edinburgh Postnatal Depression Scale)

The EPDS is a 10-item validated screening tool for postnatal
(postpartum) depression. It can also be used during pregnancy.

Reference (Original Development):
    Cox JL, Holden JM, Sagovsky R. Detection of postnatal depression.
    Development of the 10-item Edinburgh Postnatal Depression Scale.
    Br J Psychiatry. 1987;150:782-786.
    PMID: 3651732

Reference (ACOG Recommendation):
    American College of Obstetricians and Gynecologists. ACOG Committee
    Opinion No. 757: Screening for Perinatal Depression. Obstet Gynecol.
    2018;132(5):e208-e212.
    PMID: 30629567
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


class EPDSCalculator(BaseCalculator):
    """
    EPDS (Edinburgh Postnatal Depression Scale) Calculator

    10-item self-report questionnaire for perinatal depression screening.
    Score range: 0-30
    Cutoff ≥10 suggests possible depression; ≥13 suggests probable depression.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="epds",
                name="EPDS (Edinburgh Postnatal Depression Scale)",
                purpose="Screen for postnatal and perinatal depression",
                input_params=[
                    "q1_laugh",
                    "q2_enjoyment",
                    "q3_blame",
                    "q4_anxious",
                    "q5_scared",
                    "q6_overwhelmed",
                    "q7_sleep_difficulty",
                    "q8_sad",
                    "q9_crying",
                    "q10_self_harm",
                ],
                output_type="Score 0-30 with depression risk assessment",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.GYNECOLOGY,
                    Specialty.PSYCHIATRY,
                    Specialty.FAMILY_MEDICINE,
                ),
                conditions=(
                    "Postpartum Depression",
                    "Postnatal Depression",
                    "Perinatal Depression",
                    "Antenatal Depression",
                    "Maternal Mental Health",
                ),
                clinical_contexts=(
                    ClinicalContext.SCREENING,
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "Does this patient have postpartum depression?",
                    "Screen for perinatal depression",
                    "Calculate EPDS score",
                    "Assess maternal mental health",
                ),
                keywords=(
                    "EPDS",
                    "Edinburgh",
                    "postpartum depression",
                    "postnatal depression",
                    "perinatal depression",
                    "maternal depression",
                ),
            ),
            references=(
                Reference(
                    citation="Cox JL, Holden JM, Sagovsky R. Detection of postnatal depression: Development of the 10-item Edinburgh Postnatal Depression Scale. Br J Psychiatry. 1987;150:782-786.",
                    pmid="3651732",
                    doi="10.1192/bjp.150.6.782",
                    year=1987,
                ),
                Reference(
                    citation="American College of Obstetricians and Gynecologists. ACOG Committee Opinion No. 757: Screening for Perinatal Depression. Obstet Gynecol. 2018;132(5):e208-e212.",
                    pmid="30629567",
                    doi="10.1097/AOG.0000000000002927",
                    year=2018,
                ),
            ),
        )

    def calculate(self, **params) -> ScoreResult:
        """
        Calculate EPDS score.

        Args:
            Each question scored 0-3 based on frequency in past 7 days.

            Questions 1, 2 (ability to laugh, enjoyment):
                0 = As much as ever, 1 = Not quite so much, 2 = Definitely not so much, 3 = Not at all

            Questions 3-10 (negative items - scoring reversed):
                For q3, q5, q6, q7, q8, q9, q10:
                0 = No/Never, 1 = Not very often, 2 = Yes sometimes, 3 = Yes most of the time

            q1_laugh: Able to laugh and see the funny side (0-3)
            q2_enjoyment: Look forward with enjoyment (0-3)
            q3_blame: Blamed self unnecessarily (0-3)
            q4_anxious: Been anxious or worried for no good reason (0-3)
            q5_scared: Felt scared or panicky for no good reason (0-3)
            q6_overwhelmed: Things have been getting on top of me (0-3)
            q7_sleep_difficulty: So unhappy that difficulty sleeping (0-3)
            q8_sad: Felt sad or miserable (0-3)
            q9_crying: So unhappy have been crying (0-3)
            q10_self_harm: Thought of harming self (0-3)

        Returns:
            ScoreResult with EPDS score and risk assessment
        """
        questions = [
            "q1_laugh",
            "q2_enjoyment",
            "q3_blame",
            "q4_anxious",
            "q5_scared",
            "q6_overwhelmed",
            "q7_sleep_difficulty",
            "q8_sad",
            "q9_crying",
            "q10_self_harm",
        ]

        scores = {}
        for q in questions:
            value = int(params.get(q, 0))
            if not 0 <= value <= 3:
                raise ValueError(f"{q} must be 0-3")
            scores[q] = value

        total_score = sum(scores.values())

        # Check for self-harm ideation (Q10)
        self_harm_score = scores["q10_self_harm"]
        has_self_harm_ideation = self_harm_score > 0

        # Determine severity
        if total_score < 10:
            severity = Severity.NORMAL
            severity_text = "Low risk - depression unlikely"
            stage = "Low risk"
        elif total_score < 13:
            severity = Severity.MODERATE
            severity_text = "Possible depression"
            stage = "Possible depression"
        elif total_score < 20:
            severity = Severity.SEVERE
            severity_text = "Probable depression"
            stage = "Probable depression"
        else:
            severity = Severity.CRITICAL
            severity_text = "Severe depression likely"
            stage = "Severe"

        # Override severity if self-harm present
        if has_self_harm_ideation:
            if severity.value < Severity.SEVERE.value:
                severity = Severity.SEVERE

        # Subscale analysis
        anxiety_items = scores["q4_anxious"] + scores["q5_scared"]
        depression_items = scores["q8_sad"] + scores["q9_crying"]
        anhedonia_items = scores["q1_laugh"] + scores["q2_enjoyment"]

        # Recommendations (per ACOG guidelines)
        recommendations = []
        if total_score < 10:
            recommendations.append("Low risk - routine follow-up")
            recommendations.append("Provide education on warning signs")
            recommendations.append("Rescreen at 4-6 weeks postpartum")
        elif total_score < 13:
            recommendations.append("Possible depression - clinical interview recommended")
            recommendations.append("Consider referral for psychological support")
            recommendations.append("Close follow-up in 2-4 weeks")
        else:
            recommendations.append("Probable depression - full psychiatric evaluation needed")
            recommendations.append("Consider referral to psychiatrist/psychologist")
            recommendations.append("Discuss treatment options (therapy, medication)")
            recommendations.append("Assess social support and safety")

        if has_self_harm_ideation:
            recommendations.insert(0, "⚠️ URGENT: Self-harm ideation present - immediate safety assessment")
            recommendations.insert(1, "Assess suicide risk and means access")
            recommendations.insert(2, "Consider psychiatric emergency evaluation")

        warnings = []
        if self_harm_score >= 2:
            warnings.append("Significant self-harm ideation - urgent psychiatric evaluation required")
        elif self_harm_score == 1:
            warnings.append("Self-harm ideation endorsed - requires direct assessment")
        if total_score >= 20:
            warnings.append("Severe depression - high-intensity treatment indicated")
        if anxiety_items >= 4:
            warnings.append("High anxiety symptoms - consider comorbid anxiety disorder")

        next_steps = [
            "Clinical interview to confirm diagnosis",
            "Assess for bipolar disorder (screen with MDQ)",
            "Evaluate breastfeeding status if considering medication",
            "Safety planning if self-harm ideation present",
        ]

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=Interpretation(
                summary=f"EPDS = {total_score}/30: {severity_text}" + (" ⚠️ Self-harm ideation" if has_self_harm_ideation else ""),
                detail=(
                    f"EPDS score of {total_score}/30 indicates {severity_text.lower()}. "
                    f"Subscales: Anhedonia {anhedonia_items}/6, Anxiety {anxiety_items}/6, "
                    f"Depression {depression_items}/6. "
                    f"{'Self-harm ideation (Q10) is positive - requires immediate attention.' if has_self_harm_ideation else 'No self-harm ideation.'}"
                ),
                severity=severity,
                stage=stage,
                stage_description=severity_text,
                recommendations=recommendations,
                warnings=warnings,
                next_steps=next_steps,
            ),
            references=self.metadata.references,
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "total_score": total_score,
                "self_harm_score": self_harm_score,
                "has_self_harm_ideation": has_self_harm_ideation,
                "anhedonia_subscale": anhedonia_items,
                "anxiety_subscale": anxiety_items,
                "depression_subscale": depression_items,
                "severity_category": stage,
                **{f"item_{k}": v for k, v in scores.items()},
            },
        )
