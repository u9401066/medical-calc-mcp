"""
Toronto CSS (Toronto Clinical Scoring System)

The Toronto CSS is a validated clinical tool for diagnosing and
staging diabetic sensorimotor polyneuropathy. It combines symptoms,
sensory tests, and reflexes.

Reference (Original Development & Validation):
    Bril V, Perkins BA. Validation of the Toronto Clinical Scoring System
    for diabetic polyneuropathy. Diabetes Care. 2002;25(11):2048-2052.
    PMID: 12401755

Reference (Staging):
    Perkins BA, Olaleye D, Zinman B, Bril V. Simple screening tests for
    peripheral neuropathy in the diabetes clinic. Diabetes Care.
    2001;24(2):250-256.
    PMID: 11213874
"""

from typing import Any

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


class TorontoCSSCalculator(BaseCalculator):
    """
    Toronto CSS (Toronto Clinical Scoring System) Calculator

    Comprehensive diabetic polyneuropathy assessment combining:
    - Symptom scores (6 items, 0-6)
    - Sensory test scores (5 modalities, 0-5)
    - Reflex scores (knee and ankle, 0-8)
    Total range: 0-19
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="toronto_css",
                name="Toronto CSS (Toronto Clinical Scoring System)",
                purpose="Diagnose and stage diabetic polyneuropathy",
                input_params=[
                    "foot_pain",
                    "numbness",
                    "tingling",
                    "weakness",
                    "ataxia",
                    "upper_limb_symptoms",
                    "pinprick",
                    "temperature",
                    "light_touch",
                    "vibration",
                    "position",
                    "knee_reflex_right",
                    "knee_reflex_left",
                    "ankle_reflex_right",
                    "ankle_reflex_left",
                ],
                output_type="Score 0-19 with neuropathy diagnosis and staging",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.ENDOCRINOLOGY,
                    Specialty.NEUROLOGY,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Diabetic Polyneuropathy",
                    "Diabetic Sensorimotor Neuropathy",
                    "DSPN",
                    "Peripheral Neuropathy",
                ),
                clinical_contexts=(
                    ClinicalContext.DIAGNOSIS,
                    ClinicalContext.STAGING,
                    ClinicalContext.SEVERITY_ASSESSMENT,
                ),
                clinical_questions=(
                    "Does this patient have diabetic polyneuropathy?",
                    "What stage is the diabetic neuropathy?",
                    "Calculate Toronto CSS score",
                    "Assess diabetic neuropathy",
                ),
                keywords=(
                    "Toronto CSS",
                    "Toronto clinical scoring system",
                    "diabetic polyneuropathy",
                    "DSPN",
                    "neuropathy staging",
                ),
            ),
            references=(
                Reference(
                    citation="Bril V, Perkins BA. Validation of the Toronto Clinical Scoring System for diabetic polyneuropathy. Diabetes Care. 2002;25(11):2048-2052.",
                    pmid="12401755",
                    doi="10.2337/diacare.25.11.2048",
                    year=2002,
                ),
                Reference(
                    citation="Perkins BA, Olaleye D, Zinman B, Bril V. Simple screening tests for peripheral neuropathy in the diabetes clinic. Diabetes Care. 2001;24(2):250-256.",
                    pmid="11213874",
                    doi="10.2337/diacare.24.2.250",
                    year=2001,
                ),
            ),
        )

    def calculate(self, **params: Any) -> ScoreResult:
        """
        Calculate Toronto CSS score.

        Args:
            Symptoms (each True/False, max 1 point each):
                foot_pain: Foot pain present
                numbness: Numbness present
                tingling: Tingling present
                weakness: Weakness present
                ataxia: Unsteadiness in walking
                upper_limb_symptoms: Similar symptoms in upper limbs

            Sensory tests (each True if abnormal, max 1 point each):
                pinprick: Pinprick sensation abnormal
                temperature: Temperature sensation abnormal
                light_touch: Light touch abnormal
                vibration: Vibration sense abnormal
                position: Position sense abnormal

            Reflexes (each "normal"=0, "reduced"=1, "absent"=2):
                knee_reflex_right, knee_reflex_left
                ankle_reflex_right, ankle_reflex_left

        Returns:
            ScoreResult with Toronto CSS score and staging
        """
        # Symptom scoring (max 6)
        symptom_items = [
            bool(params.get("foot_pain", False)),
            bool(params.get("numbness", False)),
            bool(params.get("tingling", False)),
            bool(params.get("weakness", False)),
            bool(params.get("ataxia", False)),
            bool(params.get("upper_limb_symptoms", False)),
        ]
        symptom_score = sum(symptom_items)

        # Sensory testing scoring (max 5)
        sensory_items = [
            bool(params.get("pinprick", False)),
            bool(params.get("temperature", False)),
            bool(params.get("light_touch", False)),
            bool(params.get("vibration", False)),
            bool(params.get("position", False)),
        ]
        sensory_score = sum(sensory_items)

        # Reflex scoring
        def score_reflex(value: str) -> int:
            value = str(value).lower()
            if value in ["normal", "present"]:
                return 0
            elif value == "reduced":
                return 1
            elif value == "absent":
                return 2
            else:
                raise ValueError(f"Invalid reflex value: {value}")

        knee_r = score_reflex(params.get("knee_reflex_right", "normal"))
        knee_l = score_reflex(params.get("knee_reflex_left", "normal"))
        ankle_r = score_reflex(params.get("ankle_reflex_right", "normal"))
        ankle_l = score_reflex(params.get("ankle_reflex_left", "normal"))

        reflex_score = knee_r + knee_l + ankle_r + ankle_l  # max 8

        # Total score (max 19)
        total_score = symptom_score + sensory_score + reflex_score

        # Determine diagnosis and staging
        # Toronto CSS ≥6 suggests diabetic polyneuropathy
        has_neuropathy = total_score >= 6

        if total_score < 6:
            severity = Severity.NORMAL
            severity_text = "No diabetic polyneuropathy"
            stage = "No DPN"
        elif total_score <= 8:
            severity = Severity.MILD
            severity_text = "Mild diabetic polyneuropathy"
            stage = "Mild DPN"
        elif total_score <= 11:
            severity = Severity.MODERATE
            severity_text = "Moderate diabetic polyneuropathy"
            stage = "Moderate DPN"
        else:
            severity = Severity.SEVERE
            severity_text = "Severe diabetic polyneuropathy"
            stage = "Severe DPN"

        # Recommendations
        recommendations = []
        if not has_neuropathy:
            recommendations.append("No evidence of polyneuropathy - annual screening")
            recommendations.append("Continue glycemic optimization")
        elif total_score <= 8:
            recommendations.append("Mild DPN - foot care education")
            recommendations.append("Consider nerve conduction studies for confirmation")
        elif total_score <= 11:
            recommendations.append("Moderate DPN - protective footwear")
            recommendations.append("Regular podiatry follow-up")
            recommendations.append("Pain management if symptomatic")
        else:
            recommendations.append("Severe DPN - high ulceration risk")
            recommendations.append("Multidisciplinary foot team involvement")
            recommendations.append("Custom therapeutic footwear essential")

        warnings = []
        if total_score >= 12:
            warnings.append("Severe neuropathy - high risk for foot complications")
        if sensory_score >= 4:
            warnings.append("Significant sensory loss - fall and ulcer risk")
        if bool(params.get("upper_limb_symptoms", False)):
            warnings.append("Upper limb involvement - advanced or diffuse neuropathy")

        next_steps = [
            "Monofilament testing (10g) for ulcer risk",
            "Annual comprehensive foot examination",
            "Nerve conduction studies if diagnosis uncertain",
        ]

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=Interpretation(
                summary=f"Toronto CSS = {total_score}/19: {severity_text}",
                detail=(
                    f"Toronto CSS score of {total_score}/19 indicates {severity_text.lower()}. "
                    f"Components: Symptoms {symptom_score}/6, Sensory {sensory_score}/5, "
                    f"Reflexes {reflex_score}/8. "
                    f"{'Meets criteria for diabetic polyneuropathy (score ≥6).' if has_neuropathy else 'Does not meet DPN criteria.'}"
                ),
                severity=severity,
                stage=stage,
                stage_description=severity_text,
                recommendations=tuple(recommendations),
                warnings=tuple(warnings),
                next_steps=tuple(next_steps),
            ),
            references=list(self.metadata.references),
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "total_score": total_score,
                "symptom_score": symptom_score,
                "sensory_score": sensory_score,
                "reflex_score": reflex_score,
                "has_diabetic_polyneuropathy": has_neuropathy,
                "severity_stage": stage,
            },
        )
