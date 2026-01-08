"""
FINDRISC (Finnish Diabetes Risk Score)

The FINDRISC is a validated screening tool to identify individuals
at high risk of developing type 2 diabetes within 10 years.

Reference (Original Development):
    Lindström J, Tuomilehto J. The diabetes risk score: a practical tool
    to predict type 2 diabetes risk. Diabetes Care. 2003;26(3):725-731.
    PMID: 12610029

Reference (External Validation):
    Schwarz PE, Li J, Lindström J, Tuomilehto J. Tools for predicting the
    risk of type 2 diabetes in daily practice. Horm Metab Res. 2009;41(2):86-97.
    PMID: 19021089
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


class FINDRISCCalculator(BaseCalculator):
    """
    FINDRISC (Finnish Diabetes Risk Score) Calculator

    8-item questionnaire to estimate 10-year risk of developing
    type 2 diabetes mellitus.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="findrisc",
                name="FINDRISC (Finnish Diabetes Risk Score)",
                purpose="Estimate 10-year risk of type 2 diabetes",
                input_params=[
                    "age",
                    "bmi",
                    "waist_circumference",
                    "physical_activity",
                    "daily_vegetables",
                    "antihypertensive",
                    "history_high_glucose",
                    "family_history_diabetes",
                    "sex",
                ],
                output_type="Score 0-26 with 10-year diabetes risk",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.ENDOCRINOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.FAMILY_MEDICINE,
                ),
                conditions=(
                    "Type 2 Diabetes",
                    "Diabetes Mellitus",
                    "Prediabetes",
                    "Metabolic Syndrome",
                ),
                clinical_contexts=(
                    ClinicalContext.SCREENING,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "What is this patient's diabetes risk?",
                    "Should this patient be screened for diabetes?",
                    "Calculate FINDRISC score",
                    "10-year diabetes risk",
                ),
                keywords=(
                    "FINDRISC",
                    "diabetes risk",
                    "type 2 diabetes screening",
                    "prediabetes risk",
                    "diabetes prevention",
                ),
            ),
            references=(
                Reference(
                    citation="Lindström J, Tuomilehto J. The diabetes risk score: a practical tool to predict type 2 diabetes risk. Diabetes Care. 2003;26(3):725-731.",
                    pmid="12610029",
                    doi="10.2337/diacare.26.3.725",
                    year=2003,
                ),
                Reference(
                    citation="Schwarz PE, Li J, Lindström J, Tuomilehto J. Tools for predicting the risk of type 2 diabetes in daily practice. Horm Metab Res. 2009;41(2):86-97.",
                    pmid="19021089",
                    doi="10.1055/s-0028-1087202",
                    year=2009,
                ),
            ),
        )

    def calculate(self, **params) -> ScoreResult:
        """
        Calculate FINDRISC score.

        Args:
            age: Age in years
            bmi: Body mass index (kg/m²)
            waist_circumference: Waist circumference in cm
            physical_activity: Daily physical activity ≥30 min (True/False)
            daily_vegetables: Daily fruits/vegetables/berries (True/False)
            antihypertensive: Taking blood pressure medication (True/False)
            history_high_glucose: Ever had high blood glucose (True/False)
            family_history_diabetes: Family history of diabetes ("none", "second_degree", "first_degree")
            sex: "male" or "female"

        Returns:
            ScoreResult with FINDRISC score and 10-year risk
        """
        # Extract parameters
        age = int(params.get("age", 0))
        bmi = float(params.get("bmi", 0))
        waist = float(params.get("waist_circumference", 0))
        physical_activity = bool(params.get("physical_activity", False))
        daily_vegetables = bool(params.get("daily_vegetables", False))
        antihypertensive = bool(params.get("antihypertensive", False))
        history_high_glucose = bool(params.get("history_high_glucose", False))
        family_history = str(params.get("family_history_diabetes", "none")).lower()
        sex = str(params.get("sex", "male")).lower()

        # Validation
        if not 18 <= age <= 100:
            raise ValueError("age must be 18-100")
        if not 15 <= bmi <= 60:
            raise ValueError("bmi must be 15-60")
        if not 50 <= waist <= 200:
            raise ValueError("waist_circumference must be 50-200 cm")
        if family_history not in ["none", "second_degree", "first_degree"]:
            raise ValueError("family_history_diabetes must be 'none', 'second_degree', or 'first_degree'")
        if sex not in ["male", "female"]:
            raise ValueError("sex must be 'male' or 'female'")

        score = 0
        details = {}

        # Age scoring
        if age < 45:
            age_points = 0
        elif age < 55:
            age_points = 2
        elif age < 65:
            age_points = 3
        else:
            age_points = 4
        score += age_points
        details["age_points"] = age_points

        # BMI scoring
        if bmi < 25:
            bmi_points = 0
        elif bmi < 30:
            bmi_points = 1
        else:
            bmi_points = 3
        score += bmi_points
        details["bmi_points"] = bmi_points

        # Waist circumference scoring (sex-specific)
        if sex == "male":
            if waist < 94:
                waist_points = 0
            elif waist < 102:
                waist_points = 3
            else:
                waist_points = 4
        else:  # female
            if waist < 80:
                waist_points = 0
            elif waist < 88:
                waist_points = 3
            else:
                waist_points = 4
        score += waist_points
        details["waist_points"] = waist_points

        # Physical activity scoring
        activity_points = 0 if physical_activity else 2
        score += activity_points
        details["activity_points"] = activity_points

        # Daily vegetables scoring
        vegetable_points = 0 if daily_vegetables else 1
        score += vegetable_points
        details["vegetable_points"] = vegetable_points

        # Antihypertensive medication scoring
        bp_med_points = 2 if antihypertensive else 0
        score += bp_med_points
        details["bp_medication_points"] = bp_med_points

        # History of high blood glucose scoring
        glucose_history_points = 5 if history_high_glucose else 0
        score += glucose_history_points
        details["glucose_history_points"] = glucose_history_points

        # Family history scoring
        if family_history == "none":
            family_points = 0
        elif family_history == "second_degree":
            family_points = 3
        else:  # first_degree
            family_points = 5
        score += family_points
        details["family_history_points"] = family_points

        # Determine risk category and 10-year risk
        if score < 7:
            severity = Severity.NORMAL
            risk_text = "Low risk"
            risk_percent = "~1%"
            stage = "Low"
        elif score < 12:
            severity = Severity.MILD
            risk_text = "Slightly elevated risk"
            risk_percent = "~4%"
            stage = "Slightly elevated"
        elif score < 15:
            severity = Severity.MODERATE
            risk_text = "Moderate risk"
            risk_percent = "~17%"
            stage = "Moderate"
        elif score < 21:
            severity = Severity.SEVERE
            risk_text = "High risk"
            risk_percent = "~33%"
            stage = "High"
        else:
            severity = Severity.CRITICAL
            risk_text = "Very high risk"
            risk_percent = "~50%"
            stage = "Very high"

        # Recommendations
        recommendations = []
        if score < 7:
            recommendations.append("Continue healthy lifestyle")
            recommendations.append("Rescreen in 5 years")
        elif score < 12:
            recommendations.append("Lifestyle modification recommended")
            recommendations.append("Increase physical activity")
            recommendations.append("Consider diabetes screening with HbA1c or OGTT")
        elif score < 15:
            recommendations.append("Formal diabetes screening recommended")
            recommendations.append("Consider diabetes prevention program")
            recommendations.append("Lifestyle intervention important")
        else:
            recommendations.append("High risk - formal diabetes testing required")
            recommendations.append("Refer to diabetes prevention program")
            recommendations.append("Consider pharmacological prevention (metformin)")

        warnings = []
        if history_high_glucose:
            warnings.append("History of hyperglycemia - higher risk of progression")
        if score >= 15:
            warnings.append("Very high 10-year diabetes risk - intervention required")

        next_steps = [
            "Order fasting glucose or HbA1c" if score >= 7 else "Maintain healthy lifestyle",
            "OGTT if HbA1c 5.7-6.4% (prediabetes range)",
            "Annual rescreening if moderate-to-high risk",
        ]

        return ScoreResult(
            value=score,
            unit=Unit.SCORE,
            interpretation=Interpretation(
                summary=f"FINDRISC = {score}: {risk_text} ({risk_percent} 10-year risk)",
                detail=(
                    f"FINDRISC score of {score}/26 indicates {risk_text.lower()} with approximately "
                    f"{risk_percent} probability of developing type 2 diabetes within 10 years. "
                    f"Score components: Age {age_points}, BMI {bmi_points}, Waist {waist_points}, "
                    f"Activity {activity_points}, Diet {vegetable_points}, BP meds {bp_med_points}, "
                    f"Glucose history {glucose_history_points}, Family {family_points}."
                ),
                severity=severity,
                stage=stage,
                stage_description=f"{risk_text} ({risk_percent} 10-year risk)",
                recommendations=recommendations,
                warnings=warnings,
                next_steps=next_steps,
            ),
            references=self.metadata.references,
            tool_id=self.metadata.low_level.tool_id,
            tool_name=self.metadata.low_level.name,
            raw_inputs=params,
            calculation_details={
                "total_score": score,
                "ten_year_risk_percent": risk_percent,
                "risk_category": stage,
                **details,
            },
        )
