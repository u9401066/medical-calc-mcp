"""Tests for Nephrology Calculators"""
import pytest


class TestCkdEpi2021Calculator:
    def test_ckd_epi_basic(self):
        from src.domain.services.calculators import CkdEpi2021Calculator
        calc = CkdEpi2021Calculator()
        result = calc.calculate(age=50, sex="male", serum_creatinine=1.0)
        assert result.value > 0
        assert "mL/min" in str(result.unit)

    def test_ckd_epi_female(self):
        from src.domain.services.calculators import CkdEpi2021Calculator
        calc = CkdEpi2021Calculator()
        result = calc.calculate(age=50, sex="female", serum_creatinine=1.0)
        assert result.value > 0

    def test_tool_id(self):
        from src.domain.services.calculators import CkdEpi2021Calculator
        calc = CkdEpi2021Calculator()
        assert calc.tool_id == "ckd_epi_2021"
