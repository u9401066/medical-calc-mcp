"""
Tests for Neurology Calculators

Tests NIHSS and other neurology-related calculators.
"""

import pytest


class TestNihssCalculator:
    """Tests for NIHSS (NIH Stroke Scale) Calculator."""

    def test_no_stroke_symptoms(self):
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
        
        assert result.value == 0
        assert "no stroke" in result.interpretation.summary.lower()

    def test_minor_stroke(self):
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
        
        assert result.value == 4
        assert "minor" in result.interpretation.summary.lower()

    def test_moderate_stroke(self):
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
        
        assert 5 <= result.value <= 15
        assert "moderate" in result.interpretation.summary.lower()

    def test_moderate_severe_stroke(self):
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
        
        assert 16 <= result.value <= 20

    def test_severe_stroke(self):
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
        
        assert result.value >= 21
        assert "severe" in result.interpretation.summary.lower()

    def test_right_hemispheric_stroke_pattern(self):
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
        
        assert result.value > 0
        details = result.calculation_details
        assert details["left_motor_total"] > 0
        assert details["right_motor_total"] == 0

    def test_left_hemispheric_stroke_pattern(self):
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
        
        assert result.value > 0
        details = result.calculation_details
        assert details["right_motor_total"] > 0
        assert details["left_motor_total"] == 0
        assert details["component_scores"]["9_best_language"] > 0

    def test_max_score(self):
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
        
        assert result.value == 42

    def test_has_references(self):
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

    def test_tool_id(self):
        """Test tool ID is correct."""
        from src.domain.services.calculators import NihssCalculator
        
        calc = NihssCalculator()
        assert calc.tool_id == "nihss"

    def test_calculation_details_include_subscores(self):
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
        
        details = result.calculation_details
        assert "component_scores" in details
        component_scores = details["component_scores"]
        assert "1a_loc" in component_scores
        assert "1b_loc_questions" in component_scores
        assert "1c_loc_commands" in component_scores
        assert "5a_motor_arm_left" in component_scores
        assert "5b_motor_arm_right" in component_scores
        assert "6a_motor_leg_left" in component_scores
        assert "6b_motor_leg_right" in component_scores
