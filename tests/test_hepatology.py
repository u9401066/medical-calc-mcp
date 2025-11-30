"""Tests for Hepatology Calculators"""
import pytest


class TestMeldScoreCalculator:
    def test_meld_basic(self):
        from src.domain.services.calculators import MeldScoreCalculator
        calc = MeldScoreCalculator()
        result = calc.calculate(
            creatinine=1.0, bilirubin=1.0, inr=1.0, sodium=140
        )
        assert result.value >= 6

    def test_meld_dialysis(self):
        from src.domain.services.calculators import MeldScoreCalculator
        calc = MeldScoreCalculator()
        result = calc.calculate(
            creatinine=4.0, bilirubin=1.0, inr=1.0, sodium=140, on_dialysis=True
        )
        assert result.value >= 6

    def test_tool_id(self):
        from src.domain.services.calculators import MeldScoreCalculator
        assert MeldScoreCalculator().tool_id == "meld_score"
