"""
Tests for Hepatology Calculators

Tests MELD/MELD-Na Score calculator.
"""

import pytest


class TestMeldCalculator:
    """Tests for MELD/MELD-Na Score."""

    def test_low_meld_score(self):
        """Test MELD with normal liver function."""
        from src.domain.services.calculators import MeldScoreCalculator
        
        calc = MeldScoreCalculator()
        result = calc.calculate(
            bilirubin=1.0,
            inr=1.0,
            creatinine=0.8,
            sodium=140,
            dialysis_twice_in_past_week=False,
        )
        
        assert result.value is not None
        assert result.value < 15  # Low MELD

    def test_moderate_meld_score(self):
        """Test MELD with moderate liver dysfunction."""
        from src.domain.services.calculators import MeldScoreCalculator
        
        calc = MeldScoreCalculator()
        result = calc.calculate(
            bilirubin=3.0,
            inr=1.8,
            creatinine=1.5,
            sodium=132,
            dialysis_twice_in_past_week=False,
        )
        
        assert result.value is not None
        assert 15 <= result.value < 25

    def test_high_meld_score(self):
        """Test MELD with severe liver dysfunction."""
        from src.domain.services.calculators import MeldScoreCalculator
        
        calc = MeldScoreCalculator()
        result = calc.calculate(
            bilirubin=10.0,
            inr=3.0,
            creatinine=3.0,
            sodium=125,
            dialysis_twice_in_past_week=True,
        )
        
        assert result.value is not None
        assert result.value >= 25  # High MELD

    def test_dialysis_sets_creatinine_to_4(self):
        """Test that dialysis 2x/week sets creatinine to 4.0."""
        from src.domain.services.calculators import MeldScoreCalculator
        
        calc = MeldScoreCalculator()
        
        # Without dialysis, low creatinine
        result1 = calc.calculate(
            bilirubin=5.0,
            inr=2.0,
            creatinine=0.8,
            sodium=135,
            dialysis_twice_in_past_week=False,
        )
        
        # With dialysis (creatinine should be set to 4.0)
        result2 = calc.calculate(
            bilirubin=5.0,
            inr=2.0,
            creatinine=0.8,
            sodium=135,
            dialysis_twice_in_past_week=True,
        )
        
        # MELD should be higher with dialysis
        assert result2.value > result1.value

    def test_sodium_bounds(self):
        """Test that sodium is bounded (125-137 for MELD-Na)."""
        from src.domain.services.calculators import MeldScoreCalculator
        
        calc = MeldScoreCalculator()
        
        # Very low sodium (should be bounded to 125)
        result1 = calc.calculate(
            bilirubin=2.0,
            inr=1.5,
            creatinine=1.0,
            sodium=115,
            dialysis_twice_in_past_week=False,
        )
        
        # Normal high sodium (should be bounded to 137)
        result2 = calc.calculate(
            bilirubin=2.0,
            inr=1.5,
            creatinine=1.0,
            sodium=145,
            dialysis_twice_in_past_week=False,
        )
        
        # Both should calculate without error
        assert result1.value is not None
        assert result2.value is not None

    def test_minimum_values(self):
        """Test that minimum values are enforced (bilirubin, creatinine, INR)."""
        from src.domain.services.calculators import MeldScoreCalculator
        
        calc = MeldScoreCalculator()
        
        # Very low values (should be bounded to 1.0)
        result = calc.calculate(
            bilirubin=0.3,
            inr=0.5,
            creatinine=0.3,
            sodium=140,
            dialysis_twice_in_past_week=False,
        )
        
        assert result.value is not None
        assert result.value >= 6  # Minimum MELD is 6

    def test_meld_score_range(self):
        """Test MELD score is within valid range (6-40)."""
        from src.domain.services.calculators import MeldScoreCalculator
        
        calc = MeldScoreCalculator()
        
        # Minimum scenario
        result1 = calc.calculate(
            bilirubin=1.0,
            inr=1.0,
            creatinine=1.0,
            sodium=140,
            dialysis_twice_in_past_week=False,
        )
        assert result1.value >= 6
        
        # Maximum scenario
        result2 = calc.calculate(
            bilirubin=40.0,
            inr=6.0,
            creatinine=4.0,
            sodium=120,
            dialysis_twice_in_past_week=True,
        )
        assert result2.value <= 40

    def test_has_references(self):
        """Test that MELD includes proper references."""
        from src.domain.services.calculators import MeldScoreCalculator
        
        calc = MeldScoreCalculator()
        result = calc.calculate(
            bilirubin=2.0,
            inr=1.5,
            creatinine=1.0,
            sodium=135,
            dialysis_twice_in_past_week=False,
        )
        
        assert result.references is not None
        assert len(result.references) > 0

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import MeldScoreCalculator
        
        calc = MeldScoreCalculator()
        assert calc.tool_id == "meld"
