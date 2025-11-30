"""Tests for Surgery/Perioperative Calculators"""
import pytest


class TestCapriniVteCalculator:
    def test_caprini_low_risk(self):
        from src.domain.services.calculators import CapriniVteCalculator
        calc = CapriniVteCalculator()
        result = calc.calculate(age_years=30)
        assert result.value >= 0

    def test_caprini_high_risk(self):
        from src.domain.services.calculators import CapriniVteCalculator
        calc = CapriniVteCalculator()
        result = calc.calculate(
            age_years=70, major_surgery=True, history_dvt_pe=True, malignancy=True
        )
        assert result.value >= 5

    def test_tool_id(self):
        from src.domain.services.calculators import CapriniVteCalculator
        assert CapriniVteCalculator().tool_id == "caprini_vte"
