"""
Tests for Nephrology Calculators

Tests CKD-EPI 2021 eGFR calculator.
"""

import pytest


class TestCkdEpi2021Calculator:
    """Tests for CKD-EPI 2021 eGFR calculator."""

    def test_normal_gfr_young_male(self):
        """Test normal kidney function in young male."""
        from src.domain.services.calculators import CkdEpi2021Calculator
        
        calc = CkdEpi2021Calculator()
        result = calc.calculate(creatinine=0.9, age=30, sex="male")
        
        assert result.value is not None
        assert result.value > 90  # Normal GFR
        assert "Normal" in result.interpretation.summary or result.value >= 90

    def test_normal_gfr_young_female(self):
        """Test normal kidney function in young female."""
        from src.domain.services.calculators import CkdEpi2021Calculator
        
        calc = CkdEpi2021Calculator()
        result = calc.calculate(creatinine=0.7, age=25, sex="female")
        
        assert result.value is not None
        assert result.value > 90

    def test_moderate_ckd(self):
        """Test moderate CKD detection."""
        from src.domain.services.calculators import CkdEpi2021Calculator
        
        calc = CkdEpi2021Calculator()
        result = calc.calculate(creatinine=2.0, age=60, sex="male")
        
        assert result.value is not None
        assert result.value < 60  # Stage 3 or worse

    def test_severe_ckd(self):
        """Test severe CKD detection."""
        from src.domain.services.calculators import CkdEpi2021Calculator
        
        calc = CkdEpi2021Calculator()
        result = calc.calculate(creatinine=5.0, age=70, sex="male")
        
        assert result.value is not None
        assert result.value < 30  # Stage 4 or 5

    def test_elderly_patient(self):
        """Test GFR calculation for elderly patient."""
        from src.domain.services.calculators import CkdEpi2021Calculator
        
        calc = CkdEpi2021Calculator()
        result = calc.calculate(creatinine=1.2, age=85, sex="female")
        
        assert result.value is not None
        assert result.unit == "mL/min/1.73m²"

    def test_has_references(self):
        """Test that calculator includes proper references."""
        from src.domain.services.calculators import CkdEpi2021Calculator
        
        calc = CkdEpi2021Calculator()
        result = calc.calculate(creatinine=1.0, age=50, sex="male")
        
        assert result.references is not None
        assert len(result.references) > 0
        # Should reference the 2021 paper
        assert any("2021" in ref.citation for ref in result.references)

    def test_tool_metadata(self):
        """Test calculator metadata is properly set."""
        from src.domain.services.calculators import CkdEpi2021Calculator
        
        calc = CkdEpi2021Calculator()
        
        assert calc.tool_id == "ckd_epi_2021"
        assert "CKD-EPI" in calc.tool_name
        assert calc.category is not None

    def test_sex_case_insensitive(self):
        """Test that sex parameter is case-insensitive."""
        from src.domain.services.calculators import CkdEpi2021Calculator
        
        calc = CkdEpi2021Calculator()
        
        result1 = calc.calculate(creatinine=1.0, age=50, sex="male")
        result2 = calc.calculate(creatinine=1.0, age=50, sex="Male")
        result3 = calc.calculate(creatinine=1.0, age=50, sex="MALE")
        
        # All should produce the same result
        assert result1.value == result2.value == result3.value
