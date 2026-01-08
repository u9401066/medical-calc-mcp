"""
NDS (Neuropathy Disability Score)

The NDS is a clinical examination tool to assess the severity of
diabetic peripheral neuropathy by evaluating sensory and reflex
abnormalities.

Reference (Original Development):
    Young MJ, Boulton AJ, MacLeod AF, et al. A multicentre study of the
    prevalence of diabetic peripheral neuropathy in the United Kingdom
    hospital clinic population. Diabetologia. 1993;36(2):150-154.
    PMID: 8458529

Reference (Validation):
    Boulton AJ, Malik RA, Arezzo JC, Sosenko JM. Diabetic somatic
    neuropathies. Diabetes Care. 2004;27(6):1458-1486.
    PMID: 15161806
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


class NDSCalculator(BaseCalculator):
    """
    NDS (Neuropathy Disability Score) Calculator

    Clinical assessment of diabetic peripheral neuropathy
    based on sensory modalities and reflexes.
    Score range: 0-10 (bilateral lower extremities)
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="nds",
                name="NDS (Neuropathy Disability Score)",
                purpose="Assess severity of diabetic peripheral neuropathy",
                input_params=[
                    "vibration_right",
                    "vibration_left",
                    "pinprick_right",
                    "pinprick_left",
                    "temperature_right",
                    "temperature_left",
                    "ankle_reflex_right",
                    "ankle_reflex_left",
                ],
                output_type="Score 0-10 with neuropathy severity",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.ENDOCRINOLOGY,
                    Specialty.NEUROLOGY,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Diabetic Neuropathy",
                    "Peripheral Neuropathy",
                    "Diabetic Peripheral Neuropathy",
                    "DPN",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.SCREENING,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "How severe is this patient's diabetic neuropathy?",
                    "Does this patient have peripheral neuropathy?",
                    "Calculate NDS score",
                    "Assess neuropathy severity",
                ),
                keywords=(
                    "NDS",
                    "neuropathy disability score",
                    "diabetic neuropathy",
                    "peripheral neuropathy",
                    "sensory examination",
                ),
            ),
            references=(
                Reference(
                    citation="Young MJ, Boulton AJ, MacLeod AF, et al. A multicentre study of the prevalence of diabetic peripheral neuropathy. Diabetologia. 1993;36(2):150-154.",
                    pmid="8458529",
                    doi="10.1007/BF00400697",
                    year=1993,
                ),
                Reference(
                    citation="Boulton AJ, Malik RA, Arezzo JC, Sosenko JM. Diabetic somatic neuropathies. Diabetes Care. 2004;27(6):1458-1486.",
                    pmid="15161806",
                    doi="10.2337/diacare.27.6.1458",
                    year=2004,
                ),
            ),
        )

    def calculate(self, **params) -> ScoreResult:
        """
        Calculate NDS score.

        Args:
            vibration_right: Right foot vibration sense ("normal", "reduced", "absent")
            vibration_left: Left foot vibration sense
            pinprick_right: Right foot pinprick sense ("normal", "reduced", "absent")
            pinprick_left: Left foot pinprick sense
            temperature_right: Right foot temperature sense ("normal", "reduced", "absent")
            temperature_left: Left foot temperature sense
            ankle_reflex_right: Right ankle reflex ("present", "reduced", "absent")
            ankle_reflex_left: Left ankle reflex

        Returns:
            ScoreResult with NDS score and neuropathy severity
        """

        def score_sensation(value: str) -> int:
            """Score sensory modality: normal=0, reduced=0.5, absent=1"""
            value = str(value).lower()
            if value == "normal":
                return 0
            elif value == "reduced":
                return 1  # In original NDS, reduced counts as abnormal
            elif value == "absent":
                return 1
            else:
                raise ValueError(f"Invalid sensation value: {value}. Use 'normal', 'reduced', or 'absent'")

        def score_reflex(value: str) -> int:
            """Score ankle reflex: present=0, reduced=1, absent=2"""
            value = str(value).lower()
            if value == "present":
                return 0
            elif value == "reduced":
                return 1
            elif value == "absent":
                return 2
            else:
                raise ValueError(f"Invalid reflex value: {value}. Use 'present', 'reduced', or 'absent'")

        # Score each modality
        vibration_r = score_sensation(params.get("vibration_right", "normal"))
        vibration_l = score_sensation(params.get("vibration_left", "normal"))
        pinprick_r = score_sensation(params.get("pinprick_right", "normal"))
        pinprick_l = score_sensation(params.get("pinprick_left", "normal"))
        temperature_r = score_sensation(params.get("temperature_right", "normal"))
        temperature_l = score_sensation(params.get("temperature_left", "normal"))
        reflex_r = score_reflex(params.get("ankle_reflex_right", "present"))
        reflex_l = score_reflex(params.get("ankle_reflex_left", "present"))

        # Calculate total score
        sensory_score = vibration_r + vibration_l + pinprick_r + pinprick_l + temperature_r + temperature_l
        reflex_score = reflex_r + reflex_l

        total_score = sensory_score + reflex_score

        # Determine severity
        if total_score <= 2:
            severity = Severity.NORMAL
            severity_text = "No or minimal neuropathy"
            stage = "Normal/Minimal"
        elif total_score <= 4:
            severity = Severity.MILD
            severity_text = "Mild neuropathy"
            stage = "Mild"
        elif total_score <= 6:
            severity = Severity.MODERATE
            severity_text = "Moderate neuropathy"
            stage = "Moderate"
        else:
            severity = Severity.SEVERE
            severity_text = "Severe neuropathy"
            stage = "Severe"

        # Count abnormal findings
        abnormal_modalities = []
        if vibration_r or vibration_l:
            abnormal_modalities.append("vibration")
        if pinprick_r or pinprick_l:
            abnormal_modalities.append("pinprick")
        if temperature_r or temperature_l:
            abnormal_modalities.append("temperature")
        if reflex_r or reflex_l:
            abnormal_modalities.append("ankle reflexes")

        # Recommendations
        recommendations = []
        if total_score <= 2:
            recommendations.append("Annual foot examination")
            recommendations.append("Continue diabetes management optimization")
        elif total_score <= 4:
            recommendations.append("Foot care education essential")
            recommendations.append("Consider nerve conduction studies if diagnosis uncertain")
            recommendations.append("Optimize glycemic control")
        elif total_score <= 6:
            recommendations.append("High risk for foot ulceration - regular podiatry")
            recommendations.append("Protective footwear recommended")
            recommendations.append("Consider pain management if symptomatic")
        else:
            recommendations.append("Very high ulceration risk - intensive foot surveillance")
            recommendations.append("Custom therapeutic footwear")
            recommendations.append("Consider multidisciplinary diabetic foot team")

        warnings = []
        if total_score >= 6:
            warnings.append("High risk for foot ulceration and Charcot foot")
        if reflex_r == 2 or reflex_l == 2:
            warnings.append("Absent ankle reflexes - advanced neuropathy")

        next_steps = [
            "Combine with monofilament testing (10g)",
            "Annual foot examination",
            "Consider NCS/EMG if atypical presentation",
        ]

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=Interpretation(
                summary=f"NDS = {total_score}/10: {severity_text}",
                detail=(
                    f"NDS score of {total_score}/10 indicates {severity_text.lower()}. "
                    f"Sensory score: {sensory_score}/6, Reflex score: {reflex_score}/4. "
                    f"Abnormal findings: {', '.join(abnormal_modalities) if abnormal_modalities else 'None'}."
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
                "sensory_score": sensory_score,
                "reflex_score": reflex_score,
                "vibration_right": vibration_r,
                "vibration_left": vibration_l,
                "pinprick_right": pinprick_r,
                "pinprick_left": pinprick_l,
                "temperature_right": temperature_r,
                "temperature_left": temperature_l,
                "ankle_reflex_right": reflex_r,
                "ankle_reflex_left": reflex_l,
                "abnormal_modalities": abnormal_modalities,
                "severity_classification": stage,
            },
        )
