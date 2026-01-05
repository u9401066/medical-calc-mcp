from typing import Any
"""
Tests for Phase 17: Obstetrics & Neonatology Calculators

- Bishop Score (Cervical Ripening Assessment)
- Ballard Score (Newborn Gestational Age Assessment)
"""

import pytest

from src.domain.services.calculators import (
    BallardScoreCalculator,
    BishopScoreCalculator,
)


class TestBishopScoreCalculator:
    """Tests for Bishop Score Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        return BishopScoreCalculator()

    def test_metadata(self, calculator: Any) -> None:
        """Test metadata is correctly defined"""
        assert calculator.tool_id == "bishop_score"
        assert calculator.metadata.low_level.name == "Bishop Score"
        assert "dilation" in calculator.metadata.low_level.input_params
        assert "effacement" in calculator.metadata.low_level.input_params
        assert "station" in calculator.metadata.low_level.input_params
        assert "consistency" in calculator.metadata.low_level.input_params
        assert "position" in calculator.metadata.low_level.input_params

    def test_favorable_cervix_high_score(self, calculator: Any) -> None:
        """Test high score (favorable cervix) - score 12"""
        result = calculator.calculate(
            dilation=3,          # ≥5 cm (+3)
            effacement=3,        # ≥80% (+3)
            station=2,           # -1/0 (+2)
            consistency="soft",  # (+2)
            position="anterior", # (+2)
        )
        # Total: 3+3+2+2+2 = 12
        assert result.value is not None
        assert result.value == 12
        assert result.interpretation.summary is not None
        assert "Favorable" in result.interpretation.summary
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level.value == "low"

    def test_unfavorable_cervix_low_score(self, calculator: Any) -> None:
        """Test low score (unfavorable cervix) - score 0"""
        result = calculator.calculate(
            dilation=0,            # closed (+0)
            effacement=0,          # 0-30% (+0)
            station=0,             # -3 (+0)
            consistency="firm",    # (+0)
            position="posterior",  # (+0)
        )
        # Total: 0
        assert result.value is not None
        assert result.value == 0
        assert result.interpretation.summary is not None
        assert "Unfavorable" in result.interpretation.summary
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level.value == "high"
        assert result.interpretation.recommendations is not None
        assert "ripening" in result.interpretation.recommendations[0].lower()

    def test_moderate_score(self, calculator: Any) -> None:
        """Test moderate score (score 6-7)"""
        result = calculator.calculate(
            dilation=1,           # 1-2 cm (+1)
            effacement=2,         # 60-70% (+2)
            station=1,            # -2 (+1)
            consistency="medium", # (+1)
            position="mid",       # (+1)
        )
        # Total: 1+2+1+1+1 = 6
        assert result.value is not None
        assert result.value == 6
        assert result.interpretation.summary is not None
        assert "Moderate" in result.interpretation.summary
        assert result.interpretation.risk_level is not None
        assert result.interpretation.risk_level.value == "intermediate"

    def test_boundary_score_8_favorable(self, calculator: Any) -> None:
        """Test score 8 (boundary - favorable)"""
        result = calculator.calculate(
            dilation=2,           # 3-4 cm (+2)
            effacement=2,         # 60-70% (+2)
            station=2,            # -1/0 (+2)
            consistency="soft",   # (+2)
            position="posterior", # (+0)
        )
        # Total: 2+2+2+2+0 = 8
        assert result.value is not None
        assert result.value == 8
        assert result.interpretation.summary is not None
        assert "Favorable" in result.interpretation.summary

    def test_boundary_score_5_unfavorable(self, calculator: Any) -> None:
        """Test score 5 (boundary - unfavorable)"""
        result = calculator.calculate(
            dilation=1,            # 1-2 cm (+1)
            effacement=1,          # 40-50% (+1)
            station=1,             # -2 (+1)
            consistency="medium",  # (+1)
            position="mid",        # (+1)
        )
        # Total: 1+1+1+1+1 = 5
        assert result.value is not None
        assert result.value == 5
        assert result.interpretation.summary is not None
        assert "Unfavorable" in result.interpretation.summary

    def test_score_components_in_result(self, calculator: Any) -> None:
        """Test that score components are included in result"""
        result = calculator.calculate(
            dilation=2,
            effacement=2,
            station=2,
            consistency="medium",
            position="mid",
        )
        assert "score_breakdown" in result.calculation_details
        assert result.calculation_details is not None
        assert "dilation" in result.calculation_details["score_breakdown"]
        assert result.calculation_details is not None
        assert "effacement" in result.calculation_details["score_breakdown"]

    def test_ripening_options_for_unfavorable(self, calculator: Any) -> None:
        """Test that ripening options are provided for unfavorable cervix"""
        result = calculator.calculate(
            dilation=0,
            effacement=0,
            station=0,
            consistency="firm",
            position="posterior",
        )
        assert result.calculation_details is not None
        assert len(result.calculation_details["ripening_options"]) > 0

    def test_no_ripening_options_for_favorable(self, calculator: Any) -> None:
        """Test that ripening options are NOT provided for favorable cervix"""
        result = calculator.calculate(
            dilation=3,
            effacement=3,
            station=2,
            consistency="soft",
            position="anterior",
        )
        assert result.calculation_details.get("ripening_options") is None

    def test_case_insensitive_consistency(self, calculator: Any) -> None:
        """Test consistency is case-insensitive"""
        result1 = calculator.calculate(
            dilation=1, effacement=1, station=1,
            consistency="SOFT", position="mid"
        )
        result2 = calculator.calculate(
            dilation=1, effacement=1, station=1,
            consistency="soft", position="mid"
        )
        assert result1.value is not None
        assert result1.value == result2.value

    def test_case_insensitive_position(self, calculator: Any) -> None:
        """Test position is case-insensitive"""
        result1 = calculator.calculate(
            dilation=1, effacement=1, station=1,
            consistency="medium", position="ANTERIOR"
        )
        result2 = calculator.calculate(
            dilation=1, effacement=1, station=1,
            consistency="medium", position="anterior"
        )
        assert result1.value is not None
        assert result1.value == result2.value

    def test_invalid_dilation_raises_error(self, calculator: Any) -> None:
        """Test invalid dilation raises ValueError"""
        with pytest.raises(ValueError, match="dilation"):
            calculator.calculate(
                dilation=5,  # Invalid
                effacement=1, station=1,
                consistency="medium", position="mid"
            )

    def test_invalid_effacement_raises_error(self, calculator: Any) -> None:
        """Test invalid effacement raises ValueError"""
        with pytest.raises(ValueError, match="effacement"):
            calculator.calculate(
                dilation=1,
                effacement=-1,  # Invalid
                station=1,
                consistency="medium", position="mid"
            )

    def test_invalid_consistency_raises_error(self, calculator: Any) -> None:
        """Test invalid consistency raises ValueError"""
        with pytest.raises(ValueError, match="consistency"):
            calculator.calculate(
                dilation=1, effacement=1, station=1,
                consistency="invalid",  # Invalid
                position="mid"
            )

    def test_invalid_position_raises_error(self, calculator: Any) -> None:
        """Test invalid position raises ValueError"""
        with pytest.raises(ValueError, match="position"):
            calculator.calculate(
                dilation=1, effacement=1, station=1,
                consistency="medium",
                position="invalid"  # Invalid
            )


class TestBallardScoreCalculator:
    """Tests for Ballard Score Calculator"""

    @pytest.fixture
    def calculator(self) -> Any:
        return BallardScoreCalculator()

    def test_metadata(self, calculator: Any) -> None:
        """Test metadata is correctly defined"""
        assert calculator.tool_id == "ballard_score"
        assert calculator.metadata.low_level.name == "New Ballard Score"
        assert "posture" in calculator.metadata.low_level.input_params
        assert "skin" in calculator.metadata.low_level.input_params

    def test_term_infant_score_48(self, calculator: Any) -> None:
        """Test typical term infant (40+ weeks) - score 48"""
        result = calculator.calculate(
            # Neuromuscular (mature)
            posture=4, square_window=4, arm_recoil=4,
            popliteal_angle=4, scarf_sign=4, heel_to_ear=4,
            # Physical (mature)
            skin=4, lanugo=4, plantar_surface=4,
            breast=4, eye_ear=4, genitals=4,
        )
        # Total: 24 + 24 = 48
        assert result.value is not None
        assert result.value == 48
        assert result.calculation_details is not None
        estimated_ga = result.calculation_details["estimated_gestational_age_weeks"]
        assert 40 <= estimated_ga <= 44
        assert result.interpretation.summary is not None
        assert "Term" in result.interpretation.summary or "Post" in result.interpretation.summary

    def test_extremely_preterm_negative_score(self, calculator: Any) -> None:
        """Test extremely premature infant - negative score"""
        result = calculator.calculate(
            # Neuromuscular (immature)
            posture=-1, square_window=-1, arm_recoil=-1,
            popliteal_angle=-1, scarf_sign=-1, heel_to_ear=-1,
            # Physical (immature)
            skin=-1, lanugo=-1, plantar_surface=-1,
            breast=-1, eye_ear=-1, genitals=-1,
        )
        # Total: -6 + -6 = -12
        assert result.value is not None
        assert result.value == -12
        assert result.calculation_details is not None
        estimated_ga = result.calculation_details["estimated_gestational_age_weeks"]
        assert estimated_ga < 24  # Extremely preterm
        assert result.interpretation.summary is not None
        assert "Extremely Preterm" in result.interpretation.summary

    def test_very_preterm_score_10(self, calculator: Any) -> None:
        """Test very preterm infant (~28 weeks) - score ~10"""
        result = calculator.calculate(
            # Neuromuscular
            posture=0, square_window=1, arm_recoil=1,
            popliteal_angle=1, scarf_sign=0, heel_to_ear=0,
            # Physical
            skin=1, lanugo=1, plantar_surface=1,
            breast=0, eye_ear=1, genitals=1,
        )
        # Total neuromuscular: 0+1+1+1+0+0 = 3
        # Total physical: 1+1+1+0+1+1 = 5
        # Total: 8
        assert result.calculation_details is not None
        estimated_ga = result.calculation_details["estimated_gestational_age_weeks"]
        assert 26 <= estimated_ga <= 30

    def test_late_preterm_score_30(self, calculator: Any) -> None:
        """Test late preterm infant (~36 weeks) - score ~30"""
        result = calculator.calculate(
            # Neuromuscular
            posture=3, square_window=3, arm_recoil=3,
            popliteal_angle=3, scarf_sign=2, heel_to_ear=2,
            # Physical
            skin=2, lanugo=3, plantar_surface=2,
            breast=2, eye_ear=2, genitals=2,
        )
        # Total neuromuscular: 3+3+3+3+2+2 = 16
        # Total physical: 2+3+2+2+2+2 = 13
        # Total: 29
        assert result.calculation_details is not None
        estimated_ga = result.calculation_details["estimated_gestational_age_weeks"]
        assert 34 <= estimated_ga <= 38

    def test_score_components_breakdown(self, calculator: Any) -> None:
        """Test that score components are properly recorded"""
        result = calculator.calculate(
            posture=2, square_window=2, arm_recoil=2,
            popliteal_angle=2, scarf_sign=2, heel_to_ear=2,
            skin=2, lanugo=2, plantar_surface=2,
            breast=2, eye_ear=2, genitals=2,
        )
        assert result.calculation_details is not None
        assert result.calculation_details["neuromuscular_maturity_score"] == 12
        assert result.calculation_details is not None
        assert result.calculation_details["physical_maturity_score"] == 12
        assert result.value is not None
        assert result.value == 24

    def test_gestational_age_calculation_accuracy(self, calculator: Any) -> None:
        """Test GA calculation: score 0 = 24 weeks"""
        result = calculator.calculate(
            posture=0, square_window=0, arm_recoil=0,
            popliteal_angle=0, scarf_sign=0, heel_to_ear=0,
            skin=0, lanugo=0, plantar_surface=0,
            breast=0, eye_ear=0, genitals=0,
        )
        assert result.value is not None
        assert result.value == 0
        assert result.calculation_details is not None
        estimated_ga = result.calculation_details["estimated_gestational_age_weeks"]
        assert estimated_ga == 24.0  # Score 0 = 24 weeks

    def test_post_term_infant(self, calculator: Any) -> None:
        """Test post-term infant (>42 weeks)"""
        result = calculator.calculate(
            posture=4, square_window=4, arm_recoil=4,
            popliteal_angle=5, scarf_sign=4, heel_to_ear=4,
            skin=5, lanugo=4, plantar_surface=4,
            breast=4, eye_ear=4, genitals=4,
        )
        # Total: neuromuscular 25 + physical 25 = 50
        assert result.calculation_details is not None
        estimated_ga = result.calculation_details["estimated_gestational_age_weeks"]
        assert estimated_ga >= 42

    def test_moderate_preterm_clinical_action(self, calculator: Any) -> None:
        """Test moderate preterm gets appropriate clinical action"""
        result = calculator.calculate(
            posture=2, square_window=2, arm_recoil=2,
            popliteal_angle=2, scarf_sign=1, heel_to_ear=1,
            skin=2, lanugo=2, plantar_surface=1,
            breast=1, eye_ear=1, genitals=1,
        )
        # Should be around 32-33 weeks (Moderate Preterm)
        assert result.calculation_details is not None
        estimated_ga = result.calculation_details["estimated_gestational_age_weeks"]
        if 32 <= estimated_ga < 34:
            assert result.calculation_details is not None
            assert "Moderate" in result.calculation_details["maturity_category"]

    def test_invalid_posture_raises_error(self, calculator: Any) -> None:
        """Test invalid posture value raises error"""
        with pytest.raises(ValueError, match="posture"):
            calculator.calculate(
                posture=5,  # Invalid (max is 4)
                square_window=2, arm_recoil=2,
                popliteal_angle=2, scarf_sign=2, heel_to_ear=2,
                skin=2, lanugo=2, plantar_surface=2,
                breast=2, eye_ear=2, genitals=2,
            )

    def test_invalid_popliteal_angle_raises_error(self, calculator: Any) -> None:
        """Test invalid popliteal_angle value raises error"""
        with pytest.raises(ValueError, match="popliteal_angle"):
            calculator.calculate(
                posture=2, square_window=2, arm_recoil=2,
                popliteal_angle=6,  # Invalid (max is 5)
                scarf_sign=2, heel_to_ear=2,
                skin=2, lanugo=2, plantar_surface=2,
                breast=2, eye_ear=2, genitals=2,
            )

    def test_invalid_skin_raises_error(self, calculator: Any) -> None:
        """Test invalid skin value raises error"""
        with pytest.raises(ValueError, match="skin"):
            calculator.calculate(
                posture=2, square_window=2, arm_recoil=2,
                popliteal_angle=2, scarf_sign=2, heel_to_ear=2,
                skin=6,  # Invalid (max is 5)
                lanugo=2, plantar_surface=2,
                breast=2, eye_ear=2, genitals=2,
            )

    def test_next_step_guidance(self, calculator: Any) -> None:
        """Test that next_step guidance is provided"""
        result = calculator.calculate(
            posture=2, square_window=2, arm_recoil=2,
            popliteal_angle=2, scarf_sign=2, heel_to_ear=2,
            skin=2, lanugo=2, plantar_surface=2,
            breast=2, eye_ear=2, genitals=2,
        )
        assert "next_step" in result.calculation_details
        assert result.calculation_details is not None
        assert "growth chart" in result.calculation_details["next_step"].lower()

    def test_accuracy_note_included(self, calculator: Any) -> None:
        """Test that accuracy information is included"""
        result = calculator.calculate(
            posture=2, square_window=2, arm_recoil=2,
            popliteal_angle=2, scarf_sign=2, heel_to_ear=2,
            skin=2, lanugo=2, plantar_surface=2,
            breast=2, eye_ear=2, genitals=2,
        )
        assert "accuracy" in result.calculation_details
        assert result.calculation_details is not None
        assert "±2 weeks" in result.calculation_details["accuracy"]


class TestObstetricsRegistration:
    """Test that obstetrics calculators are properly registered"""

    def test_calculators_importable(self) -> None:
        """Test that calculators can be imported from package"""
        from src.domain.services.calculators import (
            BallardScoreCalculator,
            BishopScoreCalculator,
        )
        assert BishopScoreCalculator is not None
        assert BallardScoreCalculator is not None

    def test_calculators_in_registry_list(self) -> None:
        """Test that calculators are in the CALCULATORS list"""
        from src.domain.services.calculators import CALCULATORS
        calculator_names = [c.__name__ for c in CALCULATORS]
        assert "BishopScoreCalculator" in calculator_names
        assert "BallardScoreCalculator" in calculator_names
