"""
Tests for Anesthesiology/Preoperative Calculators

Tests ASA Physical Status, Mallampati, and RCRI calculators.
"""

import pytest


class TestAsaPhysicalStatus:
    """Tests for ASA Physical Status Classification."""

    def test_asa_class_1(self):
        """Test ASA Class I - healthy patient."""
        from src.domain.services.calculators import AsaPhysicalStatusCalculator
        
        calc = AsaPhysicalStatusCalculator()
        result = calc.calculate(asa_class=1)
        
        assert result.value == 1
        assert "healthy" in result.interpretation.summary.lower()

    def test_asa_class_2(self):
        """Test ASA Class II - mild systemic disease."""
        from src.domain.services.calculators import AsaPhysicalStatusCalculator
        
        calc = AsaPhysicalStatusCalculator()
        result = calc.calculate(asa_class=2)
        
        assert result.value == 2
        assert "mild" in result.interpretation.summary.lower()

    def test_asa_class_3(self):
        """Test ASA Class III - severe systemic disease."""
        from src.domain.services.calculators import AsaPhysicalStatusCalculator
        
        calc = AsaPhysicalStatusCalculator()
        result = calc.calculate(asa_class=3)
        
        assert result.value == 3

    def test_asa_class_4(self):
        """Test ASA Class IV - life-threatening disease."""
        from src.domain.services.calculators import AsaPhysicalStatusCalculator
        
        calc = AsaPhysicalStatusCalculator()
        result = calc.calculate(asa_class=4)
        
        assert result.value == 4

    def test_asa_class_5(self):
        """Test ASA Class V - moribund patient."""
        from src.domain.services.calculators import AsaPhysicalStatusCalculator
        
        calc = AsaPhysicalStatusCalculator()
        result = calc.calculate(asa_class=5)
        
        assert result.value == 5

    def test_asa_class_6(self):
        """Test ASA Class VI - brain-dead organ donor."""
        from src.domain.services.calculators import AsaPhysicalStatusCalculator
        
        calc = AsaPhysicalStatusCalculator()
        result = calc.calculate(asa_class=6)
        
        assert result.value == 6

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import AsaPhysicalStatusCalculator
        
        calc = AsaPhysicalStatusCalculator()
        assert calc.tool_id == "asa_physical_status"


class TestMallampatiScore:
    """Tests for Mallampati Airway Assessment Score."""

    def test_grade_1(self):
        """Test Mallampati Grade I - easy intubation."""
        from src.domain.services.calculators import MallampatiScoreCalculator
        
        calc = MallampatiScoreCalculator()
        result = calc.calculate(mallampati_class=1)
        
        assert result.value == 1
        assert result.interpretation is not None

    def test_grade_2(self):
        """Test Mallampati Grade II."""
        from src.domain.services.calculators import MallampatiScoreCalculator
        
        calc = MallampatiScoreCalculator()
        result = calc.calculate(mallampati_class=2)
        
        assert result.value == 2

    def test_grade_3(self):
        """Test Mallampati Grade III."""
        from src.domain.services.calculators import MallampatiScoreCalculator
        
        calc = MallampatiScoreCalculator()
        result = calc.calculate(mallampati_class=3)
        
        assert result.value == 3

    def test_grade_4(self):
        """Test Mallampati Grade IV - difficult intubation expected."""
        from src.domain.services.calculators import MallampatiScoreCalculator
        
        calc = MallampatiScoreCalculator()
        result = calc.calculate(mallampati_class=4)
        
        assert result.value == 4

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import MallampatiScoreCalculator
        
        calc = MallampatiScoreCalculator()
        assert calc.tool_id == "mallampati_score"


class TestRcriCalculator:
    """Tests for Revised Cardiac Risk Index (RCRI/Lee Index)."""

    def test_rcri_zero_points(self):
        """Test RCRI with no risk factors - low risk."""
        from src.domain.services.calculators import RcriCalculator
        
        calc = RcriCalculator()
        result = calc.calculate(
            high_risk_surgery=False,
            ischemic_heart_disease=False,
            heart_failure=False,
            cerebrovascular_disease=False,
            insulin_diabetes=False,
            creatinine_above_2=False,
        )
        
        assert result.value == 0
        assert "low" in result.interpretation.summary.lower()

    def test_rcri_one_point(self):
        """Test RCRI with one risk factor."""
        from src.domain.services.calculators import RcriCalculator
        
        calc = RcriCalculator()
        result = calc.calculate(
            high_risk_surgery=True,
            ischemic_heart_disease=False,
            heart_failure=False,
            cerebrovascular_disease=False,
            insulin_diabetes=False,
            creatinine_above_2=False,
        )
        
        assert result.value == 1

    def test_rcri_multiple_points(self):
        """Test RCRI with multiple risk factors."""
        from src.domain.services.calculators import RcriCalculator
        
        calc = RcriCalculator()
        result = calc.calculate(
            high_risk_surgery=True,
            ischemic_heart_disease=True,
            heart_failure=True,
            cerebrovascular_disease=False,
            insulin_diabetes=True,
            creatinine_above_2=True,
        )
        
        assert result.value == 5
        assert "high" in result.interpretation.summary.lower() or result.value >= 3

    def test_rcri_max_points(self):
        """Test RCRI with all risk factors - highest risk."""
        from src.domain.services.calculators import RcriCalculator
        
        calc = RcriCalculator()
        result = calc.calculate(
            high_risk_surgery=True,
            ischemic_heart_disease=True,
            heart_failure=True,
            cerebrovascular_disease=True,
            insulin_diabetes=True,
            creatinine_above_2=True,
        )
        
        assert result.value == 6

    def test_has_references(self):
        """Test that RCRI includes Lee et al. reference."""
        from src.domain.services.calculators import RcriCalculator
        
        calc = RcriCalculator()
        result = calc.calculate(
            high_risk_surgery=False,
            ischemic_heart_disease=False,
            heart_failure=False,
            cerebrovascular_disease=False,
            insulin_diabetes=False,
            creatinine_above_2=False,
        )
        
        assert result.references is not None
        assert len(result.references) > 0

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import RcriCalculator
        
        calc = RcriCalculator()
        assert calc.tool_id == "rcri"


class TestApfelPonvCalculator:
    """Tests for Apfel Score PONV Risk Calculator."""

    def test_zero_risk_factors(self):
        """Test Apfel score 0 - very low risk (~10%)."""
        from src.domain.services.calculators import ApfelPonvCalculator
        
        calc = ApfelPonvCalculator()
        result = calc.calculate(
            female_gender=False,
            history_motion_sickness_or_ponv=False,
            non_smoker=False,  # Smoker
            postoperative_opioids=False
        )
        
        assert result.value == 0
        assert result.calculation_details["ponv_risk_percent"] == 10.0
        assert "very low" in result.interpretation.summary.lower()

    def test_one_risk_factor(self):
        """Test Apfel score 1 - low risk (~21%)."""
        from src.domain.services.calculators import ApfelPonvCalculator
        
        calc = ApfelPonvCalculator()
        result = calc.calculate(
            female_gender=True,
            history_motion_sickness_or_ponv=False,
            non_smoker=False,
            postoperative_opioids=False
        )
        
        assert result.value == 1
        assert result.calculation_details["ponv_risk_percent"] == 21.0

    def test_two_risk_factors(self):
        """Test Apfel score 2 - moderate risk (~39%)."""
        from src.domain.services.calculators import ApfelPonvCalculator
        
        calc = ApfelPonvCalculator()
        result = calc.calculate(
            female_gender=True,
            history_motion_sickness_or_ponv=True,
            non_smoker=False,
            postoperative_opioids=False
        )
        
        assert result.value == 2
        assert result.calculation_details["ponv_risk_percent"] == 39.0
        assert "moderate" in result.interpretation.summary.lower()

    def test_three_risk_factors(self):
        """Test Apfel score 3 - high risk (~61%)."""
        from src.domain.services.calculators import ApfelPonvCalculator
        
        calc = ApfelPonvCalculator()
        result = calc.calculate(
            female_gender=True,
            history_motion_sickness_or_ponv=True,
            non_smoker=True,
            postoperative_opioids=False
        )
        
        assert result.value == 3
        assert result.calculation_details["ponv_risk_percent"] == 61.0
        assert "high" in result.interpretation.summary.lower()

    def test_four_risk_factors(self):
        """Test Apfel score 4 - very high risk (~79%)."""
        from src.domain.services.calculators import ApfelPonvCalculator
        
        calc = ApfelPonvCalculator()
        result = calc.calculate(
            female_gender=True,
            history_motion_sickness_or_ponv=True,
            non_smoker=True,
            postoperative_opioids=True
        )
        
        assert result.value == 4
        assert result.calculation_details["ponv_risk_percent"] == 79.0
        assert "very high" in result.interpretation.summary.lower()

    def test_typical_high_risk_patient(self):
        """Test typical high-risk patient: female, non-smoker, with opioids."""
        from src.domain.services.calculators import ApfelPonvCalculator
        
        calc = ApfelPonvCalculator()
        result = calc.calculate(
            female_gender=True,
            history_motion_sickness_or_ponv=False,
            non_smoker=True,
            postoperative_opioids=True
        )
        
        assert result.value == 3
        # Should recommend multi-modal prophylaxis
        assert any("multi" in rec.lower() for rec in result.interpretation.recommendations)

    def test_risk_factors_tracked(self):
        """Test that risk factors are tracked in calculation details."""
        from src.domain.services.calculators import ApfelPonvCalculator
        
        calc = ApfelPonvCalculator()
        result = calc.calculate(
            female_gender=True,
            history_motion_sickness_or_ponv=True,
            non_smoker=False,
            postoperative_opioids=False
        )
        
        factors = result.calculation_details["risk_factors_present"]
        assert "Female gender" in factors
        assert "History of motion sickness or PONV" in factors
        assert len(factors) == 2

    def test_has_references(self):
        """Test that Apfel score includes original reference."""
        from src.domain.services.calculators import ApfelPonvCalculator
        
        calc = ApfelPonvCalculator()
        result = calc.calculate(
            female_gender=False,
            history_motion_sickness_or_ponv=False,
            non_smoker=False,
            postoperative_opioids=False
        )
        
        assert result.references is not None
        assert len(result.references) >= 1
        # Check for Apfel 1999 reference
        ref_text = str(result.references[0])
        assert "Apfel" in ref_text or "10485781" in ref_text

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import ApfelPonvCalculator
        
        calc = ApfelPonvCalculator()
        assert calc.tool_id == "apfel_ponv"

    def test_metadata(self):
        """Test that metadata is properly configured."""
        from src.domain.services.calculators import ApfelPonvCalculator
        
        calc = ApfelPonvCalculator()
        assert calc.name == "Apfel Score for PONV"
        assert "anesthesiology" in [s.value for s in calc.metadata.high_level.specialties]
