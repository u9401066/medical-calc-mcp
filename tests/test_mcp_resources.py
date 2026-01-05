from typing import Any
"""
Tests for MCP Resources

Tests for calculator_resources.py and related resource handlers.
"""

from unittest.mock import MagicMock

import pytest


class TestCalculatorResourceHandler:
    """Tests for CalculatorResourceHandler"""

    @pytest.fixture
    def mock_mcp(self) -> Any:
        """Create a mock FastMCP instance"""
        mcp = MagicMock()
        # Store registered resources
        mcp._resources = {}

        def mock_resource(uri: Any) -> Any:
            def decorator(func: Any) -> Any:
                mcp._resources[uri] = func
                return func
            return decorator

        mcp.resource = mock_resource
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
        from src.infrastructure.mcp.resources.calculator_resources import CalculatorResourceHandler
        return CalculatorResourceHandler(mock_mcp, populated_registry)

    def test_handler_registers_resources(self, handler: Any, mock_mcp: Any) -> None:
        """Test that handler registers all expected resources"""
        # Should register 4 resources
        assert len(mock_mcp._resources) == 4
        assert "calculator://list" in mock_mcp._resources
        assert "calculator://{tool_id}/info" in mock_mcp._resources
        assert "calculator://{tool_id}/references" in mock_mcp._resources
        assert "specialty://{specialty}/tools" in mock_mcp._resources

    def test_get_calculator_list(self, handler: Any, mock_mcp: Any) -> None:
        """Test calculator list resource"""
        get_list = mock_mcp._resources["calculator://list"]
        result = get_list()

        assert "# Available Medical Calculators" in result
        assert "Total:" in result
        # Should have at least 68 calculators
        assert "68" in result or int(result.split("Total: ")[1].split()[0]) >= 68

    def test_get_calculator_list_groups_by_specialty(self, handler: Any, mock_mcp: Any) -> None:
        """Test that list groups calculators by specialty"""
        get_list = mock_mcp._resources["calculator://list"]
        result = get_list()

        # Should contain specialty headers
        assert "## " in result  # Markdown headers for specialties
        assert "Critical Care" in result or "critical_care" in result.lower()

    def test_get_calculator_info_valid_tool(self, handler: Any, mock_mcp: Any) -> None:
        """Test getting info for a valid tool"""
        get_info = mock_mcp._resources["calculator://{tool_id}/info"]
        result = get_info("sofa_score")

        assert "SOFA" in result
        assert "Tool ID:" in result
        assert "Purpose:" in result
        assert "Input Parameters" in result

    def test_get_calculator_info_invalid_tool(self, handler: Any, mock_mcp: Any) -> None:
        """Test getting info for an invalid tool"""
        get_info = mock_mcp._resources["calculator://{tool_id}/info"]
        result = get_info("nonexistent_tool")

        assert "not found" in result.lower()

    def test_get_calculator_info_includes_specialties(self, handler: Any, mock_mcp: Any) -> None:
        """Test that info includes specialty information"""
        get_info = mock_mcp._resources["calculator://{tool_id}/info"]
        result = get_info("apache_ii")

        assert "Specialties:" in result
        assert "Contexts:" in result

    def test_get_calculator_references_valid_tool(self, handler: Any, mock_mcp: Any) -> None:
        """Test getting references for a valid tool"""
        get_refs = mock_mcp._resources["calculator://{tool_id}/references"]
        result = get_refs("sofa_score")

        assert "References for" in result
        assert "Reference 1" in result
        assert "Citation:" in result

    def test_get_calculator_references_with_doi(self, handler: Any, mock_mcp: Any) -> None:
        """Test references include DOI links"""
        get_refs = mock_mcp._resources["calculator://{tool_id}/references"]
        result = get_refs("news2")

        # Most tools should have DOI
        if "DOI:" in result:
            assert "https://doi.org/" in result

    def test_get_calculator_references_with_pubmed(self, handler: Any, mock_mcp: Any) -> None:
        """Test references include PubMed links"""
        get_refs = mock_mcp._resources["calculator://{tool_id}/references"]
        result = get_refs("sofa_score")

        if "PubMed:" in result:
            assert "pubmed.ncbi.nlm.nih.gov" in result

    def test_get_calculator_references_invalid_tool(self, handler: Any, mock_mcp: Any) -> None:
        """Test references for invalid tool"""
        get_refs = mock_mcp._resources["calculator://{tool_id}/references"]
        result = get_refs("fake_tool")

        assert "not found" in result.lower()

    def test_get_specialty_tools_valid(self, handler: Any, mock_mcp: Any) -> None:
        """Test getting tools for a valid specialty"""
        get_specialty = mock_mcp._resources["specialty://{specialty}/tools"]
        result = get_specialty("critical_care")

        assert "Critical Care" in result
        assert "Total:" in result
        # Critical care should have multiple tools
        assert "SOFA" in result or "sofa" in result.lower()

    def test_get_specialty_tools_case_insensitive(self, handler: Any, mock_mcp: Any) -> None:
        """Test specialty lookup is case-insensitive"""
        get_specialty = mock_mcp._resources["specialty://{specialty}/tools"]

        # Try different case variations
        result1 = get_specialty("critical_care")
        result2 = get_specialty("CRITICAL_CARE")
        result3 = get_specialty("Critical_Care")

        # All should find the same specialty (not "Unknown")
        assert "Unknown specialty" not in result1
        assert "Unknown specialty" not in result2
        assert "Unknown specialty" not in result3

    def test_get_specialty_tools_invalid(self, handler: Any, mock_mcp: Any) -> None:
        """Test getting tools for invalid specialty"""
        get_specialty = mock_mcp._resources["specialty://{specialty}/tools"]
        result = get_specialty("fake_specialty")

        assert "Unknown specialty" in result
        assert "Available:" in result

    def test_get_specialty_tools_with_spaces(self, handler: Any, mock_mcp: Any) -> None:
        """Test specialty names with spaces/hyphens"""
        get_specialty = mock_mcp._resources["specialty://{specialty}/tools"]

        # Try with space instead of underscore
        result = get_specialty("critical care")
        assert "Critical Care" in result or "Unknown specialty" not in result

    def test_specialty_tools_includes_parameters(self, handler: Any, mock_mcp: Any) -> None:
        """Test that specialty tools list includes parameters"""
        get_specialty = mock_mcp._resources["specialty://{specialty}/tools"]
        result = get_specialty("anesthesiology")

        assert "Parameters:" in result


class TestResourceIntegration:
    """Integration tests for resources with real server"""

    @pytest.fixture
    def server(self) -> Any:
        """Create real server instance"""
        from src.infrastructure.mcp.server import MedicalCalculatorServer
        return MedicalCalculatorServer()

    def test_server_has_resources_registered(self, server: Any) -> None:
        """Test that server registers resources"""
        # The server should have resources registered
        assert server.registry is not None
        assert len(server.registry.list_all()) >= 68

    def test_resource_handler_exists(self, server: Any) -> None:
        """Test that resource handler is created"""
        # Server should have MCP instance
        assert server.mcp is not None


class TestResourceContent:
    """Tests for resource content formatting"""

    @pytest.fixture
    def mock_mcp(self) -> Any:
        """Create a mock FastMCP instance"""
        mcp = MagicMock()
        mcp._resources = {}

        def mock_resource(uri: Any) -> Any:
            def decorator(func: Any) -> Any:
                mcp._resources[uri] = func
                return func
            return decorator

        mcp.resource = mock_resource
        return mcp

    @pytest.fixture
    def handler(self, mock_mcp: Any) -> Any:
        """Create handler instance"""
        from src.domain.registry.tool_registry import ToolRegistry
        from src.domain.services.calculators import CALCULATORS
        from src.infrastructure.mcp.resources.calculator_resources import CalculatorResourceHandler

        registry = ToolRegistry()
        for calc_class in CALCULATORS:
            registry.register(calc_class())
        return CalculatorResourceHandler(mock_mcp, registry)

    def test_list_markdown_formatting(self, handler: Any, mock_mcp: Any) -> None:
        """Test that list output uses proper markdown"""
        get_list = mock_mcp._resources["calculator://list"]
        result = get_list()

        # Should have proper markdown structure
        assert result.startswith("#")  # Title
        assert "**" in result  # Bold text
        assert "`" in result  # Code formatting

    def test_info_markdown_sections(self, handler: Any, mock_mcp: Any) -> None:
        """Test that info output has proper sections"""
        get_info = mock_mcp._resources["calculator://{tool_id}/info"]
        result = get_info("apache_ii")

        # Should have section headers
        assert "## Input Parameters" in result
        assert "## Clinical Use" in result

    def test_references_numbered(self, handler: Any, mock_mcp: Any) -> None:
        """Test that references are numbered"""
        get_refs = mock_mcp._resources["calculator://{tool_id}/references"]
        result = get_refs("apache_ii")

        # Should have numbered references
        assert "## Reference 1" in result
