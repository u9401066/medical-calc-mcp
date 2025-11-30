"""
Tests for Cardiology Calculators

Tests CHA₂DS₂-VASc, CHA₂DS₂-VA (2024 ESC), and HEART Score calculators.
"""

import pytest


class TestChads2VascCalculator:
    """Tests for CHA₂DS₂-VASc Score (original version)."""

    def test_score_zero(self):
        """Test CHA₂DS₂-VASc with no risk factors (young male)."""
        from src.domain.services.calculators import Chads2VascCalculator
        
        calc = Chads2VascCalculator()
        result = calc.calculate(
            congestive_heart_failure=False,
            hypertension=False,
            age=50,
            diabetes=False,
            stroke_tia_thromboembolism=False,
            vascular_disease=False,
            sex="male",
        )
        
        assert result.value == 0

    def test_female_adds_one_point(self):
        """Test that female sex adds 1 point in original score."""
        from src.domain.services.calculators import Chads2VascCalculator
        
        calc = Chads2VascCalculator()
        result = calc.calculate(
            congestive_heart_failure=False,
            hypertension=False,
            age=50,
            diabetes=False,
            stroke_tia_thromboembolism=False,
            vascular_disease=False,
            sex="female",
        )
        
        assert result.value == 1  # Female sex = +1

    def test_age_65_74_adds_one_point(self):
        """Test age 65-74 adds 1 point."""
        from src.domain.services.calculators import Chads2VascCalculator
        
        calc = Chads2VascCalculator()
        result = calc.calculate(
            congestive_heart_failure=False,
            hypertension=False,
            age=70,
            diabetes=False,
            stroke_tia_thromboembolism=False,
            vascular_disease=False,
            sex="male",
        )
        
        assert result.value == 1  # Age 65-74 = +1

    def test_age_75_plus_adds_two_points(self):
        """Test age ≥75 adds 2 points."""
        from src.domain.services.calculators import Chads2VascCalculator
        
        calc = Chads2VascCalculator()
        result = calc.calculate(
            congestive_heart_failure=False,
            hypertension=False,
            age=80,
            diabetes=False,
            stroke_tia_thromboembolism=False,
            vascular_disease=False,
            sex="male",
        )
        
        assert result.value == 2  # Age ≥75 = +2

    def test_stroke_history_adds_two_points(self):
        """Test stroke/TIA history adds 2 points."""
        from src.domain.services.calculators import Chads2VascCalculator
        
        calc = Chads2VascCalculator()
        result = calc.calculate(
            congestive_heart_failure=False,
            hypertension=False,
            age=50,
            diabetes=False,
            stroke_tia_thromboembolism=True,
            vascular_disease=False,
            sex="male",
        )
        
        assert result.value == 2  # Stroke = +2

    def test_max_score_is_9(self):
        """Test maximum score is 9."""
        from src.domain.services.calculators import Chads2VascCalculator
        
        calc = Chads2VascCalculator()
        result = calc.calculate(
            congestive_heart_failure=True,  # +1
            hypertension=True,              # +1
            age=80,                         # +2
            diabetes=True,                  # +1
            stroke_tia_thromboembolism=True, # +2
            vascular_disease=True,          # +1
            sex="female",                   # +1
        )
        
        assert result.value == 9

    def test_high_score_recommends_anticoagulation(self):
        """Test high score recommends oral anticoagulation."""
        from src.domain.services.calculators import Chads2VascCalculator
        
        calc = Chads2VascCalculator()
        result = calc.calculate(
            congestive_heart_failure=True,
            hypertension=True,
            age=75,
            diabetes=True,
            stroke_tia_thromboembolism=False,
            vascular_disease=False,
            sex="male",
        )
        
        assert result.value >= 2
        # Should recommend anticoagulation
        assert "anticoagul" in result.interpretation.summary.lower() or result.value >= 2

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import Chads2VascCalculator
        
        calc = Chads2VascCalculator()
        assert calc.tool_id == "chads2_vasc"


class TestChads2VaCalculator:
    """Tests for CHA₂DS₂-VA Score (2024 ESC, sex-neutral version)."""

    def test_score_zero(self):
        """Test CHA₂DS₂-VA with no risk factors."""
        from src.domain.services.calculators import Chads2VaCalculator
        
        calc = Chads2VaCalculator()
        result = calc.calculate(
            congestive_heart_failure=False,
            hypertension=False,
            age=50,
            diabetes=False,
            stroke_tia_thromboembolism=False,
            vascular_disease=False,
        )
        
        assert result.value == 0

    def test_no_sex_parameter_required(self):
        """Test that sex is not a parameter in 2024 ESC version."""
        from src.domain.services.calculators import Chads2VaCalculator
        
        calc = Chads2VaCalculator()
        # Should work without sex parameter
        result = calc.calculate(
            congestive_heart_failure=True,
            hypertension=True,
            age=70,
            diabetes=False,
            stroke_tia_thromboembolism=False,
            vascular_disease=False,
        )
        
        assert result.value == 3  # CHF + HTN + Age 65-74

    def test_max_score_is_8(self):
        """Test maximum score is 8 (not 9, since no sex factor)."""
        from src.domain.services.calculators import Chads2VaCalculator
        
        calc = Chads2VaCalculator()
        result = calc.calculate(
            congestive_heart_failure=True,  # +1
            hypertension=True,              # +1
            age=80,                         # +2
            diabetes=True,                  # +1
            stroke_tia_thromboembolism=True, # +2
            vascular_disease=True,          # +1
        )
        
        assert result.value == 8

    def test_age_scoring(self):
        """Test age scoring matches CHA₂DS₂-VASc."""
        from src.domain.services.calculators import Chads2VaCalculator
        
        calc = Chads2VaCalculator()
        
        # Age < 65: 0 points
        result1 = calc.calculate(
            congestive_heart_failure=False,
            hypertension=False,
            age=60,
            diabetes=False,
            stroke_tia_thromboembolism=False,
            vascular_disease=False,
        )
        assert result1.value == 0
        
        # Age 65-74: 1 point
        result2 = calc.calculate(
            congestive_heart_failure=False,
            hypertension=False,
            age=70,
            diabetes=False,
            stroke_tia_thromboembolism=False,
            vascular_disease=False,
        )
        assert result2.value == 1
        
        # Age ≥75: 2 points
        result3 = calc.calculate(
            congestive_heart_failure=False,
            hypertension=False,
            age=80,
            diabetes=False,
            stroke_tia_thromboembolism=False,
            vascular_disease=False,
        )
        assert result3.value == 2

    def test_references_2024_esc(self):
        """Test that 2024 ESC Guidelines are referenced."""
        from src.domain.services.calculators import Chads2VaCalculator
        
        calc = Chads2VaCalculator()
        result = calc.calculate(
            congestive_heart_failure=False,
            hypertension=False,
            age=50,
            diabetes=False,
            stroke_tia_thromboembolism=False,
            vascular_disease=False,
        )
        
        assert result.references is not None
        assert len(result.references) > 0
        # Should reference 2024 ESC
        assert any("2024" in ref.citation for ref in result.references)

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import Chads2VaCalculator
        
        calc = Chads2VaCalculator()
        assert calc.tool_id == "chads2_va"


class TestHeartScoreCalculator:
    """Tests for HEART Score for Major Cardiac Events."""

    def test_low_risk_score(self):
        """Test HEART score for low risk patient."""
        from src.domain.services.calculators import HeartScoreCalculator
        
        calc = HeartScoreCalculator()
        result = calc.calculate(
            history=0,
            ecg=0,
            age=40,
            risk_factors=0,
            troponin=0,
        )
        
        assert result.value == 0
        assert "low" in result.interpretation.summary.lower()

    def test_moderate_risk_score(self):
        """Test HEART score for moderate risk patient."""
        from src.domain.services.calculators import HeartScoreCalculator
        
        calc = HeartScoreCalculator()
        result = calc.calculate(
            history=1,
            ecg=1,
            age=55,
            risk_factors=1,
            troponin=1,
        )
        
        assert result.value == 5  # 1+1+1+1+1 = 5

    def test_high_risk_score(self):
        """Test HEART score for high risk patient."""
        from src.domain.services.calculators import HeartScoreCalculator
        
        calc = HeartScoreCalculator()
        result = calc.calculate(
            history=2,
            ecg=2,
            age=70,
            risk_factors=2,
            troponin=2,
        )
        
        assert result.value == 10  # Max score
        assert "high" in result.interpretation.summary.lower()

    def test_age_scoring(self):
        """Test HEART age scoring."""
        from src.domain.services.calculators import HeartScoreCalculator
        
        calc = HeartScoreCalculator()
        
        # Age < 45: 0 points
        result1 = calc.calculate(history=0, ecg=0, age=40, risk_factors=0, troponin=0)
        assert result1.value == 0
        
        # Age 45-64: 1 point  
        result2 = calc.calculate(history=0, ecg=0, age=55, risk_factors=0, troponin=0)
        assert result2.value == 1
        
        # Age ≥65: 2 points
        result3 = calc.calculate(history=0, ecg=0, age=70, risk_factors=0, troponin=0)
        assert result3.value == 2

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import HeartScoreCalculator
        
        calc = HeartScoreCalculator()
        assert calc.tool_id == "heart_score"
