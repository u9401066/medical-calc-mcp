"""
Framingham Risk Score Calculator

Estimates 10-year risk of developing coronary heart disease (CHD)
based on traditional cardiovascular risk factors.

Original Reference:
    Wilson PW, D'Agostino RB, Levy D, Belanger AM, Silbershatz H, Kannel WB.
    Prediction of coronary heart disease using risk factor categories.
    Circulation. 1998;97(18):1837-1847.
    doi:10.1161/01.cir.97.18.1837. PMID: 9603539.

Updated General CVD Risk Profile:
    D'Agostino RB Sr, Vasan RS, Pencina MJ, et al.
    General cardiovascular risk profile for use in primary care:
    the Framingham Heart Study.
    Circulation. 2008;117(6):743-753.
    doi:10.1161/CIRCULATIONAHA.107.699579. PMID: 18212285.

ATP III Update:
    National Cholesterol Education Program (NCEP) Expert Panel.
    Third Report of the National Cholesterol Education Program Expert Panel
    on Detection, Evaluation, and Treatment of High Blood Cholesterol
    in Adults (Adult Treatment Panel III).
    Circulation. 2002;106(25):3143-3421. PMID: 12485966.
"""

from typing import Literal

from ...entities.score_result import ScoreResult
from ...entities.tool_metadata import ToolMetadata
from ...value_objects.interpretation import Interpretation, RiskLevel, Severity
from ...value_objects.reference import Reference
from ...value_objects.tool_keys import (
    ClinicalContext,
    HighLevelKey,
    LowLevelKey,
    Specialty,
)
from ...value_objects.units import Unit
from ..base import BaseCalculator

# Age points for men (Wilson 1998, ATP III)
AGE_POINTS_MEN: dict[str, int] = {
    "20-34": -9,
    "35-39": -4,
    "40-44": 0,
    "45-49": 3,
    "50-54": 6,
    "55-59": 8,
    "60-64": 10,
    "65-69": 11,
    "70-74": 12,
    "75-79": 13,
}

# Age points for women (Wilson 1998, ATP III)
AGE_POINTS_WOMEN: dict[str, int] = {
    "20-34": -7,
    "35-39": -3,
    "40-44": 0,
    "45-49": 3,
    "50-54": 6,
    "55-59": 8,
    "60-64": 10,
    "65-69": 12,
    "70-74": 14,
    "75-79": 16,
}

# Total cholesterol points for men by age group
TC_POINTS_MEN: dict[str, dict[str, int]] = {
    "20-39": {"<160": 0, "160-199": 4, "200-239": 7, "240-279": 9, ">=280": 11},
    "40-49": {"<160": 0, "160-199": 3, "200-239": 5, "240-279": 6, ">=280": 8},
    "50-59": {"<160": 0, "160-199": 2, "200-239": 3, "240-279": 4, ">=280": 5},
    "60-69": {"<160": 0, "160-199": 1, "200-239": 1, "240-279": 2, ">=280": 3},
    "70-79": {"<160": 0, "160-199": 0, "200-239": 0, "240-279": 1, ">=280": 1},
}

# Total cholesterol points for women by age group
TC_POINTS_WOMEN: dict[str, dict[str, int]] = {
    "20-39": {"<160": 0, "160-199": 4, "200-239": 8, "240-279": 11, ">=280": 13},
    "40-49": {"<160": 0, "160-199": 3, "200-239": 6, "240-279": 8, ">=280": 10},
    "50-59": {"<160": 0, "160-199": 2, "200-239": 4, "240-279": 5, ">=280": 7},
    "60-69": {"<160": 0, "160-199": 1, "200-239": 2, "240-279": 3, ">=280": 4},
    "70-79": {"<160": 0, "160-199": 1, "200-239": 1, "240-279": 2, ">=280": 2},
}

# Smoking points for men by age group
SMOKING_POINTS_MEN: dict[str, int] = {
    "20-39": 8,
    "40-49": 5,
    "50-59": 3,
    "60-69": 1,
    "70-79": 1,
}

# Smoking points for women by age group
SMOKING_POINTS_WOMEN: dict[str, int] = {
    "20-39": 9,
    "40-49": 7,
    "50-59": 4,
    "60-69": 2,
    "70-79": 1,
}

# HDL cholesterol points (same for both sexes)
HDL_POINTS: dict[str, int] = {
    ">=60": -1,
    "50-59": 0,
    "40-49": 1,
    "<40": 2,
}

# Systolic BP points for men (treated vs untreated)
SBP_POINTS_MEN: dict[str, dict[str, int]] = {
    "untreated": {"<120": 0, "120-129": 0, "130-139": 1, "140-159": 1, ">=160": 2},
    "treated": {"<120": 0, "120-129": 1, "130-139": 2, "140-159": 2, ">=160": 3},
}

# Systolic BP points for women (treated vs untreated)
SBP_POINTS_WOMEN: dict[str, dict[str, int]] = {
    "untreated": {"<120": 0, "120-129": 1, "130-139": 2, "140-159": 3, ">=160": 4},
    "treated": {"<120": 0, "120-129": 3, "130-139": 4, "140-159": 5, ">=160": 6},
}

# Point total to 10-year CHD risk % for men
RISK_TABLE_MEN: dict[int, str] = {
    -1: "<1%",
    0: "1%",
    1: "1%",
    2: "1%",
    3: "1%",
    4: "1%",
    5: "2%",
    6: "2%",
    7: "3%",
    8: "4%",
    9: "5%",
    10: "6%",
    11: "8%",
    12: "10%",
    13: "12%",
    14: "16%",
    15: "20%",
    16: "25%",
    17: ">=30%",
}

# Point total to 10-year CHD risk % for women
RISK_TABLE_WOMEN: dict[int, str] = {
    -1: "<1%",
    0: "<1%",
    1: "1%",
    2: "1%",
    3: "1%",
    4: "1%",
    5: "1%",
    6: "1%",
    7: "1%",
    8: "1%",
    9: "1%",
    10: "1%",
    11: "1%",
    12: "1%",
    13: "2%",
    14: "2%",
    15: "3%",
    16: "4%",
    17: "5%",
    18: "6%",
    19: "8%",
    20: "11%",
    21: "14%",
    22: "17%",
    23: "22%",
    24: "27%",
    25: ">=30%",
}


class FraminghamRiskScoreCalculator(BaseCalculator):
    """
    Framingham Risk Score Calculator

    Estimates the 10-year risk of developing coronary heart disease (CHD)
    using traditional cardiovascular risk factors.

    Parameters:
        - Age (30-79 years)
        - Sex (male/female)
        - Total cholesterol (mg/dL)
        - HDL cholesterol (mg/dL)
        - Systolic blood pressure (mmHg)
        - Treatment for hypertension (yes/no)
        - Current smoking status (yes/no)

    Risk Categories (ATP III):
        - <10%: Low risk (0-1 risk factors)
        - 10-20%: Intermediate risk (2+ risk factors)
        - >20%: High risk (CHD equivalent)

    Note:
        Diabetes is considered a CHD risk equivalent and automatically
        places patients in the high-risk category (>20%).
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            low_level=LowLevelKey(
                tool_id="framingham_risk_score",
                name="Framingham Risk Score",
                purpose="Estimate 10-year risk of coronary heart disease",
                input_params=[
                    "age",
                    "sex",
                    "total_cholesterol",
                    "hdl_cholesterol",
                    "systolic_bp",
                    "bp_treated",
                    "smoker",
                    "diabetic",
                ],
                output_type="10-year CHD risk percentage with risk category",
            ),
            high_level=HighLevelKey(
                specialties=(
                    Specialty.CARDIOLOGY,
                    Specialty.INTERNAL_MEDICINE,
                    Specialty.FAMILY_MEDICINE,
                ),
                conditions=(
                    "coronary heart disease",
                    "cardiovascular disease",
                    "atherosclerosis",
                    "coronary artery disease",
                    "myocardial infarction",
                    "heart disease",
                    "hyperlipidemia",
                    "hypertension",
                ),
                clinical_contexts=(
                    ClinicalContext.RISK_STRATIFICATION,
                    ClinicalContext.SCREENING,
                    ClinicalContext.PROGNOSIS,
                    ClinicalContext.TREATMENT_DECISION,
                ),
                clinical_questions=(
                    "What is this patient's cardiac risk?",
                    "Should this patient be on statin therapy?",
                    "What is the 10-year heart disease risk?",
                    "Does this patient need aggressive lipid management?",
                    "How do I calculate cardiovascular risk?",
                ),
                icd10_codes=(
                    "I25.10",  # Atherosclerotic heart disease
                    "I25.9",  # Chronic ischemic heart disease, unspecified
                    "E78.00",  # Pure hypercholesterolemia, unspecified
                    "I10",  # Essential hypertension
                    "Z72.0",  # Tobacco use
                ),
                keywords=(
                    "Framingham",
                    "Framingham Risk Score",
                    "FRS",
                    "coronary risk",
                    "cardiac risk",
                    "CVD risk",
                    "cardiovascular risk",
                    "heart disease risk",
                    "10-year risk",
                    "ATP III",
                    "lipid management",
                    "statin therapy",
                ),
            ),
            references=(
                Reference(
                    citation="Wilson PW, D'Agostino RB, Levy D, Belanger AM, "
                    "Silbershatz H, Kannel WB. Prediction of coronary heart disease "
                    "using risk factor categories. Circulation. 1998;97(18):1837-1847.",
                    doi="10.1161/01.cir.97.18.1837",
                    pmid="9603539",
                    year=1998,
                ),
                Reference(
                    citation="D'Agostino RB Sr, Vasan RS, Pencina MJ, et al. "
                    "General cardiovascular risk profile for use in primary care: "
                    "the Framingham Heart Study. Circulation. 2008;117(6):743-753.",
                    doi="10.1161/CIRCULATIONAHA.107.699579",
                    pmid="18212285",
                    year=2008,
                ),
                Reference(
                    citation="National Cholesterol Education Program (NCEP) Expert Panel. "
                    "Third Report on Detection, Evaluation, and Treatment of High Blood "
                    "Cholesterol in Adults (Adult Treatment Panel III). "
                    "Circulation. 2002;106(25):3143-3421.",
                    doi="10.1161/circ.106.25.3143",
                    pmid="12485966",
                    year=2002,
                ),
            ),
            version="ATP III/Wilson 1998",
            validation_status="guideline-recommended",
        )

    def calculate(
        self,
        age: int,
        sex: Literal["male", "female"],
        total_cholesterol: float,
        hdl_cholesterol: float,
        systolic_bp: int,
        bp_treated: bool = False,
        smoker: bool = False,
        diabetic: bool = False,
    ) -> ScoreResult:
        """
        Calculate Framingham Risk Score.

        Args:
            age: Patient age in years (30-79)
            sex: Patient sex ("male" or "female")
            total_cholesterol: Total cholesterol in mg/dL
            hdl_cholesterol: HDL cholesterol in mg/dL
            systolic_bp: Systolic blood pressure in mmHg
            bp_treated: Currently on blood pressure treatment?
            smoker: Current smoker?
            diabetic: Has diabetes? (CHD risk equivalent)

        Returns:
            ScoreResult with point total, 10-year CHD risk %, and recommendations

        Raises:
            ValueError: If age or other parameters are out of valid range
        """
        # Validate inputs
        if age < 20 or age > 79:
            raise ValueError("Age must be between 20 and 79 years")
        if total_cholesterol <= 0:
            raise ValueError("Total cholesterol must be positive")
        if hdl_cholesterol <= 0:
            raise ValueError("HDL cholesterol must be positive")
        if systolic_bp <= 0:
            raise ValueError("Systolic blood pressure must be positive")

        # Calculate points
        point_breakdown = self._calculate_points(
            age=age,
            sex=sex,
            total_cholesterol=total_cholesterol,
            hdl_cholesterol=hdl_cholesterol,
            systolic_bp=systolic_bp,
            bp_treated=bp_treated,
            smoker=smoker,
        )

        total_points = point_breakdown["total"]

        # Get risk percentage
        risk_percent, risk_numeric = self._get_risk(total_points, sex)

        # Diabetes overrides to high risk
        if diabetic:
            risk_percent = ">20% (diabetes = CHD equivalent)"
            risk_numeric = 25.0  # Assign high risk value

        # Generate interpretation
        interpretation = self._interpret_risk(
            risk_numeric, diabetic, smoker, bp_treated, total_cholesterol, hdl_cholesterol
        )

        # Build calculation details
        calculation_details: dict[str, object] = {
            "age_group": point_breakdown["age_group"],
            "point_breakdown": point_breakdown,
            "total_points": total_points,
            "risk_percentage": risk_percent,
            "risk_numeric": risk_numeric,
            "diabetes_status": "CHD risk equivalent" if diabetic else "No diabetes",
            "parameters": {
                "age": age,
                "sex": sex,
                "total_cholesterol_mg_dl": total_cholesterol,
                "hdl_cholesterol_mg_dl": hdl_cholesterol,
                "systolic_bp_mmhg": systolic_bp,
                "bp_treated": bp_treated,
                "smoker": smoker,
                "diabetic": diabetic,
            },
        }

        return ScoreResult(
            tool_name=self.low_level_key.name,
            tool_id=self.low_level_key.tool_id,
            value=risk_numeric,
            unit=Unit.PERCENT,
            interpretation=interpretation,
            calculation_details=calculation_details,
            references=list(self.references),
            formula_used="Framingham point system (ATP III/Wilson 1998)",
        )

    def _get_age_group(self, age: int) -> str:
        """Determine age group for point lookup."""
        if age < 35:
            return "20-34"
        elif age < 40:
            return "35-39"
        elif age < 45:
            return "40-44"
        elif age < 50:
            return "45-49"
        elif age < 55:
            return "50-54"
        elif age < 60:
            return "55-59"
        elif age < 65:
            return "60-64"
        elif age < 70:
            return "65-69"
        elif age < 75:
            return "70-74"
        else:
            return "75-79"

    def _get_cholesterol_age_group(self, age: int) -> str:
        """Get age group for cholesterol/smoking tables."""
        if age < 40:
            return "20-39"
        elif age < 50:
            return "40-49"
        elif age < 60:
            return "50-59"
        elif age < 70:
            return "60-69"
        else:
            return "70-79"

    def _get_tc_category(self, tc: float) -> str:
        """Get total cholesterol category."""
        if tc < 160:
            return "<160"
        elif tc < 200:
            return "160-199"
        elif tc < 240:
            return "200-239"
        elif tc < 280:
            return "240-279"
        else:
            return ">=280"

    def _get_hdl_category(self, hdl: float) -> str:
        """Get HDL cholesterol category."""
        if hdl >= 60:
            return ">=60"
        elif hdl >= 50:
            return "50-59"
        elif hdl >= 40:
            return "40-49"
        else:
            return "<40"

    def _get_sbp_category(self, sbp: int) -> str:
        """Get systolic BP category."""
        if sbp < 120:
            return "<120"
        elif sbp < 130:
            return "120-129"
        elif sbp < 140:
            return "130-139"
        elif sbp < 160:
            return "140-159"
        else:
            return ">=160"

    def _calculate_points(
        self,
        age: int,
        sex: Literal["male", "female"],
        total_cholesterol: float,
        hdl_cholesterol: float,
        systolic_bp: int,
        bp_treated: bool,
        smoker: bool,
    ) -> dict[str, int | str]:
        """Calculate individual point components."""
        age_group = self._get_age_group(age)
        chol_age_group = self._get_cholesterol_age_group(age)
        tc_category = self._get_tc_category(total_cholesterol)
        hdl_category = self._get_hdl_category(hdl_cholesterol)
        sbp_category = self._get_sbp_category(systolic_bp)
        bp_status = "treated" if bp_treated else "untreated"

        if sex == "male":
            age_points = AGE_POINTS_MEN.get(age_group, 0)
            tc_points = TC_POINTS_MEN.get(chol_age_group, {}).get(tc_category, 0)
            smoking_points = SMOKING_POINTS_MEN.get(chol_age_group, 0) if smoker else 0
            sbp_points = SBP_POINTS_MEN.get(bp_status, {}).get(sbp_category, 0)
        else:
            age_points = AGE_POINTS_WOMEN.get(age_group, 0)
            tc_points = TC_POINTS_WOMEN.get(chol_age_group, {}).get(tc_category, 0)
            smoking_points = SMOKING_POINTS_WOMEN.get(chol_age_group, 0) if smoker else 0
            sbp_points = SBP_POINTS_WOMEN.get(bp_status, {}).get(sbp_category, 0)

        hdl_points = HDL_POINTS.get(hdl_category, 0)

        total = age_points + tc_points + hdl_points + sbp_points + smoking_points

        return {
            "age_group": age_group,
            "age_points": age_points,
            "tc_points": tc_points,
            "hdl_points": hdl_points,
            "sbp_points": sbp_points,
            "smoking_points": smoking_points,
            "total": total,
        }

    def _get_risk(
        self, total_points: int, sex: Literal["male", "female"]
    ) -> tuple[str, float]:
        """
        Convert point total to 10-year risk percentage.

        Returns:
            Tuple of (risk string, numeric risk value)
        """
        if sex == "male":
            risk_table = RISK_TABLE_MEN
            min_points = -1
            max_points = 17
        else:
            risk_table = RISK_TABLE_WOMEN
            min_points = -1
            max_points = 25

        # Clamp points to table range
        if total_points < min_points:
            total_points = min_points
        elif total_points > max_points:
            total_points = max_points

        risk_str = risk_table.get(total_points, ">=30%")

        # Convert to numeric
        if risk_str == "<1%":
            risk_numeric = 0.5
        elif risk_str == ">=30%":
            risk_numeric = 30.0
        else:
            risk_numeric = float(risk_str.replace("%", ""))

        return risk_str, risk_numeric

    def _interpret_risk(
        self,
        risk_numeric: float,
        diabetic: bool,
        smoker: bool,
        bp_treated: bool,
        total_cholesterol: float,
        hdl_cholesterol: float,
    ) -> Interpretation:
        """Generate clinical interpretation based on risk level."""

        # Determine risk category
        if diabetic or risk_numeric > 20:
            risk_category = "High Risk"
            severity = Severity.SEVERE
            risk_level = RiskLevel.HIGH
            ldl_target = "<70 mg/dL (or <100 mg/dL)"
            recommendations = (
                "Lifestyle modification strongly recommended",
                "High-intensity statin therapy indicated",
                "LDL-C target: <70 mg/dL (very high risk) or <100 mg/dL",
                "Consider adding ezetimibe if LDL goal not achieved",
                "Aggressive blood pressure control if hypertensive",
                "Consider aspirin therapy for primary prevention",
            )
            next_steps = (
                "Initiate or intensify statin therapy",
                "Detailed lipid panel including apoB if available",
                "Screen for and treat other CHD risk factors",
                "Consider coronary calcium scoring for further risk stratification",
            )
        elif risk_numeric >= 10:
            risk_category = "Intermediate Risk"
            severity = Severity.MODERATE
            risk_level = RiskLevel.INTERMEDIATE
            ldl_target = "<100 mg/dL"
            recommendations = (
                "Lifestyle modification with dietary changes",
                "Moderate-intensity statin therapy usually indicated",
                "LDL-C target: <100 mg/dL",
                "Blood pressure optimization important",
                "Smoking cessation if applicable",
            )
            next_steps = (
                "Consider statin therapy based on overall risk profile",
                "Repeat risk assessment if borderline",
                "Consider calcium score to clarify risk stratification",
            )
        else:
            risk_category = "Low Risk"
            severity = Severity.MILD
            risk_level = RiskLevel.LOW
            ldl_target = "<130 mg/dL"
            recommendations = (
                "Lifestyle modification as primary intervention",
                "Heart-healthy diet (Mediterranean, DASH)",
                "Regular physical activity (150+ min/week moderate)",
                "Maintain healthy weight",
                "Reassess risk factors periodically",
            )
            next_steps = (
                "Annual cardiovascular risk reassessment",
                "Promote smoking cessation if smoker",
                "Encourage healthy lifestyle behaviors",
            )

        # Generate warnings
        warnings: list[str] = []
        if diabetic:
            warnings.append("Diabetes is a CHD risk equivalent (>20% risk)")
        if smoker:
            warnings.append("Active smoking significantly increases CVD risk")
        if total_cholesterol > 240:
            warnings.append("Elevated total cholesterol (>240 mg/dL)")
        if hdl_cholesterol < 40:
            warnings.append("Low HDL cholesterol (<40 mg/dL) is an independent risk factor")

        detail = (
            f"The 10-year risk of coronary heart disease is approximately "
            f"{risk_numeric:.0f}%. This places the patient in the {risk_category} "
            f"category per ATP III guidelines. LDL-C goal: {ldl_target}."
        )

        return Interpretation(
            summary=f"10-Year CHD Risk: {risk_numeric:.0f}% ({risk_category})",
            detail=detail,
            severity=severity,
            risk_level=risk_level,
            stage=risk_category,
            stage_description=f"10-year CHD risk {risk_numeric:.0f}%",
            recommendations=recommendations,
            next_steps=next_steps,
            warnings=tuple(warnings) if warnings else (),
        )
