"""
PASI (Psoriasis Area and Severity Index)

The PASI is the gold standard for measuring psoriasis severity.
It combines assessment of body surface area involvement with
erythema, induration, and desquamation for four body regions.

Reference (Original Development):
    Fredriksson T, Pettersson U. Severe psoriasis - oral therapy with
    a new retinoid. Dermatologica. 1978;157(4):238-244.
    PMID: 357213

Reference (PASI 75/90/100 Response Criteria):
    Carlin CS, Feldman SR, Krueger JG, et al. A 50% reduction in the
    Psoriasis Area and Severity Index (PASI 50) is a clinically
    significant endpoint in the assessment of psoriasis. J Am Acad
    Dermatol. 2004;50(6):859-866.
    PMID: 15153885
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


class PASICalculator(BaseCalculator):
    """
    PASI (Psoriasis Area and Severity Index) Calculator

    Assesses psoriasis severity by combining body surface area involvement
    with clinical signs (erythema, induration, desquamation) across four
    body regions: head, trunk, upper extremities, and lower extremities.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="pasi",
                name="PASI (Psoriasis Area and Severity Index)",
                purpose="Assess psoriasis severity for treatment decisions",
                input_params=[
                    "head_area",
                    "head_erythema",
                    "head_induration",
                    "head_desquamation",
                    "trunk_area",
                    "trunk_erythema",
                    "trunk_induration",
                    "trunk_desquamation",
                    "upper_area",
                    "upper_erythema",
                    "upper_induration",
                    "upper_desquamation",
                    "lower_area",
                    "lower_erythema",
                    "lower_induration",
                    "lower_desquamation",
                ],
                output_type="Score 0-72 with severity classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.DERMATOLOGY,
                    Specialty.RHEUMATOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Psoriasis",
                    "Plaque Psoriasis",
                    "Psoriatic Arthritis",
                    "Chronic Plaque Psoriasis",
                ),
                clinical_contexts=(
                    ClinicalContext.SEVERITY_ASSESSMENT,
                    ClinicalContext.TREATMENT_DECISION,
                    ClinicalContext.MONITORING,
                ),
                clinical_questions=(
                    "How severe is this patient's psoriasis?",
                    "Does this patient qualify for biologic therapy?",
                    "Is there treatment response (PASI 75)?",
                    "Calculate PASI score",
                ),
                keywords=(
                    "PASI",
                    "psoriasis severity",
                    "PASI 75",
                    "PASI 90",
                    "biologic eligibility",
                    "plaque psoriasis",
                ),
            ),
            references=(
                Reference(
                    citation="Fredriksson T, Pettersson U. Severe psoriasis - oral therapy with a new retinoid. Dermatologica. 1978;157(4):238-244.",
                    pmid="357213",
                    year=1978,
                ),
                Reference(
                    citation="Carlin CS, Feldman SR, Krueger JG, et al. A 50% reduction in the Psoriasis Area and Severity Index (PASI 50) is a clinically significant endpoint. J Am Acad Dermatol. 2004;50(6):859-866.",
                    pmid="15153885",
                    doi="10.1016/j.jaad.2003.09.014",
                    year=2004,
                ),
            ),
        )

    def calculate(self, **params: Any) -> ScoreResult:
        """
        Calculate PASI score.

        Args:
            head_area: Area score 0-6 (0=0%, 1=<10%, 2=10-29%, 3=30-49%, 4=50-69%, 5=70-89%, 6=90-100%)
            head_erythema: Erythema score 0-4 (0=none, 1=slight, 2=moderate, 3=severe, 4=very severe)
            head_induration: Induration score 0-4
            head_desquamation: Desquamation (scaling) score 0-4
            trunk_area, trunk_erythema, trunk_induration, trunk_desquamation: Same for trunk
            upper_area, upper_erythema, upper_induration, upper_desquamation: Same for upper limbs
            lower_area, lower_erythema, lower_induration, lower_desquamation: Same for lower limbs

        Returns:
            ScoreResult with PASI score and severity classification
        """
        # Extract parameters with defaults
        head_area = int(params.get("head_area", 0))
        head_erythema = int(params.get("head_erythema", 0))
        head_induration = int(params.get("head_induration", 0))
        head_desquamation = int(params.get("head_desquamation", 0))

        trunk_area = int(params.get("trunk_area", 0))
        trunk_erythema = int(params.get("trunk_erythema", 0))
        trunk_induration = int(params.get("trunk_induration", 0))
        trunk_desquamation = int(params.get("trunk_desquamation", 0))

        upper_area = int(params.get("upper_area", 0))
        upper_erythema = int(params.get("upper_erythema", 0))
        upper_induration = int(params.get("upper_induration", 0))
        upper_desquamation = int(params.get("upper_desquamation", 0))

        lower_area = int(params.get("lower_area", 0))
        lower_erythema = int(params.get("lower_erythema", 0))
        lower_induration = int(params.get("lower_induration", 0))
        lower_desquamation = int(params.get("lower_desquamation", 0))

        # Validation
        for area, name in [
            (head_area, "head_area"),
            (trunk_area, "trunk_area"),
            (upper_area, "upper_area"),
            (lower_area, "lower_area"),
        ]:
            if not 0 <= area <= 6:
                raise ValueError(f"{name} must be 0-6")

        for score, name in [
            (head_erythema, "head_erythema"),
            (head_induration, "head_induration"),
            (head_desquamation, "head_desquamation"),
            (trunk_erythema, "trunk_erythema"),
            (trunk_induration, "trunk_induration"),
            (trunk_desquamation, "trunk_desquamation"),
            (upper_erythema, "upper_erythema"),
            (upper_induration, "upper_induration"),
            (upper_desquamation, "upper_desquamation"),
            (lower_erythema, "lower_erythema"),
            (lower_induration, "lower_induration"),
            (lower_desquamation, "lower_desquamation"),
        ]:
            if not 0 <= score <= 4:
                raise ValueError(f"{name} must be 0-4")

        # Calculate regional scores
        # Body region weights: head=0.1, trunk=0.3, upper=0.2, lower=0.4
        head_score = 0.1 * head_area * (head_erythema + head_induration + head_desquamation)
        trunk_score = 0.3 * trunk_area * (trunk_erythema + trunk_induration + trunk_desquamation)
        upper_score = 0.2 * upper_area * (upper_erythema + upper_induration + upper_desquamation)
        lower_score = 0.4 * lower_area * (lower_erythema + lower_induration + lower_desquamation)

        total_pasi = head_score + trunk_score + upper_score + lower_score

        # Determine severity
        if total_pasi == 0:
            severity = Severity.NORMAL
            severity_text = "Clear"
            stage = "Clear"
        elif total_pasi < 3:
            severity = Severity.MILD
            severity_text = "Minimal psoriasis"
            stage = "Minimal"
        elif total_pasi < 10:
            severity = Severity.MILD
            severity_text = "Mild psoriasis"
            stage = "Mild"
        elif total_pasi < 20:
            severity = Severity.MODERATE
            severity_text = "Moderate psoriasis"
            stage = "Moderate"
        else:
            severity = Severity.SEVERE
            severity_text = "Severe psoriasis"
            stage = "Severe"

        # Treatment recommendations
        recommendations = []
        if total_pasi < 10:
            recommendations.append("Topical therapy appropriate")
        elif total_pasi < 20:
            recommendations.append("Consider phototherapy or systemic therapy")
            recommendations.append("May qualify for systemic treatment if topicals fail")
        else:
            recommendations.append("Systemic therapy or biologics indicated")
            recommendations.append("Meets criteria for moderate-to-severe psoriasis")

        # Biologic eligibility note
        biologic_eligible = total_pasi >= 10
        if biologic_eligible:
            recommendations.append("PASI ≥10: May qualify for biologic therapy")

        warnings = []
        if total_pasi >= 20:
            warnings.append("Severe psoriasis - consider early biologic intervention")

        next_steps = [
            "Consider DLQI for quality of life assessment",
            "Assess for psoriatic arthritis",
            "Monitor PASI response at follow-up (target: PASI 75/90/100)",
        ]

        return ScoreResult(
            value=round(total_pasi, 1),
            unit=Unit.SCORE,
            interpretation=Interpretation(
                summary=f"PASI = {round(total_pasi, 1)}: {severity_text}",
                detail=(
                    f"PASI {round(total_pasi, 1)} indicates {severity_text.lower()}. "
                    f"Regional scores - Head: {round(head_score, 1)}, Trunk: {round(trunk_score, 1)}, "
                    f"Upper: {round(upper_score, 1)}, Lower: {round(lower_score, 1)}. "
                    f"Treatment response targets: PASI 75 (good), PASI 90 (excellent), PASI 100 (complete clearance)."
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
                "total_pasi": round(total_pasi, 1),
                "head_score": round(head_score, 1),
                "trunk_score": round(trunk_score, 1),
                "upper_extremity_score": round(upper_score, 1),
                "lower_extremity_score": round(lower_score, 1),
                "biologic_eligible": biologic_eligible,
                "severity_classification": stage,
            },
        )
