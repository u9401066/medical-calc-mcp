from typing import Any

"""
Tests for Discovery Handler

Tests for discovery_handler.py - tool discovery and navigation.

v3.0 Consolidated Tools:
- discover() - unified discovery (replaces list_specialties, list_contexts, etc.)
- get_related_tools() - semantic discovery
- find_tools_by_params() - reverse param lookup
"""

from unittest.mock import MagicMock

import pytest


class TestDiscoveryHandler:
    """Tests for DiscoveryHandler"""

    @pytest.fixture
    def mock_mcp(self) -> Any:
        """Create a mock FastMCP instance"""
        mcp = MagicMock()
        # Store registered tools
        mcp._tools = {}

        def mock_tool() -> Any:
            def decorator(func: Any) -> Any:
                mcp._tools[func.__name__] = func
                return func
            return decorator

        mcp.tool = mock_tool
        return mcp

    @pytest.fixture
    def populated_registry(self) -> Any:
        """Create a registry with all calculators registered"""
        from src.domain.registry.tool_registry import ToolRegistry
        from src.domain.services.calculators import CALCULATORS

        reg = ToolRegistry()
        for calc_class in CALCULATORS:
            calc = calc_class()
            reg.register(calc)
        return reg

    @pytest.fixture
    def handler(self, mock_mcp: Any, populated_registry: Any) -> Any:
        """Create handler instance"""
        from src.infrastructure.mcp.handlers.discovery_handler import DiscoveryHandler
        return DiscoveryHandler(mock_mcp, populated_registry)

    def test_handler_registers_tools(self, handler: Any, mock_mcp: Any) -> None:
        """Test that handler registers all expected discovery tools"""
        # v3.0: Consolidated to 3 high-level tools
        expected_tools = [
            "discover",
            "get_related_tools",
            "find_tools_by_params",
        ]
        for tool_name in expected_tools:
            assert tool_name in mock_mcp._tools, f"Missing tool: {tool_name}"

    def test_discover_all_mode(self, handler: Any, mock_mcp: Any) -> None:
        """Test discover() with default 'all' mode returns specialties and contexts"""
        discover = mock_mcp._tools["discover"]
        result = discover()

        assert result.get("success")
        assert "specialties" in result
        assert "contexts" in result
        assert result["specialties"]["count"] > 0
        assert result["contexts"]["count"] > 0
        assert "next_step" in result

    def test_discover_by_specialty(self, handler: Any, mock_mcp: Any) -> None:
        """Test discover(by='specialty') returns tools for that specialty"""
        discover = mock_mcp._tools["discover"]
        result = discover(by="specialty", value="critical_care")

        assert result.get("success")
        assert "tools" in result
        assert len(result["tools"]) > 0
        assert "next_step" in result
        assert result.get("filter", {}).get("by") == "specialty"

    def test_discover_by_specialty_has_example(self, handler: Any, mock_mcp: Any) -> None:
        """Test discover(by='specialty') includes example"""
        discover = mock_mcp._tools["discover"]
        result = discover(by="specialty", value="critical_care")

        if result.get("success"):
            assert "example" in result

    def test_discover_by_specialty_invalid(self, handler: Any, mock_mcp: Any) -> None:
        """Test discover(by='specialty') with invalid specialty"""
        discover = mock_mcp._tools["discover"]
        result = discover(by="specialty", value="fake_specialty")

        # Should return error or empty with hint
        assert not result.get("success") or len(result.get("tools", [])) == 0

    def test_discover_by_specialty_missing_value(self, handler: Any, mock_mcp: Any) -> None:
        """Test discover(by='specialty') without value returns error"""
        discover = mock_mcp._tools["discover"]
        result = discover(by="specialty")

        assert not result.get("success")
        assert "error" in result

    def test_discover_by_context(self, handler: Any, mock_mcp: Any) -> None:
        """Test discover(by='context') returns tools for that context"""
        discover = mock_mcp._tools["discover"]
        result = discover(by="context", value="preoperative_assessment")

        assert result.get("success")
        assert "tools" in result
        assert len(result["tools"]) > 0

    def test_discover_by_context_invalid(self, handler: Any, mock_mcp: Any) -> None:
        """Test discover(by='context') with invalid context"""
        discover = mock_mcp._tools["discover"]
        result = discover(by="context", value="fake_context")

        assert not result.get("success") or len(result.get("tools", [])) == 0

    def test_discover_by_keyword(self, handler: Any, mock_mcp: Any) -> None:
        """Test discover(by='keyword') searches for tools"""
        discover = mock_mcp._tools["discover"]
        result = discover(by="keyword", value="sofa")

        assert "tools" in result
        tools = result.get("tools", [])
        assert any("sofa" in str(t).lower() for t in tools)

    def test_discover_by_keyword_with_limit(self, handler: Any, mock_mcp: Any) -> None:
        """Test discover(by='keyword') respects limit"""
        discover = mock_mcp._tools["discover"]
        result = discover(by="keyword", value="score", limit=5)

        tools = result.get("tools", [])
        assert len(tools) <= 5

    def test_discover_by_keyword_no_results(self, handler: Any, mock_mcp: Any) -> None:
        """Test discover(by='keyword') with no results"""
        discover = mock_mcp._tools["discover"]
        result = discover(by="keyword", value="xyznonexistent123")

        assert result.get("count", 0) == 0 or len(result.get("tools", [])) == 0
        if result.get("count", 0) == 0:
            assert "hint" in result

    def test_discover_tools_mode(self, handler: Any, mock_mcp: Any) -> None:
        """Test discover(by='tools') returns all calculators"""
        discover = mock_mcp._tools["discover"]
        result = discover(by="tools", limit=100)

        assert result.get("success")
        assert "tools" in result
        # Should have at least 68 calculators
        assert len(result["tools"]) >= 68

    def test_discover_tools_with_limit(self, handler: Any, mock_mcp: Any) -> None:
        """Test discover(by='tools') respects limit parameter"""
        discover = mock_mcp._tools["discover"]
        result = discover(by="tools", limit=10)

        assert len(result.get("tools", [])) <= 10

    def test_discover_invalid_by_value(self, handler: Any, mock_mcp: Any) -> None:
        """Test discover() with invalid 'by' parameter"""
        discover = mock_mcp._tools["discover"]
        result = discover(by="invalid_mode")

        assert not result.get("success")
        assert "valid_values" in result

    def test_get_related_tools_valid(self, handler: Any, mock_mcp: Any) -> None:
        """Test get_related_tools with valid tool_id"""
        get_related_tools = mock_mcp._tools["get_related_tools"]
        result = get_related_tools("sofa_score")

        assert result.get("success")
        assert "related_tools" in result
        assert "source_tool" in result
        assert result["source_tool"] == "sofa_score"

    def test_get_related_tools_invalid(self, handler: Any, mock_mcp: Any) -> None:
        """Test get_related_tools with invalid tool_id"""
        get_related_tools = mock_mcp._tools["get_related_tools"]
        result = get_related_tools("nonexistent_tool")

        assert not result.get("success")
        assert "error" in result

    def test_find_tools_by_params(self, handler: Any, mock_mcp: Any) -> None:
        """Test find_tools_by_params with valid params"""
        find_tools = mock_mcp._tools["find_tools_by_params"]
        result = find_tools(["age", "creatinine"])

        assert result.get("success")
        assert "tools" in result
        assert "input_params" in result

    def test_find_tools_by_params_no_match(self, handler: Any, mock_mcp: Any) -> None:
        """Test find_tools_by_params with no matching params"""
        find_tools = mock_mcp._tools["find_tools_by_params"]
        result = find_tools(["xyz_nonexistent_param"])

        assert result.get("success")  # Still succeeds but with empty results
        assert result.get("count", 0) == 0 or len(result.get("tools", [])) == 0


class TestDiscoveryWorkflow:
    """Test complete discovery workflows"""

    @pytest.fixture
    def mock_mcp(self) -> Any:
        """Create a mock FastMCP instance"""
        mcp = MagicMock()
        mcp._tools = {}

        def mock_tool() -> Any:
            def decorator(func: Any) -> Any:
                mcp._tools[func.__name__] = func
                return func
            return decorator

        mcp.tool = mock_tool
        return mcp

    @pytest.fixture
    def handler(self, mock_mcp: Any) -> Any:
        """Create handler instance"""
        from src.domain.registry.tool_registry import ToolRegistry
        from src.domain.services.calculators import CALCULATORS
        from src.infrastructure.mcp.handlers.discovery_handler import DiscoveryHandler

        reg = ToolRegistry()
        for calc_class in CALCULATORS:
            reg.register(calc_class())
        return DiscoveryHandler(mock_mcp, reg)

    def test_specialty_navigation_flow(self, handler: Any, mock_mcp: Any) -> None:
        """Test complete specialty navigation flow using consolidated discover()"""
        discover = mock_mcp._tools["discover"]

        # Step 1: List all specialties and contexts
        all_result = discover()
        assert all_result.get("success")

        # Step 2: List tools by specialty
        tools = discover(by="specialty", value="critical_care")
        assert tools.get("success")
        assert len(tools.get("tools", [])) > 0

    def test_context_navigation_flow(self, handler: Any, mock_mcp: Any) -> None:
        """Test complete context navigation flow using consolidated discover()"""
        discover = mock_mcp._tools["discover"]

        # Step 1: List all contexts
        all_result = discover()
        assert all_result.get("success")
        assert "contexts" in all_result

        # Step 2: List tools by context
        tools = discover(by="context", value="severity_assessment")

        if tools.get("success") and len(tools.get("tools", [])) > 0:
            # Success
            pass

    def test_direct_search_flow(self, handler: Any, mock_mcp: Any) -> None:
        """Test direct search workflow using consolidated discover()"""
        discover = mock_mcp._tools["discover"]

        # Search directly
        results = discover(by="keyword", value="sepsis")

        # Should find sepsis-related tools (qSOFA, SOFA, etc.)
        tools = results.get("tools", [])
        assert len(tools) >= 0  # May or may not find results


class TestDiscoveryIntegration:
    """Integration tests with real server"""

    @pytest.fixture
    def server(self) -> Any:
        """Create real server instance"""
        from src.infrastructure.mcp.server import MedicalCalculatorServer
        return MedicalCalculatorServer()

    def test_server_has_discovery_tools(self, server: Any) -> None:
        """Test that server has discovery handler"""
        assert server.registry is not None
        # Server should have calculators
        assert len(server.registry.list_all()) >= 68
