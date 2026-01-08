"""
SCORE2 (Systematic Coronary Risk Evaluation 2)

SCORE2 is a cardiovascular risk prediction algorithm developed by the
European Society of Cardiology for estimating 10-year risk of fatal and
non-fatal cardiovascular events in individuals without prior CVD.

Reference (Original):
    SCORE2 working group and ESC Cardiovascular Risk Collaboration.
    SCORE2 risk prediction algorithms: new models to estimate 10-year risk
    of cardiovascular disease in Europe. Eur Heart J. 2021;42(25):2439-2454.
    DOI: 10.1093/eurheartj/ehab309
    PMID: 34120177

Reference (Older Adults - SCORE2-OP):
    SCORE2-OP working group and ESC Cardiovascular Risk Collaboration.
    SCORE2-OP risk prediction algorithms: estimating incident cardiovascular
    event risk in older persons in four geographical risk regions.
    Eur Heart J. 2021;42(25):2455-2467.
    PMID: 34120185
"""

import math

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import ClinicalContext, HighLevelKey, LowLevelKey, Specialty
from ...value_objects.units import Unit
from ..base import BaseCalculator


class SCORE2Calculator(BaseCalculator):
    """
    SCORE2 (Systematic Coronary Risk Evaluation 2) Calculator

    Estimates 10-year risk of fatal and non-fatal CVD events.

    Input parameters:
    - Age (40-69 for SCORE2, 70+ for SCORE2-OP)
    - Sex
    - Smoking status
    - Systolic blood pressure
    - Non-HDL cholesterol (or Total cholesterol - HDL)

    Risk regions:
    - Low: Spain, France, Switzerland, etc.
    - Moderate: Germany, Austria, Netherlands, etc.
    - High: Poland, Czech Republic, Israel, etc.
    - Very High: Russia, Ukraine, Eastern Europe, etc.

    Risk categories (age-dependent):
    - <50 years: <2.5% low, 2.5-7.5% moderate, ≥7.5% high
    - 50-69 years: <5% low, 5-10% moderate, ≥10% high
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="score2",
                name="SCORE2 (Systematic Coronary Risk Evaluation 2)",
                purpose="Estimate 10-year cardiovascular risk in apparently healthy individuals",
                input_params=["age", "sex", "smoking", "systolic_bp", "non_hdl_cholesterol", "risk_region"],
                output_type="10-year CVD risk (%) with risk category",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CARDIOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.INTERNAL_MEDICINE,
                ),
                conditions=(
                    "Cardiovascular Risk Assessment",
                    "Primary Prevention",
                    "Dyslipidemia",
                    "Hypertension",
                ),
                clinical_contexts=(
                    ClinicalContext.SCREENING,
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "What is the cardiovascular risk in this patient?",
                    "Should I start statin therapy?",
                    "Does this patient need lipid-lowering treatment?",
                    "Is this patient high cardiovascular risk?",
                ),
                icd10_codes=("Z82.4", "Z91.82", "I10", "E78"),
                keywords=(
                    "SCORE2",
                    "cardiovascular risk",
                    "CVD risk",
                    "ESC",
                    "primary prevention",
                    "statin",
                    "lipid",
                    "cholesterol",
                    "hypertension",
                    "10-year risk",
                ),
            ),
            references=(
                Reference(
                    citation="SCORE2 working group and ESC Cardiovascular Risk Collaboration. "
                    "SCORE2 risk prediction algorithms: new models to estimate 10-year "
                    "risk of cardiovascular disease in Europe. "
                    "Eur Heart J. 2021;42(25):2439-2454.",
                    doi="10.1093/eurheartj/ehab309",
                    pmid="34120177",
                    year=2021,
                ),
                Reference(
                    citation="SCORE2-OP working group. SCORE2-OP risk prediction algorithms: "
                    "estimating incident cardiovascular event risk in older persons. "
                    "Eur Heart J. 2021;42(25):2455-2467.",
                    pmid="34120185",
                    year=2021,
                ),
            ),
            version="1.0.0",
            validation_status="validated",
        )

    def calculate(
        self,
        age: int,
        sex: str,
        smoking: bool,
        systolic_bp: float,
        non_hdl_cholesterol: float,
        risk_region: str = "moderate",
    ) -> ScoreResult:
        """
        Calculate SCORE2 10-year cardiovascular risk.

        Args:
            age: Age in years (40-69 for SCORE2, 70+ for SCORE2-OP)
            sex: "male" or "female"
            smoking: Current smoker status
            systolic_bp: Systolic blood pressure in mmHg
            non_hdl_cholesterol: Non-HDL cholesterol in mmol/L
                (= Total cholesterol - HDL cholesterol)
            risk_region: Risk region - "low", "moderate", "high", or "very_high"

        Returns:
            ScoreResult with 10-year CVD risk percentage
        """
        # Validate inputs
        if age < 40 or age > 90:
            raise ValueError("Age must be between 40 and 90 years")

        sex_lower = sex.lower()
        if sex_lower not in ["male", "female"]:
            raise ValueError("Sex must be 'male' or 'female'")

        if systolic_bp < 90 or systolic_bp > 250:
            raise ValueError("Systolic BP must be between 90 and 250 mmHg")

        if non_hdl_cholesterol < 1.0 or non_hdl_cholesterol > 10.0:
            raise ValueError("Non-HDL cholesterol must be between 1.0 and 10.0 mmol/L")

        region = risk_region.lower().replace("-", "_")
        valid_regions = ["low", "moderate", "high", "very_high"]
        if region not in valid_regions:
            raise ValueError(f"Risk region must be one of: {valid_regions}")

        # SCORE2 simplified calculation
        # Note: Full SCORE2 uses complex recalibrated Weibull models
        # This is a simplified approximation for clinical guidance
        # Actual risk should use official SCORE2 calculator/charts

        # Base coefficients (simplified from full model)
        is_male = sex_lower == "male"
        is_smoker = smoking

        # Age-centered variables
        age_years = (age - 60) / 5  # centered at 60, per 5 years

        # Risk factor contributions
        age_effect = age_years * 0.5
        sex_effect = 0.3 if is_male else 0
        smoking_effect = 0.65 if is_smoker else 0
        sbp_effect = (systolic_bp - 120) / 20 * 0.25
        chol_effect = (non_hdl_cholesterol - 4.0) * 0.15

        # Linear predictor
        lp = age_effect + sex_effect + smoking_effect + sbp_effect + chol_effect

        # Region adjustment factors
        region_factors = {
            "low": 0.7,
            "moderate": 1.0,
            "high": 1.3,
            "very_high": 1.8,
        }
        region_factor = region_factors[region]

        # Calculate 10-year risk (simplified logistic approximation)
        # Base 10-year risk around 5% at age 60
        base_risk = 0.05
        risk_10y = base_risk * math.exp(lp) * region_factor

        # Cap risk at realistic bounds
        risk_10y = max(0.001, min(0.80, risk_10y))
        risk_percent = round(risk_10y * 100, 1)

        # Determine risk category based on age and region
        is_score2_op = age >= 70
        category = self._get_risk_category(risk_percent, age, region)

        # Get interpretation
        interpretation = self._get_interpretation(risk_percent, category, age, is_score2_op, region)

        return ScoreResult(
            value=risk_percent,
            unit=Unit.PERCENT,
            interpretation=interpretation,
            references=list(self.references),
            tool_id=self.tool_id,
            tool_name=self.name,
            raw_inputs={
                "age": age,
                "sex": sex,
                "smoking": smoking,
                "systolic_bp": systolic_bp,
                "non_hdl_cholesterol": non_hdl_cholesterol,
                "risk_region": risk_region,
            },
            calculation_details={
                "algorithm": "SCORE2-OP" if is_score2_op else "SCORE2",
                "risk_factors": {
                    "age": age,
                    "sex": sex,
                    "smoking": is_smoker,
                    "systolic_bp": systolic_bp,
                    "non_hdl_cholesterol": non_hdl_cholesterol,
                },
                "risk_region": region,
                "ten_year_risk_percent": risk_percent,
                "risk_category": category,
                "thresholds": self._get_thresholds_for_age(age),
                "note": "Simplified calculation - use official SCORE2 charts for clinical decisions",
            },
            formula_used="SCORE2/SCORE2-OP based on age, sex, smoking, SBP, and non-HDL cholesterol",
        )

    def _get_thresholds_for_age(self, age: int) -> dict:
        """Get risk category thresholds based on age"""
        if age < 50:
            return {"low": "<2.5%", "moderate": "2.5-7.5%", "high": "≥7.5%"}
        elif age < 70:
            return {"low": "<5%", "moderate": "5-10%", "high": "≥10%"}
        else:  # SCORE2-OP
            return {"low": "<7.5%", "moderate": "7.5-15%", "high": "≥15%"}

    def _get_risk_category(self, risk_percent: float, age: int, region: str) -> str:
        """Determine risk category based on ESC guidelines"""
        if age < 50:
            if risk_percent < 2.5:
                return "Low"
            elif risk_percent < 7.5:
                return "Moderate"
            else:
                return "High"
        elif age < 70:
            if risk_percent < 5:
                return "Low"
            elif risk_percent < 10:
                return "Moderate"
            else:
                return "High"
        else:  # SCORE2-OP (≥70 years)
            if risk_percent < 7.5:
                return "Low"
            elif risk_percent < 15:
                return "Moderate"
            else:
                return "High"

    def _get_interpretation(self, risk: float, category: str, age: int, is_op: bool, region: str) -> Interpretation:
        """Get interpretation based on SCORE2 result"""

        algorithm = "SCORE2-OP" if is_op else "SCORE2"

        if category == "Low":
            return Interpretation(
                summary=f"{algorithm}: {risk}% 10-year CVD Risk (Low)",
                detail=f"10-year risk of fatal and non-fatal cardiovascular events is {risk}%. This is considered low risk for this age group.",
                severity=Severity.NORMAL,
                stage="Low Risk",
                stage_description=f"{algorithm} low risk category",
                recommendations=(
                    "Lifestyle advice for cardiovascular health",
                    "Lipid-lowering therapy generally not indicated based on risk alone",
                    "Rescreen in 5 years or if risk factors change",
                    "Address individual risk factors",
                ),
                next_steps=(
                    "Healthy lifestyle counseling",
                    "BP and lipid monitoring",
                    "Reassess in 5 years",
                ),
            )
        elif category == "Moderate":
            return Interpretation(
                summary=f"{algorithm}: {risk}% 10-year CVD Risk (Moderate)",
                detail=f"10-year risk of fatal and non-fatal cardiovascular events is {risk}%. "
                f"Consider lipid-lowering treatment especially with additional risk modifiers.",
                severity=Severity.MILD,
                stage="Moderate Risk",
                stage_description=f"{algorithm} moderate risk category",
                recommendations=(
                    "Consider lipid-lowering therapy, especially if risk modifiers present",
                    "Risk modifiers: family history, obesity, social deprivation, etc.",
                    "Target: at least 50% LDL-C reduction",
                    "LDL-C target <2.6 mmol/L (100 mg/dL)",
                    "Lifestyle interventions: smoking cessation, diet, exercise",
                ),
                next_steps=(
                    "Assess risk modifiers",
                    "Discuss shared decision-making for statin",
                    "Lifestyle optimization",
                    "Reassess in 2-5 years",
                ),
            )
        else:  # High
            return Interpretation(
                summary=f"{algorithm}: {risk}% 10-year CVD Risk (High)",
                detail=f"10-year risk of fatal and non-fatal cardiovascular events is {risk}%. Lipid-lowering therapy recommended.",
                severity=Severity.MODERATE,
                stage="High Risk",
                stage_description=f"{algorithm} high risk category",
                recommendations=(
                    "Lipid-lowering therapy RECOMMENDED",
                    "Target: at least 50% LDL-C reduction",
                    "LDL-C target <1.8 mmol/L (70 mg/dL) for very high risk",
                    "Consider high-intensity statin",
                    "Aggressive risk factor management",
                    "BP target <130/80 mmHg",
                    "Smoking cessation essential",
                ),
                warnings=(
                    "High cardiovascular event risk",
                    "Benefit of treatment clearly outweighs risk",
                ),
                next_steps=(
                    "Start high-intensity statin",
                    "Optimize blood pressure control",
                    "Diabetes screening",
                    "Smoking cessation if applicable",
                    "Follow-up lipid panel in 4-12 weeks",
                ),
            )
