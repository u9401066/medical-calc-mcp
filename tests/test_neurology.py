from typing import Any
"""
Tests for Neurology Calculators

Tests NIHSS and other neurology-related calculators.
"""



class TestNihssCalculator:
    """Tests for NIHSS (NIH Stroke Scale) Calculator."""

    def test_no_stroke_symptoms(self) -> None:
        """Test NIHSS score 0 - no stroke symptoms."""
        from src.domain.services.calculators import NihssCalculator

        calc = NihssCalculator()
        result = calc.calculate(
            loc=0,
            loc_questions=0,
            loc_commands=0,
            best_gaze=0,
            visual_fields=0,
            facial_palsy=0,
            motor_arm_left=0,
            motor_arm_right=0,
            motor_leg_left=0,
            motor_leg_right=0,
            limb_ataxia=0,
            sensory=0,
            best_language=0,
            dysarthria=0,
            extinction_inattention=0
        )

        assert result.value is not None
        assert result.value == 0
        assert result.interpretation.summary is not None
        assert "no stroke" in result.interpretation.summary.lower()

    def test_minor_stroke(self) -> None:
        """Test NIHSS score 1-4 - minor stroke."""
        from src.domain.services.calculators import NihssCalculator

        calc = NihssCalculator()
        result = calc.calculate(
            loc=0,
            loc_questions=1,
            loc_commands=0,
            best_gaze=0,
            visual_fields=0,
            facial_palsy=1,
            motor_arm_left=0,
            motor_arm_right=0,
            motor_leg_left=0,
            motor_leg_right=0,
            limb_ataxia=0,
            sensory=1,
            best_language=0,
            dysarthria=1,
            extinction_inattention=0
        )

        assert result.value is not None
        assert result.value == 4
        assert result.interpretation.summary is not None
        assert "minor" in result.interpretation.summary.lower()

    def test_moderate_stroke(self) -> None:
        """Test NIHSS score 5-15 - moderate stroke."""
        from src.domain.services.calculators import NihssCalculator

        calc = NihssCalculator()
        result = calc.calculate(
            loc=1,
            loc_questions=1,
            loc_commands=0,
            best_gaze=1,
            visual_fields=1,
            facial_palsy=2,
            motor_arm_left=2,
            motor_arm_right=0,
            motor_leg_left=2,
            motor_leg_right=0,
            limb_ataxia=1,
            sensory=1,
            best_language=1,
            dysarthria=1,
            extinction_inattention=0
        )

        assert result.value is not None
        assert 5 <= result.value <= 15
        assert result.interpretation.summary is not None
        assert "moderate" in result.interpretation.summary.lower()

    def test_moderate_severe_stroke(self) -> None:
        """Test NIHSS score 16-20 - moderate to severe stroke."""
        from src.domain.services.calculators import NihssCalculator

        calc = NihssCalculator()
        result = calc.calculate(
            loc=2,
            loc_questions=2,
            loc_commands=1,
            best_gaze=1,
            visual_fields=2,
            facial_palsy=2,
            motor_arm_left=3,
            motor_arm_right=0,
            motor_leg_left=3,
            motor_leg_right=0,
            limb_ataxia=0,  # can't test if plegic
            sensory=1,
            best_language=2,
            dysarthria=1,
            extinction_inattention=0
        )

        assert result.value is not None
        assert 16 <= result.value <= 20

    def test_severe_stroke(self) -> None:
        """Test NIHSS score 21-42 - severe stroke."""
        from src.domain.services.calculators import NihssCalculator

        calc = NihssCalculator()
        result = calc.calculate(
            loc=3,
            loc_questions=2,
            loc_commands=2,
            best_gaze=2,
            visual_fields=3,
            facial_palsy=3,
            motor_arm_left=4,
            motor_arm_right=4,
            motor_leg_left=4,
            motor_leg_right=4,
            limb_ataxia=0,  # can't test
            sensory=2,
            best_language=3,
            dysarthria=2,
            extinction_inattention=2
        )

        assert result.value is not None
        assert result.value >= 21
        assert result.interpretation.summary is not None
        assert "severe" in result.interpretation.summary.lower()

    def test_right_hemispheric_stroke_pattern(self) -> None:
        """Test typical right hemispheric stroke: left-sided weakness."""
        from src.domain.services.calculators import NihssCalculator

        calc = NihssCalculator()
        result = calc.calculate(
            loc=0,
            loc_questions=0,
            loc_commands=0,
            best_gaze=1,  # Partial gaze palsy
            visual_fields=1,  # Partial hemianopia
            facial_palsy=2,  # Left facial weakness
            motor_arm_left=3,  # Left arm weakness
            motor_arm_right=0,
            motor_leg_left=3,  # Left leg weakness
            motor_leg_right=0,
            limb_ataxia=0,
            sensory=1,  # Left-sided sensory loss
            best_language=0,  # Usually preserved in right MCA
            dysarthria=1,
            extinction_inattention=2  # Left neglect
        )

        assert result.value is not None
        assert result.value > 0
        assert result.calculation_details is not None
        details = result.calculation_details
        assert result.calculation_details is not None
        assert details["left_motor_total"] > 0
        assert details["right_motor_total"] == 0

    def test_left_hemispheric_stroke_pattern(self) -> None:
        """Test typical left hemispheric stroke: right-sided weakness + aphasia."""
        from src.domain.services.calculators import NihssCalculator

        calc = NihssCalculator()
        result = calc.calculate(
            loc=0,
            loc_questions=1,
            loc_commands=1,
            best_gaze=1,
            visual_fields=1,
            facial_palsy=2,  # Right facial weakness
            motor_arm_left=0,
            motor_arm_right=3,  # Right arm weakness
            motor_leg_left=0,
            motor_leg_right=3,  # Right leg weakness
            limb_ataxia=0,
            sensory=1,
            best_language=2,  # Aphasia - hallmark of left MCA
            dysarthria=1,
            extinction_inattention=0
        )

        assert result.value is not None
        assert result.value > 0
        assert result.calculation_details is not None
        details = result.calculation_details
        assert result.calculation_details is not None
        assert details["right_motor_total"] > 0
        assert result.calculation_details is not None
        assert details["left_motor_total"] == 0
        assert details["component_scores"]["9_best_language"] > 0

    def test_max_score(self) -> None:
        """Test NIHSS maximum score of 42."""
        from src.domain.services.calculators import NihssCalculator

        calc = NihssCalculator()
        result = calc.calculate(
            loc=3,
            loc_questions=2,
            loc_commands=2,
            best_gaze=2,
            visual_fields=3,
            facial_palsy=3,
            motor_arm_left=4,
            motor_arm_right=4,
            motor_leg_left=4,
            motor_leg_right=4,
            limb_ataxia=2,
            sensory=2,
            best_language=3,
            dysarthria=2,
            extinction_inattention=2
        )

        assert result.value is not None
        assert result.value == 42

    def test_has_references(self) -> None:
        """Test that NIHSS includes Brott 1989 reference."""
        from src.domain.services.calculators import NihssCalculator

        calc = NihssCalculator()
        result = calc.calculate(
            loc=0,
            loc_questions=0,
            loc_commands=0,
            best_gaze=0,
            visual_fields=0,
            facial_palsy=0,
            motor_arm_left=0,
            motor_arm_right=0,
            motor_leg_left=0,
            motor_leg_right=0,
            limb_ataxia=0,
            sensory=0,
            best_language=0,
            dysarthria=0,
            extinction_inattention=0
        )

        assert result.references is not None
        assert len(result.references) >= 1
        ref_text = str(result.references[0])
        assert "Brott" in ref_text or "2749846" in ref_text

    def test_tool_id(self) -> None:
        """Test tool ID is correct."""
        from src.domain.services.calculators import NihssCalculator

        calc = NihssCalculator()
        assert calc.tool_id == "nihss"

    def test_calculation_details_include_subscores(self) -> None:
        """Test that calculation details include all subscores."""
        from src.domain.services.calculators import NihssCalculator

        calc = NihssCalculator()
        result = calc.calculate(
            loc=1,
            loc_questions=1,
            loc_commands=1,
            best_gaze=0,
            visual_fields=1,
            facial_palsy=1,
            motor_arm_left=2,
            motor_arm_right=0,
            motor_leg_left=2,
            motor_leg_right=0,
            limb_ataxia=0,
            sensory=1,
            best_language=1,
            dysarthria=1,
            extinction_inattention=0
        )

        assert result.calculation_details is not None
        details = result.calculation_details
        assert details is not None
        assert "component_scores" in details
        component_scores = details["component_scores"]
        assert component_scores is not None
        assert "1a_loc" in component_scores
        assert "1b_loc_questions" in component_scores
        assert "1c_loc_commands" in component_scores
        assert "5a_motor_arm_left" in component_scores
        assert "5b_motor_arm_right" in component_scores
        assert "6a_motor_leg_left" in component_scores
        assert "6b_motor_leg_right" in component_scores


class TestAbcd2Calculator:
    """Tests for ABCD2 Score (TIA Stroke Risk) Calculator."""

    def test_low_risk_score_0(self) -> None:
        """Test ABCD2 score 0 - very low risk."""
        from src.domain.services.calculators import Abcd2Calculator

        calc = Abcd2Calculator()
        result = calc.calculate(
            age_gte_60=False,
            bp_gte_140_90=False,
            clinical_features="none",
            duration_minutes="lt_10",
            diabetes=False
        )

        assert result.value is not None
        assert result.value == 0
        assert result.interpretation.summary is not None
        assert "low" in result.interpretation.summary.lower()

    def test_low_risk_score_3(self) -> None:
        """Test ABCD2 score 3 - low risk upper bound."""
        from src.domain.services.calculators import Abcd2Calculator

        calc = Abcd2Calculator()
        result = calc.calculate(
            age_gte_60=True,    # +1
            bp_gte_140_90=True, # +1
            clinical_features="speech_only",  # +1
            duration_minutes="lt_10",
            diabetes=False
        )

        assert result.value is not None
        assert result.value == 3
        assert result.interpretation.summary is not None
        assert "low" in result.interpretation.summary.lower()

    def test_moderate_risk_score_4(self) -> None:
        """Test ABCD2 score 4 - moderate risk lower bound."""
        from src.domain.services.calculators import Abcd2Calculator

        calc = Abcd2Calculator()
        result = calc.calculate(
            age_gte_60=True,    # +1
            bp_gte_140_90=True, # +1
            clinical_features="unilateral_weakness",  # +2
            duration_minutes="lt_10",
            diabetes=False
        )

        assert result.value is not None
        assert result.value == 4
        assert result.interpretation.summary is not None
        assert "moderate" in result.interpretation.summary.lower()

    def test_moderate_risk_score_5(self) -> None:
        """Test ABCD2 score 5 - moderate risk."""
        from src.domain.services.calculators import Abcd2Calculator

        calc = Abcd2Calculator()
        result = calc.calculate(
            age_gte_60=True,    # +1
            bp_gte_140_90=True, # +1
            clinical_features="unilateral_weakness",  # +2
            duration_minutes="lt_10",
            diabetes=True       # +1
        )

        assert result.value is not None
        assert result.value == 5
        assert result.interpretation.summary is not None
        assert "moderate" in result.interpretation.summary.lower()

    def test_high_risk_score_6(self) -> None:
        """Test ABCD2 score 6 - high risk."""
        from src.domain.services.calculators import Abcd2Calculator

        calc = Abcd2Calculator()
        result = calc.calculate(
            age_gte_60=True,    # +1
            bp_gte_140_90=True, # +1
            clinical_features="unilateral_weakness",  # +2
            duration_minutes="10_to_59",  # +1
            diabetes=True       # +1
        )

        assert result.value is not None
        assert result.value == 6
        assert result.interpretation.summary is not None
        assert "high" in result.interpretation.summary.lower()

    def test_high_risk_score_7_max(self) -> None:
        """Test ABCD2 maximum score 7 - high risk."""
        from src.domain.services.calculators import Abcd2Calculator

        calc = Abcd2Calculator()
        result = calc.calculate(
            age_gte_60=True,    # +1
            bp_gte_140_90=True, # +1
            clinical_features="unilateral_weakness",  # +2
            duration_minutes="gte_60",  # +2
            diabetes=True       # +1
        )

        assert result.value is not None
        assert result.value == 7
        assert result.interpretation.summary is not None
        assert "high" in result.interpretation.summary.lower()

    def test_stroke_risk_values_included(self) -> None:
        """Test that 2-day and 7-day stroke risks are in calculation details."""
        from src.domain.services.calculators import Abcd2Calculator

        calc = Abcd2Calculator()
        result = calc.calculate(
            age_gte_60=True,
            bp_gte_140_90=True,
            clinical_features="unilateral_weakness",
            duration_minutes="gte_60",
            diabetes=True
        )

        assert result.calculation_details is not None
        details = result.calculation_details
        assert details is not None
        assert "stroke_risk_2day" in details
        assert "stroke_risk_7day" in details
        assert "stroke_risk_90day" in details

    def test_component_scores_breakdown(self) -> None:
        """Test that component scores are broken down correctly."""
        from src.domain.services.calculators import Abcd2Calculator

        calc = Abcd2Calculator()
        result = calc.calculate(
            age_gte_60=True,
            bp_gte_140_90=False,
            clinical_features="speech_only",
            duration_minutes="10_to_59",
            diabetes=True
        )

        assert result.calculation_details is not None
        details = result.calculation_details
        assert details is not None
        assert "component_scores" in details
        components = details["component_scores"]
        assert components is not None
        assert components["A_age"] == 1
        assert components["B_blood_pressure"] == 0
        assert components["C_clinical_features"] == 1
        assert components["D1_duration"] == 1
        assert components["D2_diabetes"] == 1

    def test_tool_id(self) -> None:
        """Test tool ID is correct."""
        from src.domain.services.calculators import Abcd2Calculator

        calc = Abcd2Calculator()
        assert calc.tool_id == "abcd2"

    def test_has_references(self) -> None:
        """Test that ABCD2 includes Johnston 2007 reference."""
        from src.domain.services.calculators import Abcd2Calculator

        calc = Abcd2Calculator()
        result = calc.calculate(
            age_gte_60=False,
            bp_gte_140_90=False,
            clinical_features="none",
            duration_minutes="lt_10",
            diabetes=False
        )

        assert result.references is not None
        assert len(result.references) >= 1
        ref_text = str(result.references[0])
        assert "Johnston" in ref_text or "17258668" in ref_text


class TestModifiedRankinScaleCalculator:
    """Tests for Modified Rankin Scale (mRS) Calculator."""

    def test_mrs_0_no_symptoms(self) -> None:
        """Test mRS 0 - no symptoms."""
        from src.domain.services.calculators import ModifiedRankinScaleCalculator

        calc = ModifiedRankinScaleCalculator()
        result = calc.calculate(mrs_score=0)

        assert result.value is not None
        assert result.value == 0
        assert result.interpretation.summary is not None
        assert "no symptoms" in result.interpretation.summary.lower()
        assert result.calculation_details is not None
        assert result.calculation_details["favorable_outcome"] is True

    def test_mrs_1_no_significant_disability(self) -> None:
        """Test mRS 1 - no significant disability."""
        from src.domain.services.calculators import ModifiedRankinScaleCalculator

        calc = ModifiedRankinScaleCalculator()
        result = calc.calculate(mrs_score=1)

        assert result.value is not None
        assert result.value == 1
        assert result.calculation_details is not None
        assert result.calculation_details["favorable_outcome"] is True
        assert result.calculation_details is not None
        assert result.calculation_details["independent"] is True

    def test_mrs_2_slight_disability(self) -> None:
        """Test mRS 2 - slight disability (still favorable)."""
        from src.domain.services.calculators import ModifiedRankinScaleCalculator

        calc = ModifiedRankinScaleCalculator()
        result = calc.calculate(mrs_score=2)

        assert result.value is not None
        assert result.value == 2
        assert result.interpretation.summary is not None
        assert "slight" in result.interpretation.summary.lower()
        assert result.calculation_details is not None
        assert result.calculation_details["favorable_outcome"] is True

    def test_mrs_3_moderate_disability(self) -> None:
        """Test mRS 3 - moderate disability (not favorable)."""
        from src.domain.services.calculators import ModifiedRankinScaleCalculator

        calc = ModifiedRankinScaleCalculator()
        result = calc.calculate(mrs_score=3)

        assert result.value is not None
        assert result.value == 3
        assert result.interpretation.summary is not None
        assert "moderate" in result.interpretation.summary.lower()
        assert result.calculation_details is not None
        assert result.calculation_details["favorable_outcome"] is False
        assert result.calculation_details is not None
        assert result.calculation_details["ambulatory"] is True

    def test_mrs_4_moderately_severe_disability(self) -> None:
        """Test mRS 4 - moderately severe disability."""
        from src.domain.services.calculators import ModifiedRankinScaleCalculator

        calc = ModifiedRankinScaleCalculator()
        result = calc.calculate(mrs_score=4)

        assert result.value is not None
        assert result.value == 4
        assert result.calculation_details is not None
        assert result.calculation_details["favorable_outcome"] is False
        assert result.calculation_details is not None
        assert result.calculation_details["ambulatory"] is False

    def test_mrs_5_severe_disability(self) -> None:
        """Test mRS 5 - severe disability."""
        from src.domain.services.calculators import ModifiedRankinScaleCalculator

        calc = ModifiedRankinScaleCalculator()
        result = calc.calculate(mrs_score=5)

        assert result.value is not None
        assert result.value == 5
        assert result.interpretation.summary is not None
        assert "severe" in result.interpretation.summary.lower()
        assert result.calculation_details is not None
        assert result.calculation_details["favorable_outcome"] is False

    def test_mrs_6_dead(self) -> None:
        """Test mRS 6 - dead."""
        from src.domain.services.calculators import ModifiedRankinScaleCalculator

        calc = ModifiedRankinScaleCalculator()
        result = calc.calculate(mrs_score=6)

        assert result.value is not None
        assert result.value == 6
        assert result.interpretation.summary is not None
        assert "dead" in result.interpretation.summary.lower()

    def test_tool_id(self) -> None:
        """Test tool ID is correct."""
        from src.domain.services.calculators import ModifiedRankinScaleCalculator

        calc = ModifiedRankinScaleCalculator()
        assert calc.tool_id == "modified_rankin_scale"

    def test_has_references(self) -> None:
        """Test that mRS includes van Swieten 1988 reference."""
        from src.domain.services.calculators import ModifiedRankinScaleCalculator

        calc = ModifiedRankinScaleCalculator()
        result = calc.calculate(mrs_score=0)

        assert result.references is not None
        assert len(result.references) >= 1


