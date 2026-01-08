"""
MNA (Mini Nutritional Assessment)

The MNA is a validated screening and assessment tool to identify
geriatric patients who are malnourished or at risk of malnutrition.

Reference (Original/Full MNA):
    Guigoz Y, Vellas B, Garry PJ. Assessing the nutritional status
    of the elderly: The Mini Nutritional Assessment as part of the
    geriatric evaluation. Nutr Rev. 1996;54(1 Pt 2):S59-65.
    PMID: 8919685

Reference (MNA-SF Short Form):
    Rubenstein LZ, Harker JO, Salvà A, et al. Screening for
    undernutrition in geriatric practice: developing the short-form
    mini-nutritional assessment (MNA-SF).
    J Gerontol A Biol Sci Med Sci. 2001;56(6):M366-372.
    PMID: 11382797
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


class MNACalculator(BaseCalculator):
    """
    MNA (Mini Nutritional Assessment) Calculator

    MNA-SF (Short Form): 6 questions, max 14 points
    - ≥12: Normal nutritional status
    - 8-11: At risk of malnutrition
    - 0-7: Malnourished
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="mna",
                name="MNA (Mini Nutritional Assessment)",
                purpose="Screen for malnutrition risk in elderly patients",
                input_params=[
                    "food_intake_decline",
                    "weight_loss",
                    "mobility",
                    "psychological_stress",
                    "neuropsychological",
                    "bmi_or_calf",
                ],
                output_type="Score 0-14 with nutritional status classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.GERIATRICS,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.CRITICAL_CARE,
                ),
                conditions=(
                    "Malnutrition",
                    "Frailty",
                    "Cachexia",
                    "Weight Loss",
                    "Anorexia of Aging",
                ),
                clinical_contexts=(
                    ClinicalContext.SCREENING,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "Is this patient at risk of malnutrition?",
                    "Calculate MNA score",
                    "Assess nutritional status",
                    "Screen for malnutrition",
                ),
                keywords=(
                    "MNA",
                    "Mini Nutritional Assessment",
                    "malnutrition",
                    "nutritional screening",
                    "elderly nutrition",
                    "undernutrition",
                ),
            ),
            references=(
                Reference(
                    citation="Guigoz Y, Vellas B, Garry PJ. Assessing the nutritional status of the elderly: The Mini Nutritional Assessment. Nutr Rev. 1996;54(1 Pt 2):S59-65.",
                    pmid="8919685",
                    doi="10.1111/j.1753-4887.1996.tb03793.x",
                    year=1996,
                ),
                Reference(
                    citation="Rubenstein LZ, et al. Screening for undernutrition in geriatric practice: developing the short-form mini-nutritional assessment (MNA-SF). J Gerontol A Biol Sci Med Sci. 2001;56(6):M366-372.",
                    pmid="11382797",
                    doi="10.1093/gerona/56.6.m366",
                    year=2001,
                ),
            ),
        )

    def calculate(self, **params) -> ScoreResult:
        """
        Calculate MNA-SF (Short Form).

        Args:
            food_intake_decline: Food intake decline in past 3 months
                0 = severe decrease
                1 = moderate decrease
                2 = no decrease
            weight_loss: Weight loss in past 3 months
                0 = >3 kg
                1 = does not know
                2 = 1-3 kg
                3 = no weight loss
            mobility:
                0 = bed or chair bound
                1 = able to get out of bed/chair but does not go out
                2 = goes out
            psychological_stress: Acute illness or psychological stress in past 3 months
                0 = yes
                2 = no
            neuropsychological: Neuropsychological problems
                0 = severe dementia or depression
                1 = mild dementia
                2 = no psychological problems
            bmi_or_calf: BMI or calf circumference
                0 = BMI <19 or CC <31cm
                1 = BMI 19-21 or CC 31+ but BMI <21
                2 = BMI 21-23
                3 = BMI ≥23

        Returns:
            ScoreResult with MNA-SF score and nutritional status
        """
        # Validate and collect scores
        items = {
            "food_intake_decline": {"valid": [0, 1, 2], "max": 2},
            "weight_loss": {"valid": [0, 1, 2, 3], "max": 3},
            "mobility": {"valid": [0, 1, 2], "max": 2},
            "psychological_stress": {"valid": [0, 2], "max": 2},
            "neuropsychological": {"valid": [0, 1, 2], "max": 2},
            "bmi_or_calf": {"valid": [0, 1, 2, 3], "max": 3},
        }

        scores = {}
        total = 0

        for item, config in items.items():
            value = params.get(item)
            if value is None:
                raise ValueError(f"Missing required parameter: {item}")

            value = int(value)
            if value not in config["valid"]:
                raise ValueError(f"{item} must be one of {config['valid']}, got {value}")

            scores[item] = value
            total += value

        # Interpretation (MNA-SF cutoffs)
        if total >= 12:
            severity = Severity.NORMAL
            status = "Normal nutritional status"
            detail = "No nutritional intervention needed at this time"
            risk_level = "Low"
        elif total >= 8:
            severity = Severity.MODERATE
            status = "At risk of malnutrition"
            detail = "Nutritional assessment and intervention recommended"
            risk_level = "Moderate"
        else:
            severity = Severity.SEVERE
            status = "Malnourished"
            detail = "Requires comprehensive nutritional intervention"
            risk_level = "High"

        # Identify specific concerns
        concerns = []
        if scores["food_intake_decline"] < 2:
            concerns.append("Decreased food intake")
        if scores["weight_loss"] < 3:
            concerns.append("Recent weight loss")
        if scores["mobility"] < 2:
            concerns.append("Limited mobility")
        if scores["psychological_stress"] == 0:
            concerns.append("Recent psychological stress/illness")
        if scores["neuropsychological"] < 2:
            concerns.append("Neuropsychological issues")
        if scores["bmi_or_calf"] < 2:
            concerns.append("Low BMI or calf circumference")

        # Recommendations
        recommendations = []
        if total >= 12:
            recommendations.append("Continue regular nutritional monitoring")
            recommendations.append("Reassess in 3-6 months or if condition changes")
        elif total >= 8:
            recommendations.append("Perform full MNA assessment")
            recommendations.append("Dietary consultation recommended")
            recommendations.append("Consider oral nutritional supplements")
            recommendations.append("Address modifiable risk factors")
            recommendations.append("Reassess in 1-3 months")
        else:
            recommendations.append("Urgent dietary/nutrition consultation")
            recommendations.append("Consider oral nutritional supplements")
            recommendations.append("Evaluate for underlying causes")
            recommendations.append("Monitor weight weekly")
            recommendations.append("Consider enteral nutrition if oral intake inadequate")

        warnings = []
        if total < 8:
            warnings.append("Malnutrition present - increased morbidity/mortality risk")
        if scores["weight_loss"] == 0:
            warnings.append("Significant weight loss (>3kg) - investigate cause")
        if scores["food_intake_decline"] == 0:
            warnings.append("Severe food intake decline - assess swallowing/appetite")

        next_steps = []
        if total < 12:
            next_steps.append("Complete full MNA assessment (18-item)")
            next_steps.append("Nutritional labs: albumin, prealbumin, lymphocyte count")
        next_steps.append("Address specific concerns identified")
        next_steps.append("Serial MNA monitoring")

        return ScoreResult(
            value=total,
            unit=Unit.SCORE,
            interpretation=Interpretation(
                summary=f"MNA-SF = {total}/14: {status}",
                detail=(
                    f"Mini Nutritional Assessment Short Form score of {total} out of 14 "
                    f"indicates {status.lower()}. {detail}. "
                    f"{'Concerns: ' + ', '.join(concerns) + '.' if concerns else 'No specific nutritional concerns identified.'}"
                ),
                severity=severity,
                stage=status,
                stage_description=detail,
                recommendations=recommendations,
                warnings=warnings,
                next_steps=next_steps,
            ),
            references=self.metadata.references,
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "total_score": total,
                "max_score": 14,
                "item_scores": scores,
                "nutritional_status": status,
                "risk_level": risk_level,
                "concerns": concerns,
            },
        )
