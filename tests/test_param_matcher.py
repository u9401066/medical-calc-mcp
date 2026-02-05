"""
Unit Tests for ParamMatcher

Tests the intelligent parameter matching functionality:
- Exact match
- Alias match
- Suffix stripping
- Prefix/suffix partial match
- Fuzzy match
"""

from typing import Any

import pytest

from src.domain.services.param_matcher import (
    PARAM_ALIASES,
    UNIT_SUFFIXES,
    ParamMatcher,
    ParamMatchResult,
    generate_param_template,
    get_param_matcher,
)

# =============================================================================
# Mock Calculator Classes (using real method signatures)
# =============================================================================

class MockCalculatorBase:
    """Base class for mock calculators."""
    pass


class MockCKDCalculator(MockCalculatorBase):
    """Mock CKD-EPI calculator with realistic signature."""

    def calculate(
        self,
        serum_creatinine: float,
        age: int,
        sex: str,
        is_black: bool = False,
    ) -> dict[str, Any]:
        return {"egfr": 90}


class MockNEWS2Calculator(MockCalculatorBase):
    """Mock NEWS2 calculator with realistic signature."""

    def calculate(
        self,
        respiratory_rate: int,
        spo2: int,
        on_supplemental_o2: bool,
        temperature: float,
        systolic_bp: int,
        heart_rate: int,
        consciousness: str = "A",
    ) -> dict[str, Any]:
        return {"score": 5}


class MockSimpleCalculator(MockCalculatorBase):
    """Simple mock calculator for basic tests."""

    def calculate(
        self,
        param1: int,
        param2: float,
        optional_param: str = "default",
    ) -> dict[str, Any]:
        return {"result": param1 + param2}


class TestParamAliases:
    """Test PARAM_ALIASES configuration."""

    def test_common_aliases_exist(self):
        """Verify common parameter aliases are defined."""
        # Creatinine variations
        assert "serum_creatinine" in PARAM_ALIASES
        assert "creatinine" in PARAM_ALIASES["serum_creatinine"]
        assert "cr" in PARAM_ALIASES["serum_creatinine"]
        assert "scr" in PARAM_ALIASES["serum_creatinine"]

        # Blood pressure
        assert "systolic_bp" in PARAM_ALIASES
        assert "sbp" in PARAM_ALIASES["systolic_bp"]

        # Heart rate
        assert "heart_rate" in PARAM_ALIASES
        assert "hr" in PARAM_ALIASES["heart_rate"]
        assert "pulse" in PARAM_ALIASES["heart_rate"]

    def test_no_duplicate_aliases(self):
        """Ensure no alias maps to multiple canonical names."""
        all_aliases = {}
        for canonical, aliases in PARAM_ALIASES.items():
            for alias in aliases:
                if alias in all_aliases:
                    pytest.fail(
                        f"Alias '{alias}' maps to both "
                        f"'{all_aliases[alias]}' and '{canonical}'"
                    )
                all_aliases[alias] = canonical


class TestUnitSuffixes:
    """Test UNIT_SUFFIXES configuration."""

    def test_common_suffixes_exist(self):
        """Verify common unit suffixes are defined."""
        assert "_mg_dl" in UNIT_SUFFIXES
        assert "_mmhg" in UNIT_SUFFIXES
        assert "_percent" in UNIT_SUFFIXES
        assert "_mg_kg" in UNIT_SUFFIXES


class TestParamMatcher:
    """Test ParamMatcher class."""

    @pytest.fixture
    def matcher(self):
        """Create a ParamMatcher instance."""
        return ParamMatcher(fuzzy_threshold=0.8)

    @pytest.fixture
    def ckd_calculator(self):
        """Create a mock CKD calculator."""
        return MockCKDCalculator()

    @pytest.fixture
    def news2_calculator(self):
        """Create a mock NEWS2 calculator."""
        return MockNEWS2Calculator()

    @pytest.fixture
    def simple_calculator(self):
        """Create a simple mock calculator."""
        return MockSimpleCalculator()

    def test_exact_match(self, matcher, ckd_calculator):
        """Test exact parameter matching."""
        params = {
            "serum_creatinine": 1.2,
            "age": 65,
            "sex": "male",
        }
        result = matcher.match(params, ckd_calculator)

        assert result.success is True
        assert result.matched_params["serum_creatinine"] == 1.2
        assert result.matched_params["age"] == 65
        assert result.matched_params["sex"] == "male"

    def test_alias_match(self, matcher, ckd_calculator):
        """Test alias-based parameter matching."""
        params = {
            "cr": 1.2,  # alias for serum_creatinine
            "age": 65,
            "sex": "male",
        }
        result = matcher.match(params, ckd_calculator)

        assert result.success is True
        assert result.matched_params["serum_creatinine"] == 1.2
        assert result.match_details["cr"] == "serum_creatinine"

    def test_suffix_stripping(self, matcher, ckd_calculator):
        """Test suffix stripping for unit variations."""
        params = {
            "creatinine_mg_dl": 1.2,  # should match serum_creatinine via alias
            "age": 65,
            "sex": "male",
        }
        result = matcher.match(params, ckd_calculator)

        assert result.success is True
        assert result.matched_params["serum_creatinine"] == 1.2

    def test_prefix_match(self, matcher, ckd_calculator):
        """Test prefix-based partial matching."""
        params = {
            "creatinine": 1.2,  # suffix of serum_creatinine
            "age": 65,
            "sex": "male",
        }
        result = matcher.match(params, ckd_calculator)

        assert result.success is True
        assert result.matched_params["serum_creatinine"] == 1.2

    def test_fuzzy_match(self, matcher, ckd_calculator):
        """Test fuzzy matching for typos."""
        params = {
            "serum_creatinin": 1.2,  # typo (missing 'e')
            "age": 65,
            "sex": "male",
        }
        result = matcher.match(params, ckd_calculator)

        assert result.success is True
        assert result.matched_params["serum_creatinine"] == 1.2

    def test_missing_required_param(self, matcher, ckd_calculator):
        """Test failure when required parameter is missing."""
        params = {
            "serum_creatinine": 1.2,
            # age is missing
            "sex": "male",
        }
        result = matcher.match(params, ckd_calculator)

        assert result.success is False
        assert "age" in result.missing_required

    def test_optional_param_not_required(self, matcher, ckd_calculator):
        """Test that optional parameters are not required."""
        params = {
            "serum_creatinine": 1.2,
            "age": 65,
            "sex": "male",
            # is_black has default, not required
        }
        result = matcher.match(params, ckd_calculator)

        assert result.success is True

    def test_unknown_param_suggestions(self, matcher, ckd_calculator):
        """Test suggestions for unknown parameters."""
        params = {
            "serum_creatinine": 1.2,
            "age": 65,
            "sex": "male",
            "unknown_param": 123,
        }
        result = matcher.match(params, ckd_calculator)

        # Should still succeed (all required matched)
        assert result.success is True
        # But report unmatched
        assert "unknown_param" in result.unmatched_provided

    def test_case_insensitive_matching(self, matcher, ckd_calculator):
        """Test case-insensitive parameter matching."""
        params = {
            "Serum_Creatinine": 1.2,  # different case
            "AGE": 65,
            "Sex": "male",
        }
        result = matcher.match(params, ckd_calculator)

        assert result.success is True
        assert result.matched_params["serum_creatinine"] == 1.2
        assert result.matched_params["age"] == 65


class TestGenerateParamTemplate:
    """Test generate_param_template function."""

    def test_template_generation(self):
        """Test parameter template generation."""
        calc = MockCKDCalculator()
        template = generate_param_template(calc)

        assert "serum_creatinine" in template
        assert "age" in template
        assert "sex" in template
        assert "is_black" in template

        # Check required vs optional
        assert "required" in template["serum_creatinine"]
        assert "required" in template["age"]
        assert "default" in template["is_black"] or "optional" in template["is_black"]

    def test_template_type_hints(self):
        """Test template includes type information."""
        calc = MockSimpleCalculator()
        template = generate_param_template(calc)

        assert "param1" in template
        assert "param2" in template
        assert "integer" in template["param1"]
        assert "number" in template["param2"]


class TestGetParamMatcher:
    """Test singleton pattern for ParamMatcher."""

    def test_singleton(self):
        """Test that get_param_matcher returns same instance."""
        matcher1 = get_param_matcher()
        matcher2 = get_param_matcher()

        assert matcher1 is matcher2

    def test_instance_type(self):
        """Test that get_param_matcher returns ParamMatcher."""
        matcher = get_param_matcher()
        assert isinstance(matcher, ParamMatcher)


class TestParamMatchResult:
    """Test ParamMatchResult dataclass."""

    def test_success_result(self):
        """Test successful match result."""
        result = ParamMatchResult(
            success=True,
            matched_params={"a": 1, "b": 2},
            match_details={"a": "a", "b": "b"},
            unmatched_provided=[],
            missing_required=[],
            suggestions={},
        )

        assert result.success is True
        assert result.matched_params == {"a": 1, "b": 2}

    def test_failure_result(self):
        """Test failed match result."""
        result = ParamMatchResult(
            success=False,
            matched_params={},
            match_details={},
            unmatched_provided=["unknown"],
            missing_required=["required_param"],
            suggestions={"unknown": ["required_param"]},
        )

        assert result.success is False
        assert "required_param" in result.missing_required
        assert "unknown" in result.suggestions


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def matcher(self):
        return ParamMatcher()

    @pytest.fixture
    def simple_calculator(self):
        return MockSimpleCalculator()

    def test_empty_params(self, matcher, simple_calculator):
        """Test with empty parameters."""
        result = matcher.match({}, simple_calculator)

        assert result.success is False
        assert "param1" in result.missing_required
        assert "param2" in result.missing_required

    def test_none_value_params(self, matcher, simple_calculator):
        """Test with None values in parameters."""
        result = matcher.match(
            {"param1": None, "param2": None},
            simple_calculator
        )

        # Should accept None as a value (type checking is calculator's job)
        assert result.matched_params.get("param1") is None
        assert result.matched_params.get("param2") is None

    def test_numeric_string_params(self, matcher, simple_calculator):
        """Test with numeric string values."""
        result = matcher.match(
            {"param1": "65", "param2": "1.5"},
            simple_calculator
        )

        # Should preserve the value as-is (type conversion is calculator's job)
        assert result.matched_params.get("param1") == "65"
        assert result.matched_params.get("param2") == "1.5"

    def test_hyphen_to_underscore(self, matcher):
        """Test that hyphens are converted to underscores."""

        class HyphenTestCalculator:
            def calculate(self, param_with_underscore: int) -> dict:
                return {"result": param_with_underscore}

        calc = HyphenTestCalculator()
        result = matcher.match({"param-with-underscore": 42}, calc)

        assert result.success is True
        assert result.matched_params["param_with_underscore"] == 42


class TestAliasMatching:
    """Test specific alias matching scenarios."""

    @pytest.fixture
    def matcher(self):
        return ParamMatcher()

    def test_hr_to_heart_rate(self, matcher):
        """Test hr alias matches heart_rate."""
        calc = MockNEWS2Calculator()
        params = {
            "respiratory_rate": 18,
            "spo2": 96,
            "on_supplemental_o2": False,
            "temperature": 37.0,
            "systolic_bp": 120,
            "hr": 80,  # alias
            "consciousness": "A",
        }
        result = matcher.match(params, calc)

        assert result.success is True
        assert result.matched_params["heart_rate"] == 80

    def test_sbp_to_systolic_bp(self, matcher):
        """Test sbp alias matches systolic_bp."""
        calc = MockNEWS2Calculator()
        params = {
            "respiratory_rate": 18,
            "spo2": 96,
            "on_supplemental_o2": False,
            "temperature": 37.0,
            "sbp": 120,  # alias
            "heart_rate": 80,
            "consciousness": "A",
        }
        result = matcher.match(params, calc)

        assert result.success is True
        assert result.matched_params["systolic_bp"] == 120

    def test_multiple_aliases_in_same_request(self, matcher):
        """Test multiple aliases work together."""
        calc = MockNEWS2Calculator()
        params = {
            "rr": 18,  # alias for respiratory_rate
            "spo2": 96,
            "on_supplemental_o2": False,
            "temp": 37.0,  # might need alias
            "sbp": 120,  # alias
            "hr": 80,  # alias
            "consciousness": "A",
        }
        result = matcher.match(params, calc)

        # Check that aliases were resolved
        assert result.matched_params.get("respiratory_rate") == 18
        assert result.matched_params.get("heart_rate") == 80
        assert result.matched_params.get("systolic_bp") == 120

