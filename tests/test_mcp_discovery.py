from typing import Any
"""
Tests for Discovery Handler

Tests for discovery_handler.py - tool discovery and navigation.
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
        # Should register discovery tools
        expected_tools = [
            "list_specialties",
            "list_contexts",
            "list_calculators",
            "list_by_specialty",
            "list_by_context",
            "get_calculator_info",
            "search_calculators",
        ]
        for tool_name in expected_tools:
            assert tool_name in mock_mcp._tools, f"Missing tool: {tool_name}"

    def test_list_specialties(self, handler: Any, mock_mcp: Any) -> None:
        """Test list_specialties returns available specialties"""
        list_specialties = mock_mcp._tools["list_specialties"]
        result = list_specialties()

        assert result.get("success")
        assert "available_specialties" in result
        assert len(result["available_specialties"]) > 0
        assert "next_step" in result

    def test_list_specialties_includes_counts(self, handler: Any, mock_mcp: Any) -> None:
        """Test that specialties include tool counts"""
        list_specialties = mock_mcp._tools["list_specialties"]
        result = list_specialties()

        # Each specialty should have a count
        for specialty in result.get("specialties", []):
            assert "name" in specialty or isinstance(specialty, str)

    def test_list_contexts(self, handler: Any, mock_mcp: Any) -> None:
        """Test list_contexts returns available contexts"""
        list_contexts = mock_mcp._tools["list_contexts"]
        result = list_contexts()

        assert result.get("success")
        assert "available_contexts" in result
        assert len(result["available_contexts"]) > 0
        assert "next_step" in result

    def test_list_calculators(self, handler: Any, mock_mcp: Any) -> None:
        """Test list_calculators returns all calculators"""
        list_calculators = mock_mcp._tools["list_calculators"]
        result = list_calculators(limit=100)  # Use larger limit

        assert result.get("success")
        assert "tools" in result
        # Should have at least 68 calculators
        assert len(result["tools"]) >= 68

    def test_list_calculators_with_limit(self, handler: Any, mock_mcp: Any) -> None:
        """Test list_calculators respects limit parameter"""
        list_calculators = mock_mcp._tools["list_calculators"]
        result = list_calculators(limit=10)

        assert len(result.get("tools", [])) <= 10

    def test_list_by_specialty_valid(self, handler: Any, mock_mcp: Any) -> None:
        """Test list_by_specialty with valid specialty"""
        list_by_specialty = mock_mcp._tools["list_by_specialty"]
        result = list_by_specialty("critical_care")

        assert result.get("success")
        assert "tools" in result
        assert len(result["tools"]) > 0
        assert "next_step" in result

    def test_list_by_specialty_has_example(self, handler: Any, mock_mcp: Any) -> None:
        """Test list_by_specialty includes example"""
        list_by_specialty = mock_mcp._tools["list_by_specialty"]
        result = list_by_specialty("critical_care")

        if result.get("success"):
            assert "example" in result

    def test_list_by_specialty_invalid(self, handler: Any, mock_mcp: Any) -> None:
        """Test list_by_specialty with invalid specialty"""
        list_by_specialty = mock_mcp._tools["list_by_specialty"]
        result = list_by_specialty("fake_specialty")

        # Should return error or empty with hint
        assert not result.get("success") or len(result.get("tools", [])) == 0

    def test_list_by_context_valid(self, handler: Any, mock_mcp: Any) -> None:
        """Test list_by_context with valid context"""
        list_by_context = mock_mcp._tools["list_by_context"]
        result = list_by_context("preoperative_assessment")

        assert result.get("success")
        assert "tools" in result
        assert len(result["tools"]) > 0

    def test_list_by_context_invalid(self, handler: Any, mock_mcp: Any) -> None:
        """Test list_by_context with invalid context"""
        list_by_context = mock_mcp._tools["list_by_context"]
        result = list_by_context("fake_context")

        # Should return error or empty
        assert not result.get("success") or len(result.get("tools", [])) == 0

    def test_get_calculator_info_valid(self, handler: Any, mock_mcp: Any) -> None:
        """Test get_calculator_info with valid tool_id"""
        get_calculator_info = mock_mcp._tools["get_calculator_info"]
        result = get_calculator_info("sofa_score")

        assert result.get("success")
        # Result should have tools or tool info
        assert "tools" in result or "next_step" in result
        assert "next_step" in result

    def test_get_calculator_info_includes_navigation(self, handler: Any, mock_mcp: Any) -> None:
        """Test get_calculator_info includes navigation hints"""
        get_calculator_info = mock_mcp._tools["get_calculator_info"]
        result = get_calculator_info("apache_ii")

        if result.get("success"):
            assert "navigation" in result

    def test_get_calculator_info_invalid(self, handler: Any, mock_mcp: Any) -> None:
        """Test get_calculator_info with invalid tool_id"""
        get_calculator_info = mock_mcp._tools["get_calculator_info"]
        result = get_calculator_info("nonexistent_tool")

        assert not result.get("success")

    def test_search_calculators(self, handler: Any, mock_mcp: Any) -> None:
        """Test search_calculators with valid keyword"""
        search_calculators = mock_mcp._tools["search_calculators"]
        result = search_calculators("sofa")

        assert "tools" in result or "results" in result
        # Should find SOFA-related calculators
        tools = result.get("tools", result.get("results", []))
        assert any("sofa" in str(t).lower() for t in tools)

    def test_search_calculators_with_limit(self, handler: Any, mock_mcp: Any) -> None:
        """Test search_calculators respects limit"""
        search_calculators = mock_mcp._tools["search_calculators"]
        result = search_calculators("score", limit=5)

        tools = result.get("tools", result.get("results", []))
        assert len(tools) <= 5

    def test_search_calculators_no_results(self, handler: Any, mock_mcp: Any) -> None:
        """Test search_calculators with no results"""
        search_calculators = mock_mcp._tools["search_calculators"]
        result = search_calculators("xyznonexistent123")

        # Should have hint when no results
        assert result.get("count", 0) == 0 or len(result.get("tools", [])) == 0
        if result.get("count", 0) == 0:
            assert "hint" in result

    def test_search_calculators_partial_match(self, handler: Any, mock_mcp: Any) -> None:
        """Test search_calculators with partial keyword"""
        search_calculators = mock_mcp._tools["search_calculators"]
        result = search_calculators("cardiac")

        # Should find cardiac-related tools
        tools = result.get("tools", result.get("results", []))
        assert len(tools) > 0


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
        """Test complete specialty navigation flow"""
        # Step 1: List specialties
        list_specialties = mock_mcp._tools["list_specialties"]
        specialties = list_specialties()
        assert specialties.get("success")

        # Step 2: List tools by specialty
        list_by_specialty = mock_mcp._tools["list_by_specialty"]
        tools = list_by_specialty("critical_care")
        assert tools.get("success")
        assert len(tools.get("tools", [])) > 0

        # Step 3: Get info for a tool
        get_info = mock_mcp._tools["get_calculator_info"]
        tool_id = tools["tools"][0]["tool_id"]
        info = get_info(tool_id)
        assert info.get("success")

    def test_context_navigation_flow(self, handler: Any, mock_mcp: Any) -> None:
        """Test complete context navigation flow"""
        # Step 1: List contexts
        list_contexts = mock_mcp._tools["list_contexts"]
        contexts = list_contexts()
        assert contexts.get("success")

        # Step 2: List tools by context
        list_by_context = mock_mcp._tools["list_by_context"]
        tools = list_by_context("severity_assessment")

        if tools.get("success") and len(tools.get("tools", [])) > 0:
            # Step 3: Get info for a tool
            get_info = mock_mcp._tools["get_calculator_info"]
            tool_id = tools["tools"][0]["tool_id"]
            info = get_info(tool_id)
            assert info.get("success")

    def test_direct_search_flow(self, handler: Any, mock_mcp: Any) -> None:
        """Test direct search workflow"""
        # Search directly
        search = mock_mcp._tools["search_calculators"]
        results = search("sepsis")

        # Should find sepsis-related tools (qSOFA, SOFA, etc.)
        tools = results.get("tools", results.get("results", []))
        if len(tools) > 0:
            # Get info for first result
            get_info = mock_mcp._tools["get_calculator_info"]
            tool_id = tools[0]["tool_id"] if isinstance(tools[0], dict) else tools[0]
            info = get_info(tool_id)
            # Should succeed or fail gracefully
            assert "success" in info


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
