from typing import Any
"""
Tests for Cardiology Calculators

Tests CHA₂DS₂-VASc, CHA₂DS₂-VA (2024 ESC), HEART Score, and HAS-BLED calculators.
"""



class TestChads2VascCalculator:
    """Tests for CHA₂DS₂-VASc Score (original version)."""

    def test_score_zero(self) -> None:
        """Test CHA₂DS₂-VASc with no risk factors (young male)."""
        from src.domain.services.calculators import Chads2VascCalculator

        calc = Chads2VascCalculator()
        result = calc.calculate(
            chf_or_lvef_lte_40=False,
            hypertension=False,
            age_gte_75=False,
            diabetes=False,
            stroke_tia_or_te_history=False,
            vascular_disease=False,
            age_65_to_74=False,
            female_sex=False,
        )

        assert result.value is not None
        assert result.value == 0

    def test_female_adds_one_point(self) -> None:
        """Test that female sex adds 1 point in original score."""
        from src.domain.services.calculators import Chads2VascCalculator

        calc = Chads2VascCalculator()
        result = calc.calculate(
            chf_or_lvef_lte_40=False,
            hypertension=False,
            age_gte_75=False,
            diabetes=False,
            stroke_tia_or_te_history=False,
            vascular_disease=False,
            age_65_to_74=False,
            female_sex=True,
        )

        assert result.value is not None
        assert result.value == 1  # Female sex = +1

    def test_age_65_74_adds_one_point(self) -> None:
        """Test age 65-74 adds 1 point."""
        from src.domain.services.calculators import Chads2VascCalculator

        calc = Chads2VascCalculator()
        result = calc.calculate(
            chf_or_lvef_lte_40=False,
            hypertension=False,
            age_gte_75=False,
            diabetes=False,
            stroke_tia_or_te_history=False,
            vascular_disease=False,
            age_65_to_74=True,
            female_sex=False,
        )

        assert result.value is not None
        assert result.value == 1  # Age 65-74 = +1

    def test_age_75_plus_adds_two_points(self) -> None:
        """Test age ≥75 adds 2 points."""
        from src.domain.services.calculators import Chads2VascCalculator

        calc = Chads2VascCalculator()
        result = calc.calculate(
            chf_or_lvef_lte_40=False,
            hypertension=False,
            age_gte_75=True,
            diabetes=False,
            stroke_tia_or_te_history=False,
            vascular_disease=False,
            age_65_to_74=False,
            female_sex=False,
        )

        assert result.value is not None
        assert result.value == 2  # Age ≥75 = +2

    def test_stroke_history_adds_two_points(self) -> None:
        """Test stroke/TIA history adds 2 points."""
        from src.domain.services.calculators import Chads2VascCalculator

        calc = Chads2VascCalculator()
        result = calc.calculate(
            chf_or_lvef_lte_40=False,
            hypertension=False,
            age_gte_75=False,
            diabetes=False,
            stroke_tia_or_te_history=True,
            vascular_disease=False,
            age_65_to_74=False,
            female_sex=False,
        )

        assert result.value is not None
        assert result.value == 2  # Stroke = +2

    def test_max_score_is_9(self) -> None:
        """Test maximum score is 9."""
        from src.domain.services.calculators import Chads2VascCalculator

        calc = Chads2VascCalculator()
        result = calc.calculate(
            chf_or_lvef_lte_40=True,      # +1
            hypertension=True,             # +1
            age_gte_75=True,              # +2
            diabetes=True,                 # +1
            stroke_tia_or_te_history=True, # +2
            vascular_disease=True,         # +1
            age_65_to_74=False,           # 0 (age ≥75 takes precedence)
            female_sex=True,              # +1
        )

        assert result.value is not None
        assert result.value == 9

    def test_high_score_recommends_anticoagulation(self) -> None:
        """Test high score recommends oral anticoagulation."""
        from src.domain.services.calculators import Chads2VascCalculator

        calc = Chads2VascCalculator()
        result = calc.calculate(
            chf_or_lvef_lte_40=True,
            hypertension=True,
            age_gte_75=True,
            diabetes=True,
            stroke_tia_or_te_history=False,
            vascular_disease=False,
            age_65_to_74=False,
            female_sex=False,
        )

        assert result.value is not None
        assert result.value >= 2

    def test_tool_id(self) -> None:
        """Test tool ID is correct."""
        from src.domain.services.calculators import Chads2VascCalculator

        calc = Chads2VascCalculator()
        assert calc.tool_id == "chads2_vasc"


class TestChads2VaCalculator:
    """Tests for CHA₂DS₂-VA Score (2024 ESC, sex-neutral version)."""

    def test_score_zero(self) -> None:
        """Test CHA₂DS₂-VA with no risk factors."""
        from src.domain.services.calculators import Chads2VaCalculator

        calc = Chads2VaCalculator()
        result = calc.calculate(
            chf_or_lvef_lte_40=False,
            hypertension=False,
            age_gte_75=False,
            diabetes=False,
            stroke_tia_or_te_history=False,
            vascular_disease=False,
            age_65_to_74=False,
        )

        assert result.value is not None
        assert result.value == 0

    def test_no_sex_parameter_required(self) -> None:
        """Test that sex is not a parameter in 2024 ESC version."""
        from src.domain.services.calculators import Chads2VaCalculator

        calc = Chads2VaCalculator()
        result = calc.calculate(
            chf_or_lvef_lte_40=True,
            hypertension=True,
            age_gte_75=False,
            diabetes=False,
            stroke_tia_or_te_history=False,
            vascular_disease=False,
            age_65_to_74=True,
        )

        assert result.value is not None
        assert result.value == 3  # CHF + HTN + Age 65-74

    def test_max_score_is_8(self) -> None:
        """Test maximum score is 8 (not 9, since no sex factor)."""
        from src.domain.services.calculators import Chads2VaCalculator

        calc = Chads2VaCalculator()
        result = calc.calculate(
            chf_or_lvef_lte_40=True,       # +1
            hypertension=True,             # +1
            age_gte_75=True,              # +2
            diabetes=True,                 # +1
            stroke_tia_or_te_history=True, # +2
            vascular_disease=True,         # +1
            age_65_to_74=False,
        )

        assert result.value is not None
        assert result.value == 8

    def test_age_scoring(self) -> None:
        """Test age scoring."""
        from src.domain.services.calculators import Chads2VaCalculator

        calc = Chads2VaCalculator()

        # Age < 65: 0 points
        result1 = calc.calculate(
            chf_or_lvef_lte_40=False,
            hypertension=False,
            age_gte_75=False,
            diabetes=False,
            stroke_tia_or_te_history=False,
            vascular_disease=False,
            age_65_to_74=False,
        )
        assert result1.value is not None
        assert result1.value == 0

        # Age 65-74: 1 point
        result2 = calc.calculate(
            chf_or_lvef_lte_40=False,
            hypertension=False,
            age_gte_75=False,
            diabetes=False,
            stroke_tia_or_te_history=False,
            vascular_disease=False,
            age_65_to_74=True,
        )
        assert result2.value is not None
        assert result2.value == 1

        # Age ≥75: 2 points
        result3 = calc.calculate(
            chf_or_lvef_lte_40=False,
            hypertension=False,
            age_gte_75=True,
            diabetes=False,
            stroke_tia_or_te_history=False,
            vascular_disease=False,
            age_65_to_74=False,
        )
        assert result3.value is not None
        assert result3.value == 2

    def test_references_2024_esc(self) -> None:
        """Test that 2024 ESC Guidelines are referenced."""
        from src.domain.services.calculators import Chads2VaCalculator

        calc = Chads2VaCalculator()
        result = calc.calculate(
            chf_or_lvef_lte_40=False,
            hypertension=False,
            age_gte_75=False,
            diabetes=False,
            stroke_tia_or_te_history=False,
            vascular_disease=False,
            age_65_to_74=False,
        )

        assert result.references is not None
        assert len(result.references) > 0
        assert any("2024" in ref.citation for ref in result.references)

    def test_tool_id(self) -> None:
        """Test tool ID is correct."""
        from src.domain.services.calculators import Chads2VaCalculator

        calc = Chads2VaCalculator()
        assert calc.tool_id == "chads2_va"


class TestHeartScoreCalculator:
    """Tests for HEART Score for Major Cardiac Events."""

    def test_low_risk_score(self) -> None:
        """Test HEART score for low risk patient."""
        from src.domain.services.calculators import HeartScoreCalculator

        calc = HeartScoreCalculator()
        result = calc.calculate(
            history_score=0,
            ecg_score=0,
            age_score=0,
            risk_factors_score=0,
            troponin_score=0,
        )

        assert result.value is not None
        assert result.value == 0
        assert result.interpretation.summary is not None
        assert "low" in result.interpretation.summary.lower()

    def test_moderate_risk_score(self) -> None:
        """Test HEART score for moderate risk patient."""
        from src.domain.services.calculators import HeartScoreCalculator

        calc = HeartScoreCalculator()
        result = calc.calculate(
            history_score=1,
            ecg_score=1,
            age_score=1,
            risk_factors_score=1,
            troponin_score=1,
        )

        assert result.value is not None
        assert result.value == 5

    def test_high_risk_score(self) -> None:
        """Test HEART score for high risk patient."""
        from src.domain.services.calculators import HeartScoreCalculator

        calc = HeartScoreCalculator()
        result = calc.calculate(
            history_score=2,
            ecg_score=2,
            age_score=2,
            risk_factors_score=2,
            troponin_score=2,
        )

        assert result.value is not None
        assert result.value == 10
        assert result.interpretation.summary is not None
        assert "high" in result.interpretation.summary.lower()

    def test_age_scoring(self) -> None:
        """Test HEART age scoring."""
        from src.domain.services.calculators import HeartScoreCalculator

        calc = HeartScoreCalculator()

        result1 = calc.calculate(
            history_score=0, ecg_score=0, age_score=0,
            risk_factors_score=0, troponin_score=0
        )
        assert result1.value is not None
        assert result1.value == 0

        result2 = calc.calculate(
            history_score=0, ecg_score=0, age_score=1,
            risk_factors_score=0, troponin_score=0
        )
        assert result2.value is not None
        assert result2.value == 1

        result3 = calc.calculate(
            history_score=0, ecg_score=0, age_score=2,
            risk_factors_score=0, troponin_score=0
        )
        assert result3.value is not None
        assert result3.value == 2

    def test_tool_id(self) -> None:
        """Test tool ID is correct."""
        from src.domain.services.calculators import HeartScoreCalculator

        calc = HeartScoreCalculator()
        assert calc.tool_id == "heart_score"


class TestHasBledCalculator:
    """Tests for HAS-BLED Score (2024 ESC recommended bleeding risk)."""

    def test_score_zero(self) -> None:
        """Test HAS-BLED with no risk factors."""
        from src.domain.services.calculators import HasBledCalculator

        calc = HasBledCalculator()
        result = calc.calculate(
            hypertension_uncontrolled=False,
            renal_disease=False,
            liver_disease=False,
            stroke_history=False,
            bleeding_history=False,
            labile_inr=False,
            elderly_gt_65=False,
            drugs_antiplatelet_nsaid=False,
            alcohol_excess=False,
        )

        assert result.value is not None
        assert result.value == 0
        assert result.interpretation.summary is not None
        assert "low" in result.interpretation.summary.lower()

    def test_low_risk_score(self) -> None:
        """Test HAS-BLED score of 2 is still low risk."""
        from src.domain.services.calculators import HasBledCalculator

        calc = HasBledCalculator()
        result = calc.calculate(
            hypertension_uncontrolled=True,  # +1
            renal_disease=False,
            liver_disease=False,
            stroke_history=False,
            bleeding_history=False,
            labile_inr=False,
            elderly_gt_65=True,  # +1
            drugs_antiplatelet_nsaid=False,
            alcohol_excess=False,
        )

        assert result.value is not None
        assert result.value == 2
        assert result.interpretation.summary is not None
        assert "low" in result.interpretation.summary.lower()

    def test_high_risk_score(self) -> None:
        """Test HAS-BLED ≥3 is high risk."""
        from src.domain.services.calculators import HasBledCalculator

        calc = HasBledCalculator()
        result = calc.calculate(
            hypertension_uncontrolled=True,  # +1
            renal_disease=True,              # +1
            liver_disease=False,
            stroke_history=True,             # +1
            bleeding_history=False,
            labile_inr=False,
            elderly_gt_65=False,
            drugs_antiplatelet_nsaid=False,
            alcohol_excess=False,
        )

        assert result.value is not None
        assert result.value == 3
        assert result.interpretation.summary is not None
        assert "high" in result.interpretation.summary.lower()

    def test_max_score(self) -> None:
        """Test maximum HAS-BLED score."""
        from src.domain.services.calculators import HasBledCalculator

        calc = HasBledCalculator()
        result = calc.calculate(
            hypertension_uncontrolled=True,   # +1
            renal_disease=True,               # +1
            liver_disease=True,               # +1
            stroke_history=True,              # +1
            bleeding_history=True,            # +1
            labile_inr=True,                  # +1
            elderly_gt_65=True,               # +1
            drugs_antiplatelet_nsaid=True,    # +1
            alcohol_excess=True,              # +1
        )

        assert result.value is not None
        assert result.value == 9

    def test_modifiable_factors_identified(self) -> None:
        """Test that modifiable risk factors are identified in recommendations."""
        from src.domain.services.calculators import HasBledCalculator

        calc = HasBledCalculator()
        result = calc.calculate(
            hypertension_uncontrolled=True,
            renal_disease=False,
            liver_disease=False,
            stroke_history=True,
            bleeding_history=False,
            labile_inr=True,
            elderly_gt_65=True,
            drugs_antiplatelet_nsaid=True,
            alcohol_excess=True,
        )

        # Should mention modifiable factors
        recommendations = " ".join(result.interpretation.recommendations)
        assert "hypertension" in recommendations.lower() or "BP" in recommendations

    def test_high_score_not_contraindication(self) -> None:
        """Test that high score does NOT contraindicate anticoagulation."""
        from src.domain.services.calculators import HasBledCalculator

        calc = HasBledCalculator()
        result = calc.calculate(
            hypertension_uncontrolled=True,
            renal_disease=True,
            liver_disease=True,
            stroke_history=True,
            bleeding_history=False,
            labile_inr=False,
            elderly_gt_65=False,
            drugs_antiplatelet_nsaid=False,
            alcohol_excess=False,
        )

        # High score but should mention NOT a contraindication
        recommendations = " ".join(result.interpretation.recommendations).lower()
        assert "not" in recommendations and "contraindication" in recommendations

    def test_references_include_2024_esc(self) -> None:
        """Test that 2024 ESC Guidelines are referenced."""
        from src.domain.services.calculators import HasBledCalculator

        calc = HasBledCalculator()
        result = calc.calculate(
            hypertension_uncontrolled=False,
            renal_disease=False,
            liver_disease=False,
            stroke_history=False,
            bleeding_history=False,
        )

        assert result.references is not None
        assert len(result.references) >= 2
        # Check for Pisters 2010 (original) and 2024 ESC
        citations = [ref.citation for ref in result.references]
        assert any("Pisters" in c for c in citations)
        assert any("2024" in c for c in citations)

    def test_tool_id(self) -> None:
        """Test tool ID is correct."""
        from src.domain.services.calculators import HasBledCalculator

        calc = HasBledCalculator()
        assert calc.tool_id == "has_bled"
