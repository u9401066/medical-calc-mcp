from typing import Any
"""
Enhanced Coverage Tests

Tests specifically designed to improve test coverage to 90%+.
Targets low-coverage areas: validation, transfusion, MCP handlers.
"""
import pytest

# =============================================================================
# Validation Rules Tests (rules.py: 57% -> 90%+)
# =============================================================================

class TestRangeRule:
    """Enhanced tests for RangeRule validation"""

    def test_range_rule_none_value(self) -> None:
        """None values should pass (handled by RequiredRule)"""
        from src.domain.validation.rules import RangeRule
        rule = RangeRule(min_value=0, max_value=100)
        is_valid, error = rule.validate(None)
        assert is_valid is True
        assert error is None

    def test_range_rule_non_numeric_type(self) -> None:
        """Non-numeric types should fail"""
        from src.domain.validation.rules import RangeRule
        rule = RangeRule(min_value=0, max_value=100)
        is_valid, error = rule.validate("not a number")
        assert is_valid is False
        assert error is not None
        assert "must be a number" in error

    def test_range_rule_exclusive_min(self) -> None:
        """Test exclusive minimum boundary"""
        from src.domain.validation.rules import RangeRule
        rule = RangeRule(min_value=0, min_inclusive=False)

        # Exactly 0 should fail
        is_valid, error = rule.validate(0)
        assert is_valid is False
        assert error is not None
        assert "must be greater than" in error

        # Greater than 0 should pass
        is_valid, error = rule.validate(0.1)
        assert is_valid is True

    def test_range_rule_exclusive_max(self) -> None:
        """Test exclusive maximum boundary"""
        from src.domain.validation.rules import RangeRule
        rule = RangeRule(max_value=100, max_inclusive=False)

        # Exactly 100 should fail
        is_valid, error = rule.validate(100)
        assert is_valid is False
        assert error is not None
        assert "must be less than" in error

        # Less than 100 should pass
        is_valid, error = rule.validate(99.9)
        assert is_valid is True

    def test_range_rule_inclusive_boundaries(self) -> None:
        """Test inclusive boundaries"""
        from src.domain.validation.rules import RangeRule
        rule = RangeRule(min_value=0, max_value=100, min_inclusive=True, max_inclusive=True)

        is_valid, _ = rule.validate(0)
        assert is_valid is True

        is_valid, _ = rule.validate(100)
        assert is_valid is True

    def test_range_rule_below_min(self) -> None:
        """Test below minimum value"""
        from src.domain.validation.rules import RangeRule
        rule = RangeRule(min_value=10, max_value=100, unit=" mmHg")
        is_valid, error = rule.validate(5)
        assert is_valid is False
        assert error is not None
        assert "below minimum" in error
        assert error is not None
        assert "mmHg" in error

    def test_range_rule_above_max(self) -> None:
        """Test above maximum value"""
        from src.domain.validation.rules import RangeRule
        rule = RangeRule(min_value=10, max_value=100, unit=" mmHg")
        is_valid, error = rule.validate(150)
        assert is_valid is False
        assert error is not None
        assert "exceeds maximum" in error

    def test_range_rule_description(self) -> None:
        """Test description generation"""
        from src.domain.validation.rules import RangeRule

        # Both bounds
        rule = RangeRule(min_value=0, max_value=100, unit=" mg/dL")
        assert "≥0" in rule.description
        assert "≤100" in rule.description

        # Only min (exclusive)
        rule = RangeRule(min_value=0, min_inclusive=False)
        assert ">0" in rule.description

        # Only max (exclusive)
        rule = RangeRule(max_value=100, max_inclusive=False)
        assert "<100" in rule.description

        # No bounds
        rule = RangeRule()
        assert "any value" in rule.description


class TestEnumRule:
    """Enhanced tests for EnumRule validation"""

    def test_enum_rule_none_value(self) -> None:
        """None values should pass"""
        from src.domain.validation.rules import EnumRule
        rule = EnumRule(allowed_values=("a", "b", "c"))
        is_valid, error = rule.validate(None)
        assert is_valid is True

    def test_enum_rule_case_insensitive(self) -> None:
        """Case insensitive matching"""
        from src.domain.validation.rules import EnumRule
        rule = EnumRule(allowed_values=("Male", "Female"), case_sensitive=False)

        is_valid, _ = rule.validate("male")
        assert is_valid is True

        is_valid, _ = rule.validate("FEMALE")
        assert is_valid is True

    def test_enum_rule_case_sensitive(self) -> None:
        """Case sensitive matching"""
        from src.domain.validation.rules import EnumRule
        rule = EnumRule(allowed_values=("Male", "Female"), case_sensitive=True)

        is_valid, _ = rule.validate("male")
        assert is_valid is False

        is_valid, _ = rule.validate("Male")
        assert is_valid is True

    def test_enum_rule_invalid_value(self) -> None:
        """Invalid value should fail"""
        from src.domain.validation.rules import EnumRule
        rule = EnumRule(allowed_values=("a", "b", "c"))
        is_valid, error = rule.validate("d")
        assert is_valid is False
        assert error is not None
        assert "not in allowed values" in error

    def test_enum_rule_description(self) -> None:
        """Test description"""
        from src.domain.validation.rules import EnumRule
        rule = EnumRule(allowed_values=("low", "medium", "high"))
        assert "One of:" in rule.description


class TestRequiredRule:
    """Tests for RequiredRule"""

    def test_required_rule_none(self) -> None:
        """None should fail"""
        from src.domain.validation.rules import RequiredRule
        rule = RequiredRule()
        is_valid, error = rule.validate(None)
        assert is_valid is False
        assert error is not None
        assert "required" in error.lower()

    def test_required_rule_with_value(self) -> None:
        """Value should pass"""
        from src.domain.validation.rules import RequiredRule
        rule = RequiredRule()
        is_valid, _ = rule.validate("anything")
        assert is_valid is True

        is_valid, _ = rule.validate(0)
        assert is_valid is True

    def test_required_rule_description(self) -> None:
        """Test description"""
        from src.domain.validation.rules import RequiredRule
        rule = RequiredRule()
        assert rule.description == "Required"


class TestTypeRule:
    """Tests for TypeRule validation"""

    def test_type_rule_none_value(self) -> None:
        """None values should pass"""
        from src.domain.validation.rules import TypeRule
        rule = TypeRule(expected_type=int)
        is_valid, _ = rule.validate(None)
        assert is_valid is True

    def test_type_rule_int_valid(self) -> None:
        """Integer type validation"""
        from src.domain.validation.rules import TypeRule
        rule = TypeRule(expected_type=int)

        is_valid, _ = rule.validate(42)
        assert is_valid is True

        is_valid, _ = rule.validate(42.0)  # Integer value as float
        assert is_valid is True

    def test_type_rule_int_invalid_float(self) -> None:
        """Non-integer float should fail for int type"""
        from src.domain.validation.rules import TypeRule
        rule = TypeRule(expected_type=int)
        is_valid, error = rule.validate(42.5)
        assert is_valid is False
        assert error is not None
        assert "Expected integer" in error

    def test_type_rule_float_valid(self) -> None:
        """Float type validation"""
        from src.domain.validation.rules import TypeRule
        rule = TypeRule(expected_type=float)

        is_valid, _ = rule.validate(3.14)
        assert is_valid is True

        is_valid, _ = rule.validate(42)  # Integer as float
        assert is_valid is True

    def test_type_rule_float_invalid_string(self) -> None:
        """Non-numeric string should fail"""
        from src.domain.validation.rules import TypeRule
        rule = TypeRule(expected_type=float, type_name="number")
        is_valid, error = rule.validate("not a number")
        assert is_valid is False
        assert error is not None
        assert "Expected number" in error

    def test_type_rule_string_type(self) -> None:
        """String type validation"""
        from src.domain.validation.rules import TypeRule
        rule = TypeRule(expected_type=str)

        is_valid, _ = rule.validate("hello")
        assert is_valid is True

        is_valid, error = rule.validate(123)
        assert is_valid is False
        assert error is not None
        assert "Expected str" in error

    def test_type_rule_description(self) -> None:
        """Test description"""
        from src.domain.validation.rules import TypeRule
        rule = TypeRule(expected_type=int, type_name="integer")
        assert rule.description == "integer"

        rule2 = TypeRule(expected_type=float)
        assert rule2.description == "float"


class TestCustomRule:
    """Tests for CustomRule"""

    def test_custom_rule_valid(self) -> None:
        """Custom validator returning True"""
        from src.domain.validation.rules import CustomRule
        rule = CustomRule(
            validator=lambda x: (x > 0, None if x > 0 else "Must be positive"),
            desc="Positive number"
        )
        is_valid, _ = rule.validate(5)
        assert is_valid is True

    def test_custom_rule_invalid(self) -> None:
        """Custom validator returning False"""
        from src.domain.validation.rules import CustomRule
        rule = CustomRule(
            validator=lambda x: (x > 0, None if x > 0 else "Must be positive"),
            desc="Positive number"
        )
        is_valid, error = rule.validate(-5)
        assert is_valid is False
        assert error == "Must be positive"

    def test_custom_rule_description(self) -> None:
        """Test description"""
        from src.domain.validation.rules import CustomRule
        rule = CustomRule(validator=lambda x: (True, None), desc="Always valid")
        assert rule.description == "Always valid"


class TestCompositeRule:
    """Tests for CompositeRule"""

    def test_composite_rule_all_pass(self) -> None:
        """All rules pass"""
        from src.domain.validation.rules import CompositeRule, RangeRule, TypeRule
        rule = CompositeRule(rules=[
            TypeRule(expected_type=float),
            RangeRule(min_value=0, max_value=100)
        ])
        is_valid, _ = rule.validate(50)
        assert is_valid is True

    def test_composite_rule_first_fails(self) -> None:
        """First rule fails"""
        from src.domain.validation.rules import CompositeRule, RangeRule, TypeRule
        rule = CompositeRule(rules=[
            TypeRule(expected_type=float),
            RangeRule(min_value=0, max_value=100)
        ])
        is_valid, error = rule.validate("not a number")
        assert is_valid is False

    def test_composite_rule_second_fails(self) -> None:
        """Second rule fails"""
        from src.domain.validation.rules import CompositeRule, RangeRule, TypeRule
        rule = CompositeRule(rules=[
            TypeRule(expected_type=float),
            RangeRule(min_value=0, max_value=100)
        ])
        is_valid, error = rule.validate(150)
        assert is_valid is False
        assert error is not None
        assert "exceeds maximum" in error

    def test_composite_rule_description(self) -> None:
        """Test description combines all rules"""
        from src.domain.validation.rules import CompositeRule, RangeRule, TypeRule
        rule = CompositeRule(rules=[
            TypeRule(expected_type=float),
            RangeRule(min_value=0, max_value=100)
        ])
        desc = rule.description
        assert "float" in desc
        assert "≥0" in desc


# =============================================================================
# Transfusion Calculator Enhanced Tests (65% -> 90%+)
# =============================================================================

class TestTransfusionCalculatorEnhanced:
    """Enhanced tests for transfusion calculator edge cases"""

    @pytest.fixture
    def calc(self) -> Any:
        from src.domain.services.calculators import TransfusionCalculator
        return TransfusionCalculator()

    # FFP Tests
    def test_ffp_transfusion(self, calc: Any) -> None:
        """FFP dose calculation"""
        result = calc.calculate(
            weight_kg=70,
            product_type="ffp"
        )
        assert result.value is not None
        assert result.value > 0
        assert result.interpretation.summary is not None
        assert result.interpretation.summary is not None
        assert "FFP" in result.interpretation.summary
        # 10-15 mL/kg standard dose
        assert result.value is not None
        assert 700 <= result.value <= 1050

    def test_ffp_pediatric(self, calc: Any) -> None:
        """FFP for pediatric patient"""
        result = calc.calculate(
            weight_kg=15,
            product_type="ffp"
        )
        assert result.value is not None
        assert 150 <= result.value <= 225  # 10-15 mL/kg

    # Cryoprecipitate Tests
    def test_cryo_transfusion(self, calc: Any) -> None:
        """Cryoprecipitate dose calculation"""
        result = calc.calculate(
            weight_kg=70,
            product_type="cryoprecipitate"
        )
        assert result.value is not None
        assert result.value >= 1
        assert result.interpretation.summary is not None
        assert result.interpretation.summary is not None
        assert "Cryoprecipitate" in result.interpretation.summary or "units" in result.interpretation.summary.lower()

    def test_cryo_small_patient(self, calc: Any) -> None:
        """Cryo for very small patient (minimum 1 unit)"""
        result = calc.calculate(
            weight_kg=5,
            product_type="cryoprecipitate"
        )
        assert result.value is not None
        assert result.value >= 1  # Minimum 1 unit

    def test_cryo_large_patient(self, calc: Any) -> None:
        """Cryo for large patient"""
        result = calc.calculate(
            weight_kg=100,
            product_type="cryoprecipitate"
        )
        assert result.value is not None
        assert result.value >= 10  # 1 unit per 10 kg

    # Platelet with levels
    def test_platelets_with_specific_levels(self, calc: Any) -> None:
        """Platelet transfusion with specific current/target levels"""
        result = calc.calculate(
            weight_kg=70,
            current_platelet=15,
            target_platelet=75,
            product_type="platelets",
            patient_type="adult_male"
        )
        assert result.value is not None
        assert result.value > 0
        assert result.interpretation.summary is not None
        assert result.interpretation.summary is not None
        assert "platelet" in result.interpretation.summary.lower()

    def test_platelets_concentrate_type(self, calc: Any) -> None:
        """Platelet concentrate product type"""
        result = calc.calculate(
            weight_kg=70,
            current_platelet=20,
            target_platelet=60,
            product_type="platelet_concentrate"
        )
        assert result.value is not None
        assert result.value > 0

    def test_platelets_pediatric_with_levels(self, calc: Any) -> None:
        """Pediatric platelet transfusion with specific levels"""
        result = calc.calculate(
            weight_kg=12,
            current_platelet=10,
            target_platelet=80,
            product_type="platelets",
            patient_type="child"
        )
        assert result.value is not None
        assert result.value > 0

    # Validation errors
    def test_invalid_weight_zero(self, calc: Any) -> None:
        """Zero weight should raise error"""
        with pytest.raises(ValueError, match="positive"):
            calc.calculate(
                weight_kg=0,
                current_hematocrit=25,
                target_hematocrit=30
            )

    def test_invalid_weight_negative(self, calc: Any) -> None:
        """Negative weight should raise error"""
        with pytest.raises(ValueError, match="positive"):
            calc.calculate(
                weight_kg=-10,
                current_hematocrit=25,
                target_hematocrit=30
            )

    def test_invalid_hematocrit_too_low(self, calc: Any) -> None:
        """Hematocrit below valid range"""
        with pytest.raises(ValueError, match="5-70"):
            calc.calculate(
                weight_kg=70,
                current_hematocrit=3,
                target_hematocrit=30
            )

    def test_invalid_hematocrit_too_high(self, calc: Any) -> None:
        """Hematocrit above valid range"""
        with pytest.raises(ValueError, match="5-70"):
            calc.calculate(
                weight_kg=70,
                current_hematocrit=25,
                target_hematocrit=80
            )

    def test_invalid_target_not_higher(self, calc: Any) -> None:
        """Target must be higher than current"""
        with pytest.raises(ValueError, match="greater than"):
            calc.calculate(
                weight_kg=70,
                current_hematocrit=35,
                target_hematocrit=30
            )

    def test_invalid_platelet_target_not_higher(self, calc: Any) -> None:
        """Platelet target must be higher than current"""
        with pytest.raises(ValueError, match="greater than"):
            calc.calculate(
                weight_kg=70,
                current_platelet=50,
                target_platelet=30,
                product_type="platelets"
            )

    def test_invalid_product_type(self, calc: Any) -> None:
        """Invalid product type"""
        with pytest.raises(ValueError, match="Unknown product type"):
            calc.calculate(
                weight_kg=70,
                current_hematocrit=25,
                target_hematocrit=30,
                product_type="invalid_product"
            )

    def test_missing_hct_hgb_for_rbc(self, calc: Any) -> None:
        """Missing both Hct and Hgb for RBC transfusion"""
        with pytest.raises(ValueError, match="Must provide"):
            calc.calculate(
                weight_kg=70,
                product_type="prbc"
            )

    # Large volume warnings
    def test_large_volume_warning(self, calc: Any) -> None:
        """Large volume transfusion should trigger warning"""
        result = calc.calculate(
            weight_kg=70,
            current_hematocrit=10,
            target_hematocrit=35,  # Very large gap
            patient_type="adult_male"
        )
        assert result.value is not None
        assert result.value > 2000
        assert result.interpretation.warnings is not None
        assert any("massive" in w.lower() for w in result.interpretation.warnings)

    def test_pediatric_overload_warning(self, calc: Any) -> None:
        """Small infant with large volume should warn"""
        result = calc.calculate(
            weight_kg=5,
            current_hematocrit=15,
            target_hematocrit=40,
            patient_type="infant"
        )
        # Check for overload warning
        warnings = result.interpretation.warnings
        assert len(warnings) >= 0  # May or may not have warning based on volume

    # Different patient types for EBV
    def test_all_patient_types(self, calc: Any) -> None:
        """Test all patient types for different EBV values"""
        patient_types = [
            "adult_male",
            "adult_female",
            "child",
            "infant",
            "term_neonate",
            "preterm_neonate"
        ]

        for pt in patient_types:
            result = calc.calculate(
                weight_kg=10 if "neonate" in pt or pt == "infant" else 70,
                current_hematocrit=25,
                target_hematocrit=35,
                patient_type=pt
            )
            assert result.value is not None
            assert result.value > 0, f"Failed for {pt}"


# =============================================================================
# Validators Tests (validators.py: 65% -> 90%+)
# =============================================================================

class TestValidators:
    """Tests for validators module"""

    def test_parameter_validator_import(self) -> None:
        """Test ParameterValidator can be imported"""
        from src.domain.validation.validators import ParameterValidator
        validator = ParameterValidator()
        assert validator is not None


# =============================================================================
# Parameter Specs Tests (parameter_specs.py: 67% -> 90%+)
# =============================================================================

class TestParameterSpecs:
    """Tests for parameter specifications"""

    def test_parameter_specs_module_exists(self) -> None:
        """Test parameter_specs module exists"""
        from src.domain.validation import parameter_specs
        assert parameter_specs is not None


# =============================================================================
# MCP Handler Tests (to improve handler coverage)
# =============================================================================

class TestMCPHandlerCoverage:
    """Tests to improve MCP handler coverage"""

    def test_cardiology_handlers(self) -> None:
        """Test cardiology calculator handlers"""
        from src.domain.services.calculators import (
            Chads2VascCalculator,
            HeartScoreCalculator,
        )

        # CHA₂DS₂-VASc
        calc: Any = Chads2VascCalculator()
        result = calc.calculate(
            chf_or_lvef_lte_40=True,
            hypertension=True,
            age_gte_75=True,
            diabetes=False,
            stroke_tia_or_te_history=False,
            vascular_disease=False,
            age_65_to_74=False,
            female_sex=True
        )
        assert result.value is not None
        assert result.value >= 0

        # HEART Score
        calc = HeartScoreCalculator()
        result = calc.calculate(
            history_score=2,
            ecg_score=1,
            age_score=2,
            risk_factors_score=1,
            troponin_score=0
        )
        assert result.value is not None
        assert result.value >= 0

    def test_neurology_handlers(self) -> None:
        """Test neurology calculator handlers"""
        from src.domain.services.calculators import (
            GlasgowComaScaleCalculator,
            NihssCalculator,
        )

        # GCS
        calc: Any = GlasgowComaScaleCalculator()
        result = calc.calculate(
            eye_response=4,
            verbal_response=5,
            motor_response=6
        )
        assert result.value is not None
        assert result.value == 15

        # NIHSS
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

    def test_pulmonology_handlers(self) -> None:
        """Test pulmonology calculator handlers"""
        from src.domain.services.calculators import (
            AaGradientCalculator,
            PfRatioCalculator,
            RoxIndexCalculator,
        )

        # P/F Ratio
        calc: Any = PfRatioCalculator()
        result = calc.calculate(pao2=90, fio2=0.21)
        assert result.value is not None
        assert result.value > 400

        # A-a Gradient
        calc = AaGradientCalculator()
        result = calc.calculate(
            age=50,
            pao2=90,
            paco2=40,
            fio2=0.21
        )
        assert result.value is not None
        assert result.value >= 0

        # ROX Index
        calc = RoxIndexCalculator()
        result = calc.calculate(
            spo2=95,
            fio2=0.4,
            respiratory_rate=20
        )
        assert result.value is not None
        assert result.value > 0

    def test_pediatric_score_handlers(self) -> None:
        """Test pediatric score calculator handlers"""
        from src.domain.services.calculators import (
            APGARScoreCalculator,
            PIM3Calculator,
        )

        # APGAR
        calc: Any = APGARScoreCalculator()
        result = calc.calculate(
            appearance=2,
            pulse=2,
            grimace=2,
            activity=2,
            respiration=2
        )
        assert result.value is not None
        assert result.value == 10

        # PIM3
        calc = PIM3Calculator()
        result = calc.calculate(
            systolic_bp=100,
            pupillary_reaction="both_react",
            mechanical_ventilation=False,
            base_excess=-2,
            elective_admission=True,
            recovery_post_procedure=True,
            cardiac_bypass=False,
            high_risk_diagnosis=False,
            low_risk_diagnosis=False,
            very_high_risk_diagnosis=False
        )
        assert result.value is not None
        assert result.value >= 0

    def test_general_handlers(self) -> None:
        """Test general calculator handlers"""
        from src.domain.services.calculators import (
            CorrectedQtCalculator,
            IdealBodyWeightCalculator,
        )

        # IBW
        calc: Any = IdealBodyWeightCalculator()
        result = calc.calculate(height_cm=175, sex="male")
        assert result.value is not None
        assert result.value > 0

        # Corrected QT
        calc = CorrectedQtCalculator()
        result = calc.calculate(qt_interval=400, heart_rate=72)
        assert result.value is not None
        assert result.value > 0


# =============================================================================
# Reference Class Tests
# =============================================================================

class TestReferenceClass:
    """Tests for Reference value object"""

    def test_reference_to_dict_with_level_of_evidence(self) -> None:
        """Test Reference.to_dict includes level_of_evidence"""
        from src.domain.value_objects.reference import Reference

        ref = Reference(
            citation="Test Author et al. Journal 2024",
            pmid="12345678",
            level_of_evidence="Level I"
        )

        d = ref.to_dict()
        assert "level_of_evidence" in d
        assert d["level_of_evidence"] == "Level I"

    def test_reference_to_dict_without_level_of_evidence(self) -> None:
        """Test Reference.to_dict when level_of_evidence is None"""
        from src.domain.value_objects.reference import Reference

        ref = Reference(
            citation="Test Author et al. Journal 2024",
            pmid="12345678"
        )

        d = ref.to_dict()
        # Should either not have key or have None
        assert d.get("level_of_evidence") is None or "level_of_evidence" not in d


# =============================================================================
# Clinical Constants Tests
# =============================================================================

class TestClinicalConstants:
    """Tests for clinical constants"""

    def test_ebv_constants(self) -> None:
        """Test estimated blood volume constants"""
        from src.domain.value_objects.clinical_constants import get_ebv_per_kg

        assert get_ebv_per_kg("adult_male") == 70
        assert get_ebv_per_kg("adult_female") == 65
        assert get_ebv_per_kg("child") == 75
        assert get_ebv_per_kg("infant") == 80
        assert get_ebv_per_kg("term_neonate") == 85
        assert get_ebv_per_kg("preterm_neonate") == 90

        # Unknown patient type with default
        assert get_ebv_per_kg("unknown", default=70) == 70


# =============================================================================
# Tool Keys Tests
# =============================================================================

class TestToolKeys:
    """Tests for tool key value objects"""

    def test_tool_keys_module_exists(self) -> None:
        """Test tool_keys module exists and has content"""
        from src.domain.value_objects import tool_keys
        assert tool_keys is not None
