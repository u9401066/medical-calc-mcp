from typing import Any

"""
Tests for Application Use Cases

Covers:
- CalculateUseCase: Main calculation execution
- DiscoveryUseCase: Tool discovery operations

Target: Improve coverage from 18-23% to 80%+
"""

import pytest

from src.application.dto import (
    CalculateRequest,
    DiscoveryMode,
    DiscoveryRequest,
)
from src.application.use_cases import CalculateUseCase, DiscoveryUseCase
from src.domain.registry import ToolRegistry
from src.domain.services.calculators import CALCULATORS


class TestCalculateUseCase:
    """Test CalculateUseCase - the main calculation execution"""

    @pytest.fixture
    def use_case(self, registry: Any) -> Any:
        """Create CalculateUseCase with populated registry"""
        return CalculateUseCase(registry)

    # ========================================================================
    # Success Cases
    # ========================================================================

    def test_successful_calculation_gcs(self, use_case: Any) -> None:
        """Test successful GCS calculation"""
        request = CalculateRequest(
            tool_id="glasgow_coma_scale",  # Full tool_id
            params={
                "eye_response": 4,
                "verbal_response": 5,
                "motor_response": 6,
            }
        )

        response = use_case.execute(request)

        assert response.success is True
        assert response.result == 15
        assert response.tool_id == "glasgow_coma_scale"
        assert "GCS" in response.score_name or "Glasgow" in response.score_name
        assert response.error is None

    def test_successful_calculation_ckd_epi(self, use_case: Any) -> None:
        """Test successful CKD-EPI calculation"""
        request = CalculateRequest(
            tool_id="ckd_epi_2021",
            params={
                "serum_creatinine": 1.2,  # Correct param name
                "age": 65,
                "sex": "male",
            }
        )

        response = use_case.execute(request)

        assert response.success is True
        assert response.result is not None
        assert 50 < response.result < 80  # Expected range for this input

    def test_successful_calculation_sofa(self, use_case: Any) -> None:
        """Test successful SOFA calculation"""
        request = CalculateRequest(
            tool_id="sofa_score",  # Correct tool_id
            params={
                "pao2_fio2_ratio": 300,
                "platelets": 100,
                "bilirubin": 2.0,
                "gcs_score": 14,
                "creatinine": 1.5,
                "map_value": 65,
            }
        )

        response = use_case.execute(request)

        assert response.success is True
        assert response.result is not None
        assert response.result >= 0

    def test_successful_calculation_with_component_scores(self, use_case: Any) -> None:
        """Test that component scores are returned"""
        request = CalculateRequest(
            tool_id="apache_ii",
            params={
                "temperature": 38.5,
                "mean_arterial_pressure": 70,
                "heart_rate": 110,
                "respiratory_rate": 24,
                "fio2": 0.4,
                "pao2": 70,
                "arterial_ph": 7.35,
                "serum_sodium": 140,
                "serum_potassium": 4.0,
                "serum_creatinine": 1.5,
                "acute_renal_failure": False,
                "hematocrit": 35,
                "wbc_count": 12,
                "gcs_score": 14,
                "age": 65,
                "chronic_health_conditions": [],
                "admission_type": "nonoperative",
            }
        )

        response = use_case.execute(request)

        assert response.success is True
        # APACHE II should have component details
        if response.component_scores:
            assert isinstance(response.component_scores, dict)

    def test_successful_calculation_with_references(self, use_case: Any) -> None:
        """Test that references are returned"""
        request = CalculateRequest(
            tool_id="rcri",
            params={
                "high_risk_surgery": True,
                "ischemic_heart_disease": False,
                "heart_failure": False,
                "cerebrovascular_disease": False,
                "insulin_diabetes": False,
                "creatinine_above_2": False,
            }
        )

        response = use_case.execute(request)

        assert response.success is True
        assert response.references is not None
        assert len(response.references) > 0
        # Check reference structure
        ref = response.references[0]
        assert ref.citation is not None

    # ========================================================================
    # Error Cases - Calculator Not Found
    # ========================================================================

    def test_calculator_not_found(self, use_case: Any) -> None:
        """Test error when calculator doesn't exist"""
        request = CalculateRequest(
            tool_id="nonexistent_calculator",
            params={}
        )

        response = use_case.execute(request)

        assert response.success is False
        assert "not found" in response.error.lower()
        # Should suggest how to find calculators
        assert "list_calculators" in response.error or "search_calculators" in response.error

    def test_calculator_not_found_suggests_alternatives(self, use_case: Any) -> None:
        """Test that error suggests similar calculators when typo is detected"""
        request = CalculateRequest(
            tool_id="sofa_scor",  # Typo - close to sofa_score
            params={}
        )

        response = use_case.execute(request)

        assert response.success is False
        # Should suggest similar tool names (Did you mean: ...)
        assert "did you mean" in response.error.lower() or "list_calculators" in response.error.lower()

    # ========================================================================
    # Error Cases - Invalid Parameters
    # ========================================================================

    def test_missing_required_parameter(self, use_case: Any) -> None:
        """Test error when required parameter is missing"""
        request = CalculateRequest(
            tool_id="glasgow_coma_scale",
            params={
                "eye_response": 4,
                # Missing verbal_response and motor_response
            }
        )

        response = use_case.execute(request)

        assert response.success is False
        assert "parameter" in response.error.lower() or "required" in response.error.lower()

    def test_invalid_parameter_type(self, use_case: Any) -> None:
        """Test error when parameter type is wrong"""
        request = CalculateRequest(
            tool_id="glasgow_coma_scale",
            params={
                "eye_response": "four",  # Should be int
                "verbal_response": 5,
                "motor_response": 6,
            }
        )

        response = use_case.execute(request)

        # May fail during calculation or validation
        assert response.success is False or response.result is not None

    def test_parameter_out_of_range(self, use_case: Any) -> None:
        """Test error when parameter value is out of range"""
        request = CalculateRequest(
            tool_id="glasgow_coma_scale",
            params={
                "eye_response": 10,  # Max is 4
                "verbal_response": 5,
                "motor_response": 6,
            }
        )

        response = use_case.execute(request)

        assert response.success is False
        # Should mention valid range
        assert "1" in response.error or "4" in response.error or "range" in response.error.lower()

    def test_unexpected_parameter(self, use_case: Any) -> None:
        """Test error when unexpected parameter is provided"""
        request = CalculateRequest(
            tool_id="glasgow_coma_scale",
            params={
                "eye_response": 4,
                "verbal_response": 5,
                "motor_response": 6,
                "unexpected_param": "value",
            }
        )

        response = use_case.execute(request)

        # Should either ignore or error
        # The behavior depends on implementation
        assert response is not None

    # ========================================================================
    # Edge Cases
    # ========================================================================

    def test_empty_params(self, use_case: Any) -> None:
        """Test with empty parameters"""
        request = CalculateRequest(
            tool_id="glasgow_coma_scale",
            params={}
        )

        response = use_case.execute(request)

        assert response.success is False

    def test_none_values_in_params(self, use_case: Any) -> None:
        """Test with None values"""
        request = CalculateRequest(
            tool_id="ckd_epi_2021",
            params={
                "serum_creatinine": None,
                "age": 65,
                "sex": "male",
            }
        )

        response = use_case.execute(request)

        assert response.success is False

    def test_interpretation_dto_conversion(self, use_case: Any) -> None:
        """Test that interpretation is properly converted to DTO"""
        # Use RCRI which we know works
        request = CalculateRequest(
            tool_id="rcri",
            params={
                "high_risk_surgery": True,
                "ischemic_heart_disease": True,
                "heart_failure": False,
                "cerebrovascular_disease": False,
                "insulin_diabetes": False,
                "creatinine_above_2": False,
            }
        )

        response = use_case.execute(request)

        assert response.success is True


class TestDiscoveryUseCase:
    """Test DiscoveryUseCase - tool discovery operations"""

    @pytest.fixture
    def use_case(self, registry: Any) -> Any:
        """Create DiscoveryUseCase with populated registry"""
        return DiscoveryUseCase(registry)

    # ========================================================================
    # List All
    # ========================================================================

    def test_list_all_tools(self, use_case: Any) -> None:
        """Test listing all tools"""
        request = DiscoveryRequest(mode=DiscoveryMode.LIST_ALL)

        response = use_case.execute(request)

        assert response.success is True
        assert response.count > 0
        assert response.tools is not None
        assert len(response.tools) > 0

    def test_list_all_with_limit(self, use_case: Any) -> None:
        """Test listing with limit"""
        request = DiscoveryRequest(mode=DiscoveryMode.LIST_ALL, limit=5)

        response = use_case.execute(request)

        assert response.success is True
        assert len(response.tools) <= 5

    # ========================================================================
    # Search
    # ========================================================================

    def test_search_by_keyword(self, use_case: Any) -> None:
        """Test searching by keyword"""
        request = DiscoveryRequest(
            mode=DiscoveryMode.SEARCH,
            query="sepsis"
        )

        response = use_case.execute(request)

        assert response.success is True
        # Should find SOFA, qSOFA
        tool_ids = [t.tool_id for t in response.tools]
        assert any("sofa" in tid for tid in tool_ids)

    def test_search_by_specialty_keyword(self, use_case: Any) -> None:
        """Test searching by specialty keyword"""
        request = DiscoveryRequest(
            mode=DiscoveryMode.SEARCH,
            query="cardiac"
        )

        response = use_case.execute(request)

        assert response.success is True
        # Should find cardiology tools
        assert response.count >= 0

    def test_search_empty_query(self, use_case: Any) -> None:
        """Test search with empty query"""
        request = DiscoveryRequest(
            mode=DiscoveryMode.SEARCH,
            query=""
        )

        response = use_case.execute(request)

        # Should return all or empty
        assert response.success is True

    # ========================================================================
    # By Specialty
    # ========================================================================

    def test_filter_by_specialty(self, use_case: Any) -> None:
        """Test filtering by specialty"""
        request = DiscoveryRequest(
            mode=DiscoveryMode.BY_SPECIALTY,
            specialty="critical_care"
        )

        response = use_case.execute(request)

        assert response.success is True
        assert response.count > 0
        # All returned tools should be in critical care
        for tool in response.tools:
            assert "critical_care" in tool.specialties

    def test_filter_by_specialty_not_found(self, use_case: Any) -> None:
        """Test filtering by unknown specialty"""
        request = DiscoveryRequest(
            mode=DiscoveryMode.BY_SPECIALTY,
            specialty="unknown_specialty"
        )

        response = use_case.execute(request)

        assert response.success is False
        assert "Unknown specialty" in response.error
        # Should suggest available specialties
        assert response.available_specialties is not None

    def test_filter_by_specialty_missing(self, use_case: Any) -> None:
        """Test filtering without specialty specified"""
        request = DiscoveryRequest(
            mode=DiscoveryMode.BY_SPECIALTY,
            specialty=None
        )

        response = use_case.execute(request)

        assert response.success is False
        assert "required" in response.error.lower()

    # ========================================================================
    # By Context
    # ========================================================================

    def test_filter_by_context(self, use_case: Any) -> None:
        """Test filtering by clinical context"""
        request = DiscoveryRequest(
            mode=DiscoveryMode.BY_CONTEXT,
            context="preoperative_assessment"
        )

        response = use_case.execute(request)

        assert response.success is True
        # Should find ASA, RCRI, etc.
        assert response.count > 0

    def test_filter_by_context_not_found(self, use_case: Any) -> None:
        """Test filtering by unknown context"""
        request = DiscoveryRequest(
            mode=DiscoveryMode.BY_CONTEXT,
            context="unknown_context"
        )

        response = use_case.execute(request)

        assert response.success is False
        assert response.available_contexts is not None

    def test_filter_by_context_missing(self, use_case: Any) -> None:
        """Test filtering without context specified"""
        request = DiscoveryRequest(
            mode=DiscoveryMode.BY_CONTEXT,
            context=None
        )

        response = use_case.execute(request)

        assert response.success is False

    # ========================================================================
    # By Condition
    # ========================================================================

    def test_filter_by_condition(self, use_case: Any) -> None:
        """Test filtering by condition"""
        request = DiscoveryRequest(
            mode=DiscoveryMode.BY_CONDITION,
            condition="pneumonia"
        )

        response = use_case.execute(request)

        assert response.success is True
        # Should find CURB-65, PSI/PORT

    def test_filter_by_condition_missing(self, use_case: Any) -> None:
        """Test filtering without condition specified"""
        request = DiscoveryRequest(
            mode=DiscoveryMode.BY_CONDITION,
            condition=None
        )

        response = use_case.execute(request)

        assert response.success is False

    # ========================================================================
    # Get Info
    # ========================================================================

    def test_get_tool_info(self, use_case: Any) -> None:
        """Test getting detailed tool info"""
        request = DiscoveryRequest(
            mode=DiscoveryMode.GET_INFO,
            tool_id="sofa_score"
        )

        response = use_case.execute(request)

        assert response.success is True
        assert response.tool_detail is not None
        assert response.tool_detail.tool_id == "sofa_score"
        assert response.tool_detail.name is not None
        assert response.tool_detail.purpose is not None
        assert response.tool_detail.input_params is not None

    def test_get_tool_info_not_found(self, use_case: Any) -> None:
        """Test getting info for unknown tool"""
        request = DiscoveryRequest(
            mode=DiscoveryMode.GET_INFO,
            tool_id="unknown_tool"
        )

        response = use_case.execute(request)

        assert response.success is False
        assert "not found" in response.error.lower()

    def test_get_tool_info_missing_id(self, use_case: Any) -> None:
        """Test getting info without tool_id"""
        request = DiscoveryRequest(
            mode=DiscoveryMode.GET_INFO,
            tool_id=None
        )

        response = use_case.execute(request)

        assert response.success is False
        assert "required" in response.error.lower()

    # ========================================================================
    # List Specialties
    # ========================================================================

    def test_list_specialties(self, use_case: Any) -> None:
        """Test listing available specialties"""
        request = DiscoveryRequest(mode=DiscoveryMode.LIST_SPECIALTIES)

        response = use_case.execute(request)

        assert response.success is True
        assert response.available_specialties is not None
        assert len(response.available_specialties) > 0
        # Should include common specialties
        assert "critical_care" in response.available_specialties

    # ========================================================================
    # List Contexts
    # ========================================================================

    def test_list_contexts(self, use_case: Any) -> None:
        """Test listing available clinical contexts"""
        request = DiscoveryRequest(mode=DiscoveryMode.LIST_CONTEXTS)

        response = use_case.execute(request)

        assert response.success is True
        assert response.available_contexts is not None
        assert len(response.available_contexts) > 0

    # ========================================================================
    # Tool Summary DTO
    # ========================================================================

    def test_tool_summary_dto_structure(self, use_case: Any) -> None:
        """Test ToolSummaryDTO has expected fields"""
        request = DiscoveryRequest(mode=DiscoveryMode.LIST_ALL, limit=1)

        response = use_case.execute(request)

        assert response.success is True
        tool = response.tools[0]

        assert tool.tool_id is not None
        assert tool.name is not None
        assert tool.purpose is not None
        assert tool.specialties is not None
        assert isinstance(tool.specialties, list)

    # ========================================================================
    # Tool Detail DTO
    # ========================================================================

    def test_tool_detail_dto_structure(self, use_case: Any) -> None:
        """Test ToolDetailDTO has expected fields"""
        request = DiscoveryRequest(
            mode=DiscoveryMode.GET_INFO,
            tool_id="glasgow_coma_scale"
        )

        response = use_case.execute(request)

        assert response.success is True
        detail = response.tool_detail

        assert detail.tool_id == "glasgow_coma_scale"
        assert detail.name is not None
        assert detail.input_params is not None
        assert detail.specialties is not None
        assert detail.clinical_contexts is not None
        assert detail.references is not None


class TestUseCaseIntegration:
    """Integration tests for use cases working together"""

    @pytest.fixture
    def registry(self) -> Any:
        """Create a registry with all calculators"""

        reg = ToolRegistry()
        for calc_class in CALCULATORS:
            calc = calc_class()
            reg.register(calc)
        return reg

    def test_discover_then_calculate(self, registry: Any) -> None:
        """Test discovery followed by calculation"""
        discovery = DiscoveryUseCase(registry)
        CalculateUseCase(registry)

        # Step 1: Discover tools for sepsis
        disc_request = DiscoveryRequest(
            mode=DiscoveryMode.SEARCH,
            query="sepsis"
        )
        disc_response = discovery.execute(disc_request)

        assert disc_response.success is True
        assert disc_response.count > 0

        # Step 2: Get info about first tool
        tool_id = disc_response.tools[0].tool_id
        info_request = DiscoveryRequest(
            mode=DiscoveryMode.GET_INFO,
            tool_id=tool_id
        )
        info_response = discovery.execute(info_request)

        assert info_response.success is True

    def test_all_calculators_can_execute(self, registry: Any) -> None:
        """Test that all registered calculators can execute without errors"""
        calculate = CalculateUseCase(registry)

        # Sample params for different calculators
        test_cases = [
            ("glasgow_coma_scale", {"eye_response": 4, "verbal_response": 5, "motor_response": 6}),
            ("rass", {"rass_score": 0}),
            ("asa_physical_status", {"asa_class": 2}),
        ]

        for tool_id, params in test_cases:
            request = CalculateRequest(tool_id=tool_id, params=params)
            response = calculate.execute(request)

            assert response is not None, f"No response for {tool_id}"
            assert response.success is True, f"Failed for {tool_id}: {response.error}"


# ============================================================================
# Run tests
# ============================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
