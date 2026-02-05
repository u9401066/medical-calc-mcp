"""
NRS-2002 (Nutritional Risk Screening 2002)

The NRS-2002 is a screening tool developed by ESPEN to identify hospitalized
patients at nutritional risk who may benefit from nutritional support.

Reference (Original):
    Kondrup J, Rasmussen HH, Hamberg O, et al. Nutritional risk screening
    (NRS 2002): a new method based on an analysis of controlled clinical
    trials. Clin Nutr. 2003;22(3):321-336.
    DOI: 10.1016/s0261-5614(02)00214-5
    PMID: 12765673

Reference (ESPEN Guideline):
    Cederholm T, Jensen GL, Correia MITD, et al. GLIM criteria for the
    diagnosis of malnutrition - A consensus report from the global clinical
    nutrition community. Clin Nutr. 2019;38(1):1-9.
    PMID: 30181091
"""

from typing import Any, Optional

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class NRS2002Calculator(BaseCalculator):
    """
    NRS-2002 (Nutritional Risk Screening 2002) Calculator

    Two-step screening:
    1. Initial screening (4 questions)
    2. Final screening if initial is positive

    Final screening components:
    - Impaired nutritional status (0-3 points)
    - Severity of disease (0-3 points)
    - Age adjustment (+1 if age ≥70)

    Total score ≥3: At nutritional risk
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="nrs_2002",
                name="NRS-2002 (Nutritional Risk Screening 2002)",
                purpose="Screen hospitalized patients for nutritional risk",
                input_params=["bmi", "weight_loss_percent", "reduced_intake", "disease_severity", "age"],
                output_type="Score (0-7) with nutritional risk classification",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CRITICAL_CARE,
                    Specialty.SURGERY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.ONCOLOGY,
                    Specialty.GASTROENTEROLOGY,
                ),
                conditions=(
                    "Malnutrition",
                    "Undernutrition",
                    "Nutritional Risk",
                    "Weight Loss",
                    "Sarcopenia",
                ),
                clinical_contexts=(
                    ClinicalContext.SCREENING,
                    ClinicalContext.PREOPERATIVE_ASSESSMENT,
                    ClinicalContext.ICU_MANAGEMENT,
                    ClinicalContext.PROGNOSIS,
                ),
                clinical_questions=(
                    "Is this patient at nutritional risk?",
                    "Does this patient need nutritional support?",
                    "Should I consult nutrition services?",
                    "How do I screen for malnutrition?",
                ),
                icd10_codes=("E44", "E46", "R63.4", "R63.6"),
                keywords=(
                    "NRS-2002",
                    "nutritional risk",
                    "malnutrition screening",
                    "ESPEN",
                    "nutrition assessment",
                    "weight loss",
                    "BMI",
                    "undernutrition",
                ),
            ),
            references=(
                Reference(
                    citation="Kondrup J, Rasmussen HH, Hamberg O, et al. Nutritional risk "
                    "screening (NRS 2002): a new method based on an analysis of "
                    "controlled clinical trials. Clin Nutr. 2003;22(3):321-336.",
                    doi="10.1016/s0261-5614(02)00214-5",
                    pmid="12765673",
                    year=2003,
                ),
                Reference(
                    citation="Cederholm T, Jensen GL, Correia MITD, et al. GLIM criteria for the diagnosis of malnutrition. Clin Nutr. 2019;38(1):1-9.",
                    pmid="30181091",
                    year=2019,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        bmi: Optional[float] = None,
        weight_loss_percent_3m: float = 0,
        reduced_intake_percent: float = 100,
        disease_severity: int = 0,
        age: int = 50,
    ) -> ScoreResult:
        """
        Calculate NRS-2002 score.

        Args:
            bmi: Body Mass Index (kg/m²), optional
            weight_loss_percent_3m: Percentage weight loss in last 3 months (0-100)
            reduced_intake_percent: Food intake as % of normal (0-100)
            disease_severity: Disease severity score:
                0 = Normal nutritional requirements
                1 = Mild (hip fracture, chronic patients with complications)
                2 = Moderate (major abdominal surgery, stroke, pneumonia, hematologic malignancy)
                3 = Severe (head injury, BMT, ICU patients with APACHE >10)
            age: Patient age in years

        Returns:
            ScoreResult with NRS-2002 score and interpretation
        """
        # Validate inputs
        if bmi is not None and (bmi < 10 or bmi > 60):
            raise ValueError("BMI must be between 10 and 60 kg/m²")
        if not 0 <= weight_loss_percent_3m <= 100:
            raise ValueError("Weight loss percent must be between 0 and 100")
        if not 0 <= reduced_intake_percent <= 100:
            raise ValueError("Reduced intake percent must be between 0 and 100")
        if not 0 <= disease_severity <= 3:
            raise ValueError("Disease severity must be between 0 and 3")
        if age < 0:
            raise ValueError("Age cannot be negative")

        # Calculate nutritional status score (0-3)
        nutritional_score = 0
        nutritional_details: dict[str, Any] = {}

        # BMI component
        if bmi is not None:
            if bmi < 18.5:
                nutritional_score = max(nutritional_score, 3)
                nutritional_details["bmi"] = {"value": bmi, "score_contribution": "3 (BMI <18.5)"}
            elif bmi < 20.5:
                nutritional_score = max(nutritional_score, 2)
                nutritional_details["bmi"] = {"value": bmi, "score_contribution": "2 (BMI 18.5-20.5)"}
            else:
                nutritional_details["bmi"] = {"value": bmi, "score_contribution": "0 (BMI ≥20.5)"}

        # Weight loss component
        if weight_loss_percent_3m > 5:
            if bmi is not None and bmi < 20.5:
                nutritional_score = max(nutritional_score, 3)
                nutritional_details["weight_loss"] = {"value": weight_loss_percent_3m, "score_contribution": "3 (>5% with low BMI)"}
            elif weight_loss_percent_3m > 5:
                # Score based on weight loss timing and amount
                if weight_loss_percent_3m > 5:
                    nutritional_score = max(nutritional_score, 2)
                    nutritional_details["weight_loss"] = {"value": weight_loss_percent_3m, "score_contribution": "2 (>5% in 3 months)"}
        else:
            nutritional_details["weight_loss"] = {"value": weight_loss_percent_3m, "score_contribution": "0 (≤5%)"}

        # Reduced intake component
        intake_reduction = 100 - reduced_intake_percent
        if intake_reduction >= 75:  # <25% of normal
            nutritional_score = max(nutritional_score, 3)
            nutritional_details["food_intake"] = {"value": f"{reduced_intake_percent}% of normal", "score_contribution": "3 (<25% of normal)"}
        elif intake_reduction >= 50:  # 25-50% of normal
            nutritional_score = max(nutritional_score, 2)
            nutritional_details["food_intake"] = {"value": f"{reduced_intake_percent}% of normal", "score_contribution": "2 (25-50% of normal)"}
        elif intake_reduction >= 25:  # 50-75% of normal
            nutritional_score = max(nutritional_score, 1)
            nutritional_details["food_intake"] = {"value": f"{reduced_intake_percent}% of normal", "score_contribution": "1 (50-75% of normal)"}
        else:
            nutritional_details["food_intake"] = {"value": f"{reduced_intake_percent}% of normal", "score_contribution": "0 (>75% of normal)"}

        # Disease severity score (0-3)
        disease_descriptions = {
            0: "Normal nutritional requirements",
            1: "Mild (hip fracture, chronic complications)",
            2: "Moderate (major surgery, stroke, pneumonia, hematologic malignancy)",
            3: "Severe (head injury, BMT, ICU with APACHE >10)",
        }

        # Age adjustment
        age_adjustment = 1 if age >= 70 else 0

        # Total score
        total_score = nutritional_score + disease_severity + age_adjustment

        # At risk if score ≥3
        at_risk = total_score >= 3

        # Get interpretation
        interpretation = self._get_interpretation(total_score, at_risk, nutritional_score, disease_severity, age_adjustment)

        return ScoreResult(
            value=total_score,
            unit=Unit.SCORE,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "bmi": bmi,
                "weight_loss_percent_3m": weight_loss_percent_3m,
                "reduced_intake_percent": reduced_intake_percent,
                "disease_severity": disease_severity,
                "age": age,
            },
            calculation_details={
                "components": {
                    "nutritional_status": {
                        "score": nutritional_score,
                        "max": 3,
                        "details": nutritional_details,
                    },
                    "disease_severity": {
                        "score": disease_severity,
                        "max": 3,
                        "description": disease_descriptions[disease_severity],
                    },
                    "age_adjustment": {
                        "score": age_adjustment,
                        "age": age,
                        "description": "+1 if age ≥70",
                    },
                },
                "total_score": total_score,
                "max_score": 7,
                "at_risk": at_risk,
                "threshold": 3,
            },
            formula_used="NRS-2002 = Nutritional status (0-3) + Disease severity (0-3) + Age (0/1)",
        )

    def _get_interpretation(self, score: int, at_risk: bool, nutritional: int, disease: int, age_adj: int) -> Interpretation:
        """Get interpretation based on NRS-2002 score"""

        component_text = f"Nutritional={nutritional}, Disease={disease}, Age={age_adj}"

        if at_risk:
            return Interpretation(
                summary=f"NRS-2002 Score {score}: At Nutritional Risk",
                detail=f"Score ≥3 indicates patient is at nutritional risk and likely to benefit from nutritional intervention. Components: {component_text}.",
                severity=Severity.MODERATE if score < 5 else Severity.SEVERE,
                stage="At Risk",
                stage_description="Score ≥3: Nutritional intervention indicated",
                recommendations=(
                    "Initiate nutritional care plan",
                    "Calculate protein and energy requirements",
                    "Standard: 25-30 kcal/kg/day, 1.2-1.5 g protein/kg/day",
                    "Consider early enteral nutrition if oral intake inadequate",
                    "Dietitian/nutrition team consultation",
                    "Monitor weight and intake daily",
                    "Reassess NRS-2002 weekly",
                ),
                warnings=(
                    "Malnutrition associated with worse outcomes",
                    "Increased complication rates and mortality",
                    "Delayed wound healing",
                    "Higher infection risk",
                ),
                next_steps=(
                    "Formal nutrition assessment",
                    "Calculate requirements",
                    "Initiate nutrition support plan",
                    "Document in medical record",
                ),
            )
        else:
            return Interpretation(
                summary=f"NRS-2002 Score {score}: Low Nutritional Risk",
                detail=f"Score <3 indicates patient is not currently at high nutritional risk. "
                f"Components: {component_text}. Rescreen weekly during hospitalization.",
                severity=Severity.NORMAL if score == 0 else Severity.MILD,
                stage="Low Risk",
                stage_description="Score <3: Not at high nutritional risk",
                recommendations=(
                    "Continue regular diet as tolerated",
                    "Monitor food intake",
                    "Rescreen weekly during hospitalization",
                    "Rescreen if clinical condition changes",
                ),
                next_steps=(
                    "Weekly rescreening",
                    "Monitor intake and weight",
                ),
            )
