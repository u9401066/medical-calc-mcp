"""
Tests for Framingham Risk Score Calculator

References:
    Wilson PW, D'Agostino RB, Levy D, et al.
    Prediction of coronary heart disease using risk factor categories.
    Circulation. 1998;97(18):1837-1847. PMID: 9603539.

    D'Agostino RB Sr, Vasan RS, Pencina MJ, et al.
    General cardiovascular risk profile for use in primary care.
    Circulation. 2008;117(6):743-753. PMID: 18212285.
"""

import pytest

from src.domain.services.calculators.framingham import (
    FraminghamRiskScoreCalculator,
)
from src.domain.value_objects.interpretation import RiskLevel, Severity


@pytest.fixture
def calculator() -> FraminghamRiskScoreCalculator:
    """Provide a Framingham Risk Score calculator instance."""
    return FraminghamRiskScoreCalculator()


class TestFraminghamBasicCalculations:
    """Test basic Framingham score calculations."""

    def test_low_risk_young_male(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Young male with optimal values = low risk."""
        result = calculator.calculate(
            age=35,
            sex="male",
            total_cholesterol=180,  # Optimal
            hdl_cholesterol=55,
            systolic_bp=115,
            bp_treated=False,
            smoker=False,
            diabetic=False,
        )
        assert result.value < 10
        assert "Low" in result.interpretation.stage

    def test_low_risk_young_female(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Young female with optimal values = low risk."""
        result = calculator.calculate(
            age=35,
            sex="female",
            total_cholesterol=180,
            hdl_cholesterol=65,
            systolic_bp=110,
            bp_treated=False,
            smoker=False,
            diabetic=False,
        )
        assert result.value < 10
        assert result.interpretation.risk_level in [RiskLevel.VERY_LOW, RiskLevel.LOW]

    def test_moderate_risk_middle_aged_male(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Middle-aged male with moderate risk factors."""
        result = calculator.calculate(
            age=55,
            sex="male",
            total_cholesterol=220,
            hdl_cholesterol=45,
            systolic_bp=135,
            bp_treated=False,
            smoker=False,
            diabetic=False,
        )
        # Should be in intermediate risk range
        assert 5 <= result.value <= 20

    def test_high_risk_elderly_male_smoker(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Elderly male smoker with high cholesterol = high risk."""
        result = calculator.calculate(
            age=65,
            sex="male",
            total_cholesterol=260,
            hdl_cholesterol=35,
            systolic_bp=150,
            bp_treated=False,
            smoker=True,
            diabetic=False,
        )
        assert result.value >= 15

    def test_diabetic_automatic_high_risk(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Diabetes = CHD risk equivalent (>20% risk)."""
        result = calculator.calculate(
            age=45,
            sex="male",
            total_cholesterol=190,
            hdl_cholesterol=55,
            systolic_bp=120,
            bp_treated=False,
            smoker=False,
            diabetic=True,
        )
        assert result.value >= 20
        assert result.interpretation.risk_level == RiskLevel.HIGH
        assert "CHD risk equivalent" in result.calculation_details["diabetes_status"]


class TestFraminghamMaleCalculations:
    """Test Framingham calculations specific to male patients."""

    def test_male_age_points_young(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Test age points for young male."""
        result = calculator.calculate(
            age=32,
            sex="male",
            total_cholesterol=180,
            hdl_cholesterol=55,
            systolic_bp=115,
        )
        breakdown = result.calculation_details["point_breakdown"]
        assert breakdown["age_points"] == -9  # 20-34 age group for men

    def test_male_age_points_elderly(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Test age points for elderly male."""
        result = calculator.calculate(
            age=72,
            sex="male",
            total_cholesterol=180,
            hdl_cholesterol=55,
            systolic_bp=115,
        )
        breakdown = result.calculation_details["point_breakdown"]
        assert breakdown["age_points"] == 12  # 70-74 age group for men

    def test_male_smoking_points(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Test smoking adds points for male."""
        result_nonsmoker = calculator.calculate(
            age=45,
            sex="male",
            total_cholesterol=200,
            hdl_cholesterol=50,
            systolic_bp=125,
            smoker=False,
        )
        result_smoker = calculator.calculate(
            age=45,
            sex="male",
            total_cholesterol=200,
            hdl_cholesterol=50,
            systolic_bp=125,
            smoker=True,
        )
        nonsmoker_points = result_nonsmoker.calculation_details["point_breakdown"]["smoking_points"]
        smoker_points = result_smoker.calculation_details["point_breakdown"]["smoking_points"]
        assert nonsmoker_points == 0
        assert smoker_points > 0

    def test_male_bp_treatment_effect(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Test BP treatment increases points for male."""
        result_untreated = calculator.calculate(
            age=55,
            sex="male",
            total_cholesterol=200,
            hdl_cholesterol=50,
            systolic_bp=145,
            bp_treated=False,
        )
        result_treated = calculator.calculate(
            age=55,
            sex="male",
            total_cholesterol=200,
            hdl_cholesterol=50,
            systolic_bp=145,
            bp_treated=True,
        )
        untreated_points = result_untreated.calculation_details["point_breakdown"]["sbp_points"]
        treated_points = result_treated.calculation_details["point_breakdown"]["sbp_points"]
        assert treated_points >= untreated_points


class TestFraminghamFemaleCalculations:
    """Test Framingham calculations specific to female patients."""

    def test_female_age_points_young(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Test age points for young female."""
        result = calculator.calculate(
            age=32,
            sex="female",
            total_cholesterol=180,
            hdl_cholesterol=60,
            systolic_bp=115,
        )
        breakdown = result.calculation_details["point_breakdown"]
        assert breakdown["age_points"] == -7  # 20-34 age group for women

    def test_female_age_points_elderly(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Test age points for elderly female."""
        result = calculator.calculate(
            age=76,
            sex="female",
            total_cholesterol=180,
            hdl_cholesterol=60,
            systolic_bp=115,
        )
        breakdown = result.calculation_details["point_breakdown"]
        assert breakdown["age_points"] == 16  # 75-79 age group for women

    def test_female_generally_lower_risk(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Female generally has lower risk than male with same factors."""
        male_result = calculator.calculate(
            age=55,
            sex="male",
            total_cholesterol=220,
            hdl_cholesterol=45,
            systolic_bp=140,
        )
        female_result = calculator.calculate(
            age=55,
            sex="female",
            total_cholesterol=220,
            hdl_cholesterol=45,
            systolic_bp=140,
        )
        # Same risk factors, female typically has lower risk
        assert female_result.value <= male_result.value


class TestFraminghamCholesterol:
    """Test cholesterol component calculations."""

    def test_optimal_tc_zero_points(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Optimal total cholesterol (<160) = 0 points."""
        result = calculator.calculate(
            age=45,
            sex="male",
            total_cholesterol=150,
            hdl_cholesterol=50,
            systolic_bp=120,
        )
        breakdown = result.calculation_details["point_breakdown"]
        assert breakdown["tc_points"] == 0

    def test_high_tc_adds_points(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """High TC (≥280) adds maximum points."""
        result = calculator.calculate(
            age=45,
            sex="male",
            total_cholesterol=300,
            hdl_cholesterol=50,
            systolic_bp=120,
        )
        breakdown = result.calculation_details["point_breakdown"]
        assert breakdown["tc_points"] > 5

    def test_high_hdl_negative_points(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """High HDL (≥60) = -1 point."""
        result = calculator.calculate(
            age=45,
            sex="male",
            total_cholesterol=200,
            hdl_cholesterol=65,
            systolic_bp=120,
        )
        breakdown = result.calculation_details["point_breakdown"]
        assert breakdown["hdl_points"] == -1

    def test_low_hdl_positive_points(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Low HDL (<40) = +2 points."""
        result = calculator.calculate(
            age=45,
            sex="male",
            total_cholesterol=200,
            hdl_cholesterol=35,
            systolic_bp=120,
        )
        breakdown = result.calculation_details["point_breakdown"]
        assert breakdown["hdl_points"] == 2


class TestFraminghamBloodPressure:
    """Test blood pressure component calculations."""

    def test_normal_bp_minimal_points(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Normal BP (<120) = 0 points untreated."""
        result = calculator.calculate(
            age=45,
            sex="male",
            total_cholesterol=200,
            hdl_cholesterol=50,
            systolic_bp=115,
            bp_treated=False,
        )
        breakdown = result.calculation_details["point_breakdown"]
        assert breakdown["sbp_points"] == 0

    def test_high_bp_adds_points(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """High BP (≥160) adds points."""
        result = calculator.calculate(
            age=45,
            sex="male",
            total_cholesterol=200,
            hdl_cholesterol=50,
            systolic_bp=170,
            bp_treated=False,
        )
        breakdown = result.calculation_details["point_breakdown"]
        assert breakdown["sbp_points"] >= 2


class TestFraminghamRiskCategories:
    """Test risk category classification."""

    def test_low_risk_category(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Risk <10% = Low Risk category."""
        result = calculator.calculate(
            age=40,
            sex="male",
            total_cholesterol=180,
            hdl_cholesterol=55,
            systolic_bp=115,
        )
        assert result.interpretation.stage == "Low Risk"

    def test_intermediate_risk_category(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Risk 10-20% = Intermediate Risk category."""
        result = calculator.calculate(
            age=55,
            sex="male",
            total_cholesterol=240,
            hdl_cholesterol=40,
            systolic_bp=145,
            smoker=True,
        )
        # Should be intermediate or high risk
        assert result.interpretation.stage in ["Intermediate Risk", "High Risk"]

    def test_high_risk_category(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Risk >20% = High Risk category."""
        result = calculator.calculate(
            age=65,
            sex="male",
            total_cholesterol=280,
            hdl_cholesterol=35,
            systolic_bp=160,
            bp_treated=True,
            smoker=True,
        )
        assert result.interpretation.stage == "High Risk"
        assert result.interpretation.risk_level == RiskLevel.HIGH


class TestFraminghamRecommendations:
    """Test Framingham-based recommendations."""

    def test_low_risk_lifestyle_focus(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Low risk: emphasize lifestyle."""
        result = calculator.calculate(
            age=35,
            sex="female",
            total_cholesterol=180,
            hdl_cholesterol=60,
            systolic_bp=115,
        )
        recommendations = result.interpretation.recommendations
        assert any("lifestyle" in r.lower() for r in recommendations)

    def test_high_risk_statin_recommendation(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """High risk: statin therapy indicated."""
        result = calculator.calculate(
            age=60,
            sex="male",
            total_cholesterol=250,
            hdl_cholesterol=35,
            systolic_bp=155,
            smoker=True,
        )
        recommendations = result.interpretation.recommendations
        assert any("statin" in r.lower() for r in recommendations)

    def test_warnings_for_smoker(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Smoker gets warning."""
        result = calculator.calculate(
            age=50,
            sex="male",
            total_cholesterol=200,
            hdl_cholesterol=50,
            systolic_bp=130,
            smoker=True,
        )
        warnings = result.interpretation.warnings
        assert any("smoking" in w.lower() for w in warnings)

    def test_warnings_for_low_hdl(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Low HDL gets warning."""
        result = calculator.calculate(
            age=50,
            sex="male",
            total_cholesterol=200,
            hdl_cholesterol=35,
            systolic_bp=130,
        )
        warnings = result.interpretation.warnings
        assert any("hdl" in w.lower() for w in warnings)


class TestFraminghamValidation:
    """Test input validation."""

    def test_age_too_young_error(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Age <20 raises error."""
        with pytest.raises(ValueError, match="Age must be"):
            calculator.calculate(
                age=18,
                sex="male",
                total_cholesterol=200,
                hdl_cholesterol=50,
                systolic_bp=120,
            )

    def test_age_too_old_error(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Age >79 raises error."""
        with pytest.raises(ValueError, match="Age must be"):
            calculator.calculate(
                age=85,
                sex="male",
                total_cholesterol=200,
                hdl_cholesterol=50,
                systolic_bp=120,
            )

    def test_negative_cholesterol_error(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Negative cholesterol raises error."""
        with pytest.raises(ValueError, match="cholesterol"):
            calculator.calculate(
                age=50,
                sex="male",
                total_cholesterol=-100,
                hdl_cholesterol=50,
                systolic_bp=120,
            )

    def test_negative_bp_error(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Negative BP raises error."""
        with pytest.raises(ValueError, match="blood pressure"):
            calculator.calculate(
                age=50,
                sex="male",
                total_cholesterol=200,
                hdl_cholesterol=50,
                systolic_bp=-10,
            )


class TestFraminghamClinicalScenarios:
    """Test realistic clinical scenarios."""

    def test_scenario_healthy_40_year_old_male(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Healthy 40-year-old male - routine screening."""
        result = calculator.calculate(
            age=40,
            sex="male",
            total_cholesterol=195,
            hdl_cholesterol=52,
            systolic_bp=118,
            bp_treated=False,
            smoker=False,
            diabetic=False,
        )
        assert result.value < 10
        # Low risk, lifestyle-focused recommendations

    def test_scenario_postmenopausal_woman_multiple_risk_factors(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """58-year-old postmenopausal woman with multiple risk factors."""
        result = calculator.calculate(
            age=58,
            sex="female",
            total_cholesterol=245,
            hdl_cholesterol=42,
            systolic_bp=148,
            bp_treated=True,  # On BP meds but not controlled
            smoker=False,
            diabetic=False,
        )
        # Intermediate to high risk
        assert result.value >= 5

    def test_scenario_young_male_smoker_family_history_concern(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """35-year-old male smoker with lipid issues."""
        result = calculator.calculate(
            age=35,
            sex="male",
            total_cholesterol=260,
            hdl_cholesterol=38,
            systolic_bp=125,
            bp_treated=False,
            smoker=True,
            diabetic=False,
        )
        # Even young patient can have elevated risk with smoking and lipids
        assert result.value > 0
        warnings = result.interpretation.warnings
        assert any("smoking" in w.lower() for w in warnings)

    def test_scenario_diabetic_patient(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Diabetic patient - automatic high risk."""
        result = calculator.calculate(
            age=50,
            sex="female",
            total_cholesterol=200,
            hdl_cholesterol=50,
            systolic_bp=130,
            bp_treated=False,
            smoker=False,
            diabetic=True,
        )
        assert result.value >= 20
        assert result.interpretation.risk_level == RiskLevel.HIGH
        assert "High Risk" in result.interpretation.stage


class TestFraminghamMetadata:
    """Test Framingham calculator metadata and references."""

    def test_tool_id(self, calculator: FraminghamRiskScoreCalculator) -> None:
        """Test calculator tool_id."""
        assert calculator.tool_id == "framingham_risk_score"

    def test_metadata_name(self, calculator: FraminghamRiskScoreCalculator) -> None:
        """Test metadata name."""
        assert "Framingham" in calculator.metadata.low_level.name

    def test_metadata_specialties(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Test specialties include cardiology."""
        specialties = calculator.metadata.high_level.specialties
        specialty_values = [s.value for s in specialties]
        assert "cardiology" in specialty_values

    def test_references_exist(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Test that references are present."""
        refs = calculator.references
        assert len(refs) >= 2
        pmids = [ref.pmid for ref in refs]
        assert "9603539" in pmids  # Wilson 1998
        assert "18212285" in pmids  # D'Agostino 2008

    def test_result_includes_parameters(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Test result includes input parameters."""
        result = calculator.calculate(
            age=50,
            sex="male",
            total_cholesterol=210,
            hdl_cholesterol=48,
            systolic_bp=135,
        )
        params = result.calculation_details["parameters"]
        assert params["age"] == 50
        assert params["sex"] == "male"
        assert params["total_cholesterol_mg_dl"] == 210


class TestFraminghamEdgeCases:
    """Test edge cases for Framingham calculations."""

    def test_boundary_age_20(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Test minimum valid age - 20."""
        result = calculator.calculate(
            age=20,
            sex="male",
            total_cholesterol=180,
            hdl_cholesterol=55,
            systolic_bp=115,
        )
        assert result.value is not None

    def test_boundary_age_79(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Test maximum valid age - 79."""
        result = calculator.calculate(
            age=79,
            sex="female",
            total_cholesterol=200,
            hdl_cholesterol=50,
            systolic_bp=130,
        )
        assert result.value is not None

    def test_extreme_high_cholesterol(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Test very high cholesterol values."""
        result = calculator.calculate(
            age=50,
            sex="male",
            total_cholesterol=400,
            hdl_cholesterol=25,
            systolic_bp=120,
        )
        # Should still calculate, high risk
        assert result.value > 0

    def test_extreme_high_bp(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Test very high BP values."""
        result = calculator.calculate(
            age=50,
            sex="male",
            total_cholesterol=200,
            hdl_cholesterol=50,
            systolic_bp=200,
        )
        assert result.value > 0

    def test_negative_total_points_possible(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Young patient with optimal values can have negative points."""
        result = calculator.calculate(
            age=25,
            sex="male",
            total_cholesterol=150,
            hdl_cholesterol=70,  # Very high HDL = -1
            systolic_bp=110,
        )
        breakdown = result.calculation_details["point_breakdown"]
        total = breakdown["total"]
        # Young male (-9) + optimal TC (0) + high HDL (-1) can be negative
        assert total < 0


class TestFraminghamCalculationDetails:
    """Test calculation details structure."""

    def test_point_breakdown_structure(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Test point breakdown contains expected components."""
        result = calculator.calculate(
            age=50,
            sex="male",
            total_cholesterol=200,
            hdl_cholesterol=50,
            systolic_bp=130,
        )
        breakdown = result.calculation_details["point_breakdown"]
        assert "age_points" in breakdown
        assert "tc_points" in breakdown
        assert "hdl_points" in breakdown
        assert "sbp_points" in breakdown
        assert "smoking_points" in breakdown
        assert "total" in breakdown

    def test_risk_numeric_matches_percentage(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Test risk_numeric is consistent with result value."""
        result = calculator.calculate(
            age=50,
            sex="male",
            total_cholesterol=200,
            hdl_cholesterol=50,
            systolic_bp=130,
        )
        assert result.value == result.calculation_details["risk_numeric"]

    def test_formula_description(
        self, calculator: FraminghamRiskScoreCalculator
    ) -> None:
        """Test formula description is present."""
        result = calculator.calculate(
            age=50,
            sex="male",
            total_cholesterol=200,
            hdl_cholesterol=50,
            systolic_bp=130,
        )
        assert "Framingham" in result.formula_used
        assert "ATP III" in result.formula_used
