"""
Tests for Pulmonology Calculators

Tests CURB-65 and PSI/PORT Score calculators.
"""

import pytest


class TestCurb65Calculator:
    """Tests for CURB-65 Score for Pneumonia Severity."""

    def test_score_zero(self):
        """Test CURB-65 with no criteria met - outpatient management."""
        from src.domain.services.calculators import Curb65Calculator
        
        calc = Curb65Calculator()
        result = calc.calculate(
            confusion=False,
            bun_greater_than_19=False,
            respiratory_rate_30_or_more=False,
            systolic_bp_less_than_90=False,
            diastolic_bp_60_or_less=False,
            age_65_or_older=False,
        )
        
        assert result.value == 0
        assert "outpatient" in result.interpretation.summary.lower() or "low" in result.interpretation.summary.lower()

    def test_score_one(self):
        """Test CURB-65 with 1 criterion met."""
        from src.domain.services.calculators import Curb65Calculator
        
        calc = Curb65Calculator()
        result = calc.calculate(
            confusion=False,
            bun_greater_than_19=False,
            respiratory_rate_30_or_more=False,
            systolic_bp_less_than_90=False,
            diastolic_bp_60_or_less=False,
            age_65_or_older=True,  # +1
        )
        
        assert result.value == 1

    def test_score_two(self):
        """Test CURB-65 with 2 criteria met - consider hospital admission."""
        from src.domain.services.calculators import Curb65Calculator
        
        calc = Curb65Calculator()
        result = calc.calculate(
            confusion=True,          # +1
            bun_greater_than_19=True, # +1
            respiratory_rate_30_or_more=False,
            systolic_bp_less_than_90=False,
            diastolic_bp_60_or_less=False,
            age_65_or_older=False,
        )
        
        assert result.value == 2

    def test_score_three_or_more(self):
        """Test CURB-65 with 3+ criteria - consider ICU."""
        from src.domain.services.calculators import Curb65Calculator
        
        calc = Curb65Calculator()
        result = calc.calculate(
            confusion=True,                    # +1
            bun_greater_than_19=True,          # +1
            respiratory_rate_30_or_more=True,  # +1
            systolic_bp_less_than_90=False,
            diastolic_bp_60_or_less=False,
            age_65_or_older=True,              # +1
        )
        
        assert result.value == 4
        assert "icu" in result.interpretation.summary.lower() or "severe" in result.interpretation.summary.lower()

    def test_max_score_is_5(self):
        """Test maximum CURB-65 score is 5."""
        from src.domain.services.calculators import Curb65Calculator
        
        calc = Curb65Calculator()
        result = calc.calculate(
            confusion=True,
            bun_greater_than_19=True,
            respiratory_rate_30_or_more=True,
            systolic_bp_less_than_90=True,    # +1 (only counts once for hypotension)
            diastolic_bp_60_or_less=True,     # Part of same criterion
            age_65_or_older=True,
        )
        
        assert result.value == 5

    def test_blood_pressure_counts_once(self):
        """Test that hypotension only counts once."""
        from src.domain.services.calculators import Curb65Calculator
        
        calc = Curb65Calculator()
        
        # Only systolic
        result1 = calc.calculate(
            confusion=False,
            bun_greater_than_19=False,
            respiratory_rate_30_or_more=False,
            systolic_bp_less_than_90=True,
            diastolic_bp_60_or_less=False,
            age_65_or_older=False,
        )
        
        # Both systolic and diastolic
        result2 = calc.calculate(
            confusion=False,
            bun_greater_than_19=False,
            respiratory_rate_30_or_more=False,
            systolic_bp_less_than_90=True,
            diastolic_bp_60_or_less=True,
            age_65_or_older=False,
        )
        
        # Should both be 1, not 2
        assert result1.value == 1
        assert result2.value == 1

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import Curb65Calculator
        
        calc = Curb65Calculator()
        assert calc.tool_id == "curb65"


class TestPsiPortCalculator:
    """Tests for PSI/PORT Score for Pneumonia."""

    def test_class_i_young_healthy(self):
        """Test PSI Class I - young healthy patient."""
        from src.domain.services.calculators import PsiPortCalculator
        
        calc = PsiPortCalculator()
        result = calc.calculate(
            age=40,
            sex="male",
            nursing_home_resident=False,
            neoplastic_disease=False,
            liver_disease=False,
            congestive_heart_failure=False,
            cerebrovascular_disease=False,
            renal_disease=False,
            altered_mental_status=False,
            respiratory_rate_30_or_higher=False,
            systolic_bp_less_than_90=False,
            temperature_less_than_35_or_40_plus=False,
            pulse_125_or_higher=False,
            arterial_ph_less_than_7_35=False,
            bun_30_or_higher=False,
            sodium_less_than_130=False,
            glucose_250_or_higher=False,
            hematocrit_less_than_30=False,
            pao2_less_than_60=False,
            pleural_effusion=False,
        )
        
        # Class I should have very low score
        assert "class i" in result.interpretation.summary.lower() or result.value <= 50

    def test_class_v_severe(self):
        """Test PSI Class V - highest risk."""
        from src.domain.services.calculators import PsiPortCalculator
        
        calc = PsiPortCalculator()
        result = calc.calculate(
            age=80,
            sex="male",
            nursing_home_resident=True,
            neoplastic_disease=True,
            liver_disease=True,
            congestive_heart_failure=True,
            cerebrovascular_disease=True,
            renal_disease=True,
            altered_mental_status=True,
            respiratory_rate_30_or_higher=True,
            systolic_bp_less_than_90=True,
            temperature_less_than_35_or_40_plus=True,
            pulse_125_or_higher=True,
            arterial_ph_less_than_7_35=True,
            bun_30_or_higher=True,
            sodium_less_than_130=True,
            glucose_250_or_higher=True,
            hematocrit_less_than_30=True,
            pao2_less_than_60=True,
            pleural_effusion=True,
        )
        
        assert result.value > 130  # Class V: >130 points

    def test_age_scoring(self):
        """Test age contribution to PSI score."""
        from src.domain.services.calculators import PsiPortCalculator
        
        calc = PsiPortCalculator()
        
        # Male age 50: +50 points (age in years)
        result1 = calc.calculate(
            age=50, sex="male",
            nursing_home_resident=False, neoplastic_disease=False,
            liver_disease=False, congestive_heart_failure=False,
            cerebrovascular_disease=False, renal_disease=False,
            altered_mental_status=False, respiratory_rate_30_or_higher=False,
            systolic_bp_less_than_90=False, temperature_less_than_35_or_40_plus=False,
            pulse_125_or_higher=False, arterial_ph_less_than_7_35=False,
            bun_30_or_higher=False, sodium_less_than_130=False,
            glucose_250_or_higher=False, hematocrit_less_than_30=False,
            pao2_less_than_60=False, pleural_effusion=False,
        )
        
        # Female age 50: +40 points (age - 10)
        result2 = calc.calculate(
            age=50, sex="female",
            nursing_home_resident=False, neoplastic_disease=False,
            liver_disease=False, congestive_heart_failure=False,
            cerebrovascular_disease=False, renal_disease=False,
            altered_mental_status=False, respiratory_rate_30_or_higher=False,
            systolic_bp_less_than_90=False, temperature_less_than_35_or_40_plus=False,
            pulse_125_or_higher=False, arterial_ph_less_than_7_35=False,
            bun_30_or_higher=False, sodium_less_than_130=False,
            glucose_250_or_higher=False, hematocrit_less_than_30=False,
            pao2_less_than_60=False, pleural_effusion=False,
        )
        
        assert result1.value == 50
        assert result2.value == 40

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import PsiPortCalculator
        
        calc = PsiPortCalculator()
        assert calc.tool_id == "psi_port"
