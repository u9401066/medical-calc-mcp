"""
SALT (Severity of Alopecia Tool)

The SALT score quantifies hair loss by assessing the percentage of
scalp involvement in alopecia areata and related conditions. It divides
the scalp into four quadrants with standardized percentages.

Reference (Original Development):
    Olsen EA, Hordinsky MK, Price VH, et al. Alopecia areata investigational
    assessment guidelines - Part II. National Alopecia Areata Foundation.
    J Am Acad Dermatol. 2004;51(3):440-447.
    PMID: 15337988

Reference (Clinical Trial Use):
    Olsen EA, Roberts JL, Shapiro J, et al. Evaluation and treatment of
    male and female pattern hair loss. J Am Acad Dermatol. 2005;52(2):301-311.
    PMID: 15692478
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


class SALTCalculator(BaseCalculator):
    """
    SALT (Severity of Alopecia Tool) Calculator

    Assesses scalp hair loss by percentage involvement.
    Scalp divided into 4 quadrants:
    - Top (40% of scalp)
    - Back (24% of scalp)
    - Right side (18% of scalp)
    - Left side (18% of scalp)
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="salt_score",
                name="SALT (Severity of Alopecia Tool)",
                purpose="Quantify hair loss severity in alopecia",
                input_params=[
                    "top_hair_loss",
                    "back_hair_loss",
                    "right_hair_loss",
                    "left_hair_loss",
                ],
                output_type="Score 0-100% with severity classification",
            ),
            high_level=HighLevelKey(
                specialties=(Specialty.DERMATOLOGY,),
                conditions=(
                    "Alopecia Areata",
                    "Alopecia Totalis",
                    "Alopecia Universalis",
                    "Hair Loss",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "How severe is this patient's alopecia?",
                    "What is the SALT score?",
                    "Quantify hair loss percentage",
                    "Calculate alopecia severity",
                ),
                keywords=(
                    "SALT",
                    "alopecia severity",
                    "hair loss",
                    "alopecia areata",
                    "scalp involvement",
                ),
            ),
            references=(
                Reference(
                    citation="Olsen EA, Hordinsky MK, Price VH, et al. Alopecia areata investigational assessment guidelines - Part II. J Am Acad Dermatol. 2004;51(3):440-447.",
                    pmid="15337988",
                    doi="10.1016/j.jaad.2003.09.032",
                    year=2004,
                ),
                Reference(
                    citation="Olsen EA, Roberts JL, Shapiro J, et al. Evaluation and treatment of male and female pattern hair loss. J Am Acad Dermatol. 2005;52(2):301-311.",
                    pmid="15692478",
                    doi="10.1016/j.jaad.2004.11.016",
                    year=2005,
                ),
            ),
        )

    def calculate(self, **params: Any) -> ScoreResult:
        """
        Calculate SALT score.

        Args:
            top_hair_loss: Percentage hair loss in top quadrant (0-100%)
            back_hair_loss: Percentage hair loss in back quadrant (0-100%)
            right_hair_loss: Percentage hair loss in right quadrant (0-100%)
            left_hair_loss: Percentage hair loss in left quadrant (0-100%)

        Returns:
            ScoreResult with SALT score and severity classification
        """
        # Extract parameters
        top_loss = float(params.get("top_hair_loss", 0))
        back_loss = float(params.get("back_hair_loss", 0))
        right_loss = float(params.get("right_hair_loss", 0))
        left_loss = float(params.get("left_hair_loss", 0))

        # Validation
        for loss, name in [
            (top_loss, "top_hair_loss"),
            (back_loss, "back_hair_loss"),
            (right_loss, "right_hair_loss"),
            (left_loss, "left_hair_loss"),
        ]:
            if not 0 <= loss <= 100:
                raise ValueError(f"{name} must be 0-100")

        # Calculate SALT score
        # Scalp weights: top=40%, back=24%, right=18%, left=18%
        top_contribution = (top_loss / 100) * 40
        back_contribution = (back_loss / 100) * 24
        right_contribution = (right_loss / 100) * 18
        left_contribution = (left_loss / 100) * 18

        total_salt = top_contribution + back_contribution + right_contribution + left_contribution

        # Determine severity classification
        if total_salt == 0:
            severity = Severity.NORMAL
            severity_text = "No hair loss (S0)"
            stage = "S0"
            stage_desc = "No scalp hair loss"
        elif total_salt < 25:
            severity = Severity.MILD
            severity_text = "Limited hair loss (S1)"
            stage = "S1"
            stage_desc = "<25% scalp hair loss"
        elif total_salt < 50:
            severity = Severity.MODERATE
            severity_text = "Moderate hair loss (S2)"
            stage = "S2"
            stage_desc = "25-49% scalp hair loss"
        elif total_salt < 75:
            severity = Severity.SEVERE
            severity_text = "Extensive hair loss (S3)"
            stage = "S3"
            stage_desc = "50-74% scalp hair loss"
        elif total_salt < 100:
            severity = Severity.SEVERE
            severity_text = "Near-total hair loss (S4)"
            stage = "S4"
            stage_desc = "75-99% scalp hair loss"
        else:
            severity = Severity.CRITICAL
            severity_text = "Total scalp hair loss (S5 - Alopecia Totalis)"
            stage = "S5"
            stage_desc = "100% scalp hair loss (Alopecia Totalis)"

        # Check for specific patterns
        is_totalis = total_salt == 100

        # Treatment recommendations
        recommendations = []
        if total_salt == 0:
            recommendations.append("No treatment needed")
        elif total_salt < 25:
            recommendations.append("Topical corticosteroids or minoxidil")
            recommendations.append("Intralesional corticosteroid injections")
        elif total_salt < 50:
            recommendations.append("Intralesional corticosteroids")
            recommendations.append("Consider topical immunotherapy (DPCP)")
            recommendations.append("May consider systemic therapy if progressing")
        else:
            recommendations.append("Consider systemic therapy (JAK inhibitors, methotrexate)")
            recommendations.append("Wigs or hairpieces for cosmetic management")
            recommendations.append("Psychological support recommended")

        # JAK inhibitor eligibility (FDA approved for SALT ≥50%)
        jak_eligible = total_salt >= 50
        if jak_eligible:
            recommendations.append("SALT ≥50%: May qualify for JAK inhibitor therapy (baricitinib)")

        warnings = []
        if total_salt >= 50:
            warnings.append("Extensive hair loss - assess for body hair involvement")
        if total_salt == 100:
            warnings.append("Alopecia totalis - evaluate for alopecia universalis")

        next_steps = [
            "Document with photography for monitoring",
            "Assess for nail involvement",
            "Evaluate for associated autoimmune conditions",
            "Consider dermoscopy examination",
        ]

        return ScoreResult(
            value=round(total_salt, 1),
            unit=Unit.PERCENT,
            interpretation=Interpretation(
                summary=f"SALT = {round(total_salt, 1)}%: {severity_text}",
                detail=(
                    f"SALT score {round(total_salt, 1)}% indicates {stage_desc}. "
                    f"Regional contributions: Top {round(top_contribution, 1)}% (of 40%), "
                    f"Back {round(back_contribution, 1)}% (of 24%), "
                    f"Right {round(right_contribution, 1)}% (of 18%), "
                    f"Left {round(left_contribution, 1)}% (of 18%)."
                ),
                severity=severity,
                stage=stage,
                stage_description=stage_desc,
                recommendations=tuple(recommendations),
                warnings=tuple(warnings),
                next_steps=tuple(next_steps),
            ),
            references=list(self.metadata.references),
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "total_salt": round(total_salt, 1),
                "top_contribution": round(top_contribution, 1),
                "back_contribution": round(back_contribution, 1),
                "right_contribution": round(right_contribution, 1),
                "left_contribution": round(left_contribution, 1),
                "severity_stage": stage,
                "is_alopecia_totalis": is_totalis,
                "jak_inhibitor_eligible": jak_eligible,
            },
        )
