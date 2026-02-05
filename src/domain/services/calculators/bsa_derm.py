"""
BSA for Dermatology (Body Surface Area for Skin Disease Assessment)

The Palmar Method and Rule of Nines are commonly used to estimate
body surface area involvement in dermatological conditions.
The patient's palm (including fingers) represents approximately 1% BSA.

Reference (Rule of Nines):
    Wallace AB. The exposure treatment of burns. Lancet.
    1951;1(6653):501-504.
    PMID: 14805109

Reference (Palmar Method):
    Long CC, Finlay AY. The finger-tip unit--a new practical measure.
    Clin Exp Dermatol. 1991;16(6):444-447.
    PMID: 1806320
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


class BSADermatologyCalculator(BaseCalculator):
    """
    BSA for Dermatology Calculator

    Calculates body surface area involvement for skin conditions
    using either the Rule of Nines or the Palmar Method.
    Used for psoriasis, atopic dermatitis, and other skin diseases.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="bsa_dermatology",
                name="BSA for Dermatology (Body Surface Area)",
                purpose="Estimate body surface area affected by skin disease",
                input_params=[
                    "head_neck",
                    "trunk_anterior",
                    "trunk_posterior",
                    "arm_left",
                    "arm_right",
                    "hand_left",
                    "hand_right",
                    "leg_left",
                    "leg_right",
                    "genital",
                    "age_group",
                ],
                output_type="Percentage BSA with severity classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.DERMATOLOGY,
                    Specialty.RHEUMATOLOGY,
                ),
                conditions=(
                    "Psoriasis",
                    "Atopic Dermatitis",
                    "Skin Disease",
                    "Eczema",
                    "Vitiligo",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "What percentage of body surface area is affected?",
                    "Calculate BSA for skin disease",
                    "Estimate skin involvement",
                ),
                keywords=(
                    "BSA",
                    "body surface area",
                    "skin involvement",
                    "rule of nines",
                    "palmar method",
                ),
            ),
            references=(
                Reference(
                    citation="Wallace AB. The exposure treatment of burns. Lancet. 1951;1(6653):501-504.",
                    pmid="14805109",
                    year=1951,
                ),
                Reference(
                    citation="Long CC, Finlay AY. The finger-tip unit - a new practical measure. Clin Exp Dermatol. 1991;16(6):444-447.",
                    pmid="1806320",
                    doi="10.1111/j.1365-2230.1991.tb01232.x",
                    year=1991,
                ),
            ),
        )

    def calculate(self, **params: Any) -> ScoreResult:
        """
        Calculate BSA involvement.

        Args:
            head_neck: Percentage of head/neck affected (0-100% of that region)
            trunk_anterior: Percentage of anterior trunk affected (0-100%)
            trunk_posterior: Percentage of posterior trunk affected (0-100%)
            arm_left: Percentage of left arm affected (0-100%)
            arm_right: Percentage of right arm affected (0-100%)
            hand_left: Percentage of left hand affected (0-100%)
            hand_right: Percentage of right hand affected (0-100%)
            leg_left: Percentage of left leg affected (0-100%)
            leg_right: Percentage of right leg affected (0-100%)
            genital: Percentage of genital area affected (0-100%)
            age_group: "adult", "child", or "infant" (affects regional percentages)

        Returns:
            ScoreResult with total BSA percentage and severity classification
        """
        # Extract parameters
        head_neck = float(params.get("head_neck", 0))
        trunk_ant = float(params.get("trunk_anterior", 0))
        trunk_post = float(params.get("trunk_posterior", 0))
        arm_left = float(params.get("arm_left", 0))
        arm_right = float(params.get("arm_right", 0))
        hand_left = float(params.get("hand_left", 0))
        hand_right = float(params.get("hand_right", 0))
        leg_left = float(params.get("leg_left", 0))
        leg_right = float(params.get("leg_right", 0))
        genital = float(params.get("genital", 0))
        age_group = str(params.get("age_group", "adult")).lower()

        # Validation
        all_regions = [
            (head_neck, "head_neck"),
            (trunk_ant, "trunk_anterior"),
            (trunk_post, "trunk_posterior"),
            (arm_left, "arm_left"),
            (arm_right, "arm_right"),
            (hand_left, "hand_left"),
            (hand_right, "hand_right"),
            (leg_left, "leg_left"),
            (leg_right, "leg_right"),
            (genital, "genital"),
        ]

        for value, name in all_regions:
            if not 0 <= value <= 100:
                raise ValueError(f"{name} must be 0-100")

        if age_group not in ["adult", "child", "infant"]:
            raise ValueError("age_group must be 'adult', 'child', or 'infant'")

        # Rule of Nines percentages by age group
        if age_group == "adult":
            weights = {
                "head_neck": 9,
                "trunk_anterior": 18,
                "trunk_posterior": 18,
                "arm_each": 9,
                "hand_each": 1,  # Included in arm, but can be separate
                "leg_each": 18,
                "genital": 1,
            }
        elif age_group == "child":
            # Child (1-9 years) - larger head, smaller legs
            weights = {
                "head_neck": 15,
                "trunk_anterior": 18,
                "trunk_posterior": 18,
                "arm_each": 9,
                "hand_each": 1,
                "leg_each": 14,
                "genital": 1,
            }
        else:  # infant
            # Infant (<1 year) - even larger head, smaller legs
            weights: dict[str, float] = {
                "head_neck": 18.0,
                "trunk_anterior": 18.0,
                "trunk_posterior": 18.0,
                "arm_each": 9.0,
                "hand_each": 1.0,
                "leg_each": 13.5,
                "genital": 1.0,
            }

        # Calculate contributions (each region % of that region × weight)
        head_contribution = (head_neck / 100) * weights["head_neck"]
        trunk_ant_contribution = (trunk_ant / 100) * weights["trunk_anterior"]
        trunk_post_contribution = (trunk_post / 100) * weights["trunk_posterior"]
        arm_left_contribution = (arm_left / 100) * weights["arm_each"]
        arm_right_contribution = (arm_right / 100) * weights["arm_each"]
        hand_left_contribution = (hand_left / 100) * weights["hand_each"]
        hand_right_contribution = (hand_right / 100) * weights["hand_each"]
        leg_left_contribution = (leg_left / 100) * weights["leg_each"]
        leg_right_contribution = (leg_right / 100) * weights["leg_each"]
        genital_contribution = (genital / 100) * weights["genital"]

        total_bsa = (
            head_contribution
            + trunk_ant_contribution
            + trunk_post_contribution
            + arm_left_contribution
            + arm_right_contribution
            + hand_left_contribution
            + hand_right_contribution
            + leg_left_contribution
            + leg_right_contribution
            + genital_contribution
        )

        # Determine severity classification (for psoriasis/eczema)
        if total_bsa < 3:
            severity = Severity.MILD
            severity_text = "Mild (<3% BSA)"
            stage = "Mild"
        elif total_bsa < 10:
            severity = Severity.MODERATE
            severity_text = "Moderate (3-10% BSA)"
            stage = "Moderate"
        else:
            severity = Severity.SEVERE
            severity_text = "Severe (>10% BSA)"
            stage = "Severe"

        # Treatment recommendations
        recommendations = []
        if total_bsa < 3:
            recommendations.append("Topical therapy appropriate")
        elif total_bsa < 10:
            recommendations.append("Topical therapy +/- phototherapy")
            recommendations.append("Consider systemic therapy if topicals inadequate")
        else:
            recommendations.append("Systemic therapy or biologics typically indicated")
            recommendations.append("BSA ≥10% meets criteria for moderate-to-severe disease")

        # Biologic eligibility
        biologic_eligible = total_bsa >= 10

        warnings = []
        if genital > 0:
            warnings.append("Genital involvement - may indicate high-impact disease")
        if head_neck >= 50:
            warnings.append("Significant facial/scalp involvement - impacts quality of life")

        next_steps = [
            "Combine with PASI/SCORAD for comprehensive assessment",
            "Assess quality of life with DLQI",
            "Document photographically for monitoring",
        ]

        return ScoreResult(
            value=round(total_bsa, 1),
            unit=Unit.PERCENT,
            interpretation=Interpretation(
                summary=f"BSA = {round(total_bsa, 1)}%: {severity_text}",
                detail=(
                    f"Total body surface area affected: {round(total_bsa, 1)}%. "
                    f"Regional breakdown: Head/neck {round(head_contribution, 1)}%, "
                    f"Trunk {round(trunk_ant_contribution + trunk_post_contribution, 1)}%, "
                    f"Arms {round(arm_left_contribution + arm_right_contribution, 1)}%, "
                    f"Legs {round(leg_left_contribution + leg_right_contribution, 1)}%. "
                    f"Assessment based on {age_group} Rule of Nines."
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
                "total_bsa": round(total_bsa, 1),
                "head_neck_contribution": round(head_contribution, 1),
                "trunk_anterior_contribution": round(trunk_ant_contribution, 1),
                "trunk_posterior_contribution": round(trunk_post_contribution, 1),
                "arm_left_contribution": round(arm_left_contribution, 1),
                "arm_right_contribution": round(arm_right_contribution, 1),
                "leg_left_contribution": round(leg_left_contribution, 1),
                "leg_right_contribution": round(leg_right_contribution, 1),
                "age_group": age_group,
                "biologic_eligible": biologic_eligible,
                "severity_classification": stage,
            },
        )
