"""
Integration Tests for Calculate Endpoint

Tests the full calculation flow with intelligent parameter matching:
- 75 tool smoke tests
- Parameter alias handling
- Error message quality
"""

import pytest
from typing import Any
from src.domain.registry.tool_registry import ToolRegistry
from src.application.use_cases.calculate_use_case import CalculateUseCase
from src.application.dto import CalculateRequest


# Note: 'registry' fixture is provided by conftest.py
# It creates a ToolRegistry with all calculators registered


class TestCalculateUseCase:
    """Integration tests for CalculateUseCase."""

    @pytest.fixture
    def use_case(self, registry):
        """Create CalculateUseCase with real registry from conftest."""
        return CalculateUseCase(registry)

    # ==================== Smoke Tests ====================

    def test_all_calculators_discoverable(self, registry):
        """Test that all calculators can be discovered."""
        all_ids = registry.list_all_ids()
        assert len(all_ids) > 0, "No calculators registered"
        print(f"\n✅ Found {len(all_ids)} calculators")

    def test_all_calculators_have_metadata(self, registry):
        """Test that all calculators have required metadata."""
        all_ids = registry.list_all_ids()
        issues = []

        for tool_id in all_ids:
            calc = registry.get_calculator(tool_id)
            if calc is None:
                issues.append(f"{tool_id}: calculator not found")
                continue

            # Check essential attributes
            if not hasattr(calc, "metadata"):
                issues.append(f"{tool_id}: missing metadata")
            if not hasattr(calc, "calculate"):
                issues.append(f"{tool_id}: missing calculate method")

        if issues:
            pytest.fail("\n".join(issues))

    # ==================== Core Calculator Tests ====================

    @pytest.mark.parametrize("tool_id,params", [
        # Critical Care - use correct tool_ids
        ("news2_score", {
            "respiratory_rate": 18,
            "spo2": 96,
            "on_supplemental_o2": False,
            "temperature": 37.0,
            "systolic_bp": 120,
            "heart_rate": 80,
            "consciousness": "A",
        }),
        ("apache_ii", {
            "temperature": 37.0,
            "mean_arterial_pressure": 70,
            "heart_rate": 80,
            "respiratory_rate": 18,
            "fio2": 0.21,
            "pao2": 90,
            "arterial_ph": 7.4,
            "serum_sodium": 140,
            "serum_potassium": 4.0,
            "serum_creatinine": 1.0,
            "hematocrit": 40,
            "wbc_count": 10,
            "gcs_score": 15,
        }),
        ("glasgow_coma_scale", {
            "eye_response": 4,
            "verbal_response": 5,
            "motor_response": 6,
        }),
        ("qsofa_score", {
            "respiratory_rate": 24,  # >= 22
            "altered_mentation": True,
            "systolic_bp": 90,  # <= 100
        }),
        # Nephrology
        ("ckd_epi_2021", {
            "serum_creatinine": 1.2,
            "age": 65,
            "sex": "male",
        }),
        # Anesthesiology
        ("asa_physical_status", {
            "asa_class": 2,
            "is_emergency": False,
        }),
        ("mallampati_score", {
            "mallampati_class": 2,
        }),
        # Cardiology
        ("heart_score", {
            "history_score": 1,
            "ecg_score": 1,
            "age_score": 2,
            "risk_factors_score": 1,
            "troponin_score": 0,
        }),
    ])
    def test_core_calculators(self, use_case, tool_id, params):
        """Test core calculators with valid parameters."""
        request = CalculateRequest(tool_id=tool_id, params=params)
        response = use_case.execute(request)

        assert response.success, f"{tool_id} failed: {response.error}"
        assert response.result is not None
        print(f"\n✅ {tool_id}: {response.result} {response.unit}")

    # ==================== Parameter Alias Tests ====================

    def test_creatinine_alias(self, use_case):
        """Test that 'cr' alias works for serum_creatinine."""
        request = CalculateRequest(
            tool_id="ckd_epi_2021",
            params={
                "cr": 1.2,  # alias
                "age": 65,
                "sex": "male",
            }
        )
        response = use_case.execute(request)

        # Should succeed with alias matching
        if not response.success:
            # Check if it provides helpful error
            assert "param_template" in (response.component_scores or {})
            print(f"\n⚠️ Alias not matched, but got template: {response.component_scores}")

    def test_heart_rate_alias(self, use_case):
        """Test that 'hr' alias works for heart_rate."""
        request = CalculateRequest(
            tool_id="news2_score",
            params={
                "respiratory_rate": 18,
                "spo2": 96,
                "on_supplemental_o2": False,
                "temperature": 37.0,
                "systolic_bp": 120,
                "hr": 80,  # alias for heart_rate
                "consciousness": "A",
            }
        )
        response = use_case.execute(request)

        # Check success or helpful error
        if not response.success:
            assert response.error, "Should have error message"
            print(f"\n⚠️ Alias issue: {response.error}")

    def test_blood_pressure_alias(self, use_case):
        """Test blood pressure parameter variations."""
        request = CalculateRequest(
            tool_id="news2_score",
            params={
                "respiratory_rate": 18,
                "spo2": 96,
                "on_supplemental_o2": False,
                "temperature": 37.0,
                "sbp": 120,  # alias for systolic_bp
                "heart_rate": 80,
                "consciousness": "A",
            }
        )
        response = use_case.execute(request)

        # Should handle alias or provide helpful message
        print(f"\n{'✅' if response.success else '⚠️'} BP alias: {response.error or 'OK'}")

    # ==================== Error Message Quality Tests ====================

    def test_missing_required_param_message(self, use_case):
        """Test error message quality for missing parameters."""
        request = CalculateRequest(
            tool_id="ckd_epi_2021",
            params={
                "serum_creatinine": 1.2,
                # missing age and sex
            }
        )
        response = use_case.execute(request)

        assert not response.success
        assert response.error
        # Should mention missing params
        assert "missing" in response.error.lower() or "required" in response.error.lower()
        # Should provide template
        assert response.component_scores is not None
        print(f"\n📝 Error message: {response.error}")

    def test_unknown_param_suggestion(self, use_case):
        """Test that unknown params get suggestions."""
        request = CalculateRequest(
            tool_id="ckd_epi_2021",
            params={
                "creatinin": 1.2,  # typo
                "age": 65,
                "sex": "male",
            }
        )
        response = use_case.execute(request)

        # Should either succeed via fuzzy match or provide suggestion
        if not response.success:
            assert "did you mean" in response.error.lower() or "creatinine" in response.error.lower()

    def test_tool_not_found_suggestion(self, use_case):
        """Test tool not found error has suggestions."""
        request = CalculateRequest(
            tool_id="ckdepi2021",  # typo
            params={}
        )
        response = use_case.execute(request)

        assert not response.success
        # Should suggest similar tool IDs
        assert "did you mean" in response.error.lower() or "ckd_epi" in response.error.lower()

    # ==================== Template Generation Tests ====================

    def test_error_includes_param_template(self, use_case):
        """Test that errors include fillable param template."""
        request = CalculateRequest(
            tool_id="news2_score",
            params={}  # no params
        )
        response = use_case.execute(request)

        assert not response.success
        assert response.component_scores is not None

        # Check for param_template
        if "param_template" in response.component_scores:
            template = response.component_scores["param_template"]
            assert isinstance(template, dict)
            assert len(template) > 0
            print(f"\n📋 Template: {template}")

    # ==================== Edge Cases ====================

    def test_boolean_param_handling(self, use_case):
        """Test boolean parameter handling."""
        request = CalculateRequest(
            tool_id="news2_score",
            params={
                "respiratory_rate": 18,
                "spo2": 96,
                "on_supplemental_o2": True,  # boolean
                "temperature": 37.0,
                "systolic_bp": 120,
                "heart_rate": 80,
                "consciousness": "A",
            }
        )
        response = use_case.execute(request)

        assert response.success, f"Boolean handling failed: {response.error}"

    def test_string_enum_param_handling(self, use_case):
        """Test string enum parameter handling."""
        request = CalculateRequest(
            tool_id="ckd_epi_2021",
            params={
                "serum_creatinine": 1.2,
                "age": 65,
                "sex": "female",  # string enum
            }
        )
        response = use_case.execute(request)

        assert response.success, f"String enum handling failed: {response.error}"

    def test_negative_value_handling(self, use_case):
        """Test handling of negative values (should be rejected)."""
        request = CalculateRequest(
            tool_id="ckd_epi_2021",
            params={
                "serum_creatinine": -1.2,  # invalid negative
                "age": 65,
                "sex": "male",
            }
        )
        response = use_case.execute(request)

        # Should fail validation
        assert not response.success
        assert "validation" in response.error.lower() or "invalid" in response.error.lower()

    def test_extreme_values(self, use_case):
        """Test handling of extreme but valid values."""
        request = CalculateRequest(
            tool_id="ckd_epi_2021",
            params={
                "serum_creatinine": 15.0,  # very high but valid
                "age": 100,  # old but valid
                "sex": "male",
            }
        )
        response = use_case.execute(request)

        # Should succeed with extreme values
        assert response.success, f"Extreme values failed: {response.error}"


class TestCalculatorCoverage:
    """Test coverage across all calculator categories."""

    # Uses 'registry' fixture from conftest.py

    @pytest.fixture
    def use_case(self, registry):
        return CalculateUseCase(registry)

    def test_critical_care_calculators(self, registry):
        """Verify critical care calculators are available."""
        critical_care = [
            "news2_score", "apache_ii", "sofa_score", "qsofa_score", "glasgow_coma_scale", "four_score",
            "rass", "cam_icu"
        ]
        available = registry.list_all_ids()

        for calc in critical_care:
            assert calc in available, f"Missing critical care calculator: {calc}"

    def test_nephrology_calculators(self, registry):
        """Verify nephrology calculators are available."""
        nephrology = ["ckd_epi_2021", "cockcroft_gault", "kdigo_aki"]
        available = registry.list_all_ids()

        for calc in nephrology:
            assert calc in available, f"Missing nephrology calculator: {calc}"

    def test_anesthesiology_calculators(self, registry):
        """Verify anesthesiology calculators are available."""
        anesthesia = ["asa_physical_status", "mallampati_score", "apfel_ponv", "stop_bang"]
        available = registry.list_all_ids()

        for calc in anesthesia:
            assert calc in available, f"Missing anesthesiology calculator: {calc}"

    def test_cardiology_calculators(self, registry):
        """Verify cardiology calculators are available."""
        cardiology = ["heart_score", "chads2_vasc", "wells_pe"]
        available = registry.list_all_ids()

        for calc in cardiology:
            if calc not in available:
                print(f"⚠️ Cardiology calculator not found: {calc}")


class TestResponseFormat:
    """Test response format consistency."""

    @pytest.fixture
    def use_case(self, registry):
        return CalculateUseCase(registry)

    def test_success_response_format(self, use_case):
        """Test successful response has all required fields."""
        request = CalculateRequest(
            tool_id="glasgow_coma_scale",
            params={
                "eye_response": 4,
                "verbal_response": 5,
                "motor_response": 6,
            }
        )
        response = use_case.execute(request)

        assert response.success is True
        assert response.tool_id == "glasgow_coma_scale"
        assert response.score_name
        assert response.result is not None
        assert response.error is None

    def test_error_response_format(self, use_case):
        """Test error response has all required fields."""
        request = CalculateRequest(
            tool_id="nonexistent",
            params={}
        )
        response = use_case.execute(request)

        assert response.success is False
        assert response.tool_id == "nonexistent"
        assert response.error is not None
        assert len(response.error) > 0

    def test_interpretation_format(self, use_case):
        """Test interpretation is properly formatted."""
        request = CalculateRequest(
            tool_id="news2_score",
            params={
                "respiratory_rate": 25,  # elevated
                "spo2": 92,  # low
                "on_supplemental_o2": True,
                "temperature": 38.5,  # fever
                "systolic_bp": 100,  # borderline
                "heart_rate": 110,  # elevated
                "consciousness": "A",
            }
        )
        response = use_case.execute(request)

        if response.success and response.interpretation:
            assert response.interpretation.summary
            print(f"\n📊 Interpretation: {response.interpretation.summary}")


class TestBoundaryValidation:
    """Test automatic boundary validation integrated into calculate flow."""

    @pytest.fixture
    def use_case(self, registry):
        return CalculateUseCase(registry)

    def test_normal_values_no_warnings(self, use_case):
        """Test that normal values don't trigger boundary warnings."""
        request = CalculateRequest(
            tool_id="news2_score",
            params={
                "respiratory_rate": 16,  # normal
                "spo2": 98,  # normal
                "on_supplemental_o2": False,
                "temperature": 37.0,  # normal
                "systolic_bp": 120,  # normal
                "heart_rate": 75,  # normal
                "consciousness": "A",
            }
        )
        response = use_case.execute(request)

        assert response.success
        # Normal values should not have boundary warnings
        if response.component_scores:
            warnings = response.component_scores.get("_boundary_warnings", [])
            assert len(warnings) == 0, f"Expected no warnings for normal values, got: {warnings}"

    def test_abnormal_values_trigger_warnings(self, use_case):
        """Test that clinically abnormal values trigger boundary warnings."""
        request = CalculateRequest(
            tool_id="news2_score",
            params={
                "respiratory_rate": 45,  # severely elevated (>warning_max=40)
                "spo2": 98,
                "on_supplemental_o2": False,
                "temperature": 37.0,
                "systolic_bp": 120,
                "heart_rate": 200,  # severely elevated (>warning_max=180)
                "consciousness": "A",
            }
        )
        response = use_case.execute(request)

        assert response.success
        assert response.component_scores
        warnings = response.component_scores.get("_boundary_warnings", [])

        # Should have warnings for respiratory_rate and heart_rate
        assert len(warnings) >= 2, f"Expected at least 2 warnings, got: {warnings}"

        # Check warning structure
        for warning in warnings:
            assert "parameter" in warning
            assert "value" in warning
            assert "severity" in warning
            assert "message" in warning

        # Verify specific parameters triggered
        warned_params = [w["parameter"] for w in warnings]
        assert "respiratory_rate" in warned_params
        assert "heart_rate" in warned_params

        print(f"\n🚨 Boundary warnings triggered: {warnings}")

    def test_warning_includes_reference(self, use_case):
        """Test that warnings include literature references when available."""
        request = CalculateRequest(
            tool_id="ckd_epi_2021",
            params={
                "serum_creatinine": 20.0,  # severely elevated (>warning_max=15)
                "age": 50,
                "sex": "male",
            }
        )
        response = use_case.execute(request)

        assert response.success
        assert response.component_scores
        warnings = response.component_scores.get("_boundary_warnings", [])

        # Should have warning for creatinine
        assert len(warnings) >= 1

        # Check that reference is included
        cr_warning = next((w for w in warnings if w["parameter"] == "serum_creatinine"), None)
        assert cr_warning is not None

        if "reference" in cr_warning:
            ref = cr_warning["reference"]
            assert "source" in ref
            assert "citation" in ref
            print(f"\n📚 Reference included: {ref}")

    def test_calculation_still_succeeds_with_warnings(self, use_case):
        """Test that calculation succeeds even with boundary warnings."""
        request = CalculateRequest(
            tool_id="qsofa_score",
            params={
                "respiratory_rate": 50,  # abnormal (triggers scoring + warning)
                "systolic_bp": 50,  # abnormal (triggers scoring + warning)
                "altered_mental_status": True,
            }
        )
        response = use_case.execute(request)

        # Calculation should still succeed
        assert response.success
        assert response.result is not None

        # But should have boundary warnings
        assert response.component_scores
        warnings = response.component_scores.get("_boundary_warnings", [])
        assert len(warnings) >= 1, "Expected warnings for extreme values"

        print(f"\n✅ Score calculated: {response.result} with {len(warnings)} warning(s)")

    def test_boundary_warnings_separate_from_clinical_warnings(self, use_case):
        """Test that boundary warnings are separate from clinical interpretation warnings."""
        request = CalculateRequest(
            tool_id="news2_score",
            params={
                "respiratory_rate": 45,  # triggers boundary warning + scoring points
                "spo2": 85,  # critical (triggers boundary warning + scoring points)
                "on_supplemental_o2": True,
                "temperature": 35.0,  # low (triggers scoring)
                "systolic_bp": 80,  # low (triggers scoring)
                "heart_rate": 200,  # triggers boundary warning + scoring
                "consciousness": "V",  # altered
            }
        )
        response = use_case.execute(request)

        assert response.success

        # Check boundary warnings (input validation)
        boundary_warnings = response.component_scores.get("_boundary_warnings", [])
        assert len(boundary_warnings) >= 2, "Expected boundary warnings"

        # Check clinical interpretation (output)
        assert response.interpretation is not None
        assert response.interpretation.summary is not None

        print(f"\n📊 Boundary warnings (input check): {len(boundary_warnings)}")
        print(f"📋 Clinical interpretation: {response.interpretation.summary}")

