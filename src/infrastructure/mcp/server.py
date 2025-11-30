"""
Medical Calculator MCP Server

A Model Context Protocol server providing medical calculators with intelligent
tool discovery for AI agents.

Architecture:
    This server follows DDD principles with clear separation:
    - Domain Layer: Calculators, Registry, Value Objects
    - Application Layer: Use Cases, DTOs
    - Infrastructure Layer: MCP Handlers, Resources

Usage:
    # Development mode with MCP inspector
    mcp dev src/infrastructure/mcp/server.py
    
    # Direct execution (stdio transport)
    python -m src.infrastructure.mcp.server
    
    # HTTP transport
    python -m src.infrastructure.mcp.server --transport http

Tool Discovery Flow:
    1. Agent calls search_calculators(), list_by_specialty(), or list_by_context()
    2. Agent calls get_calculator_info(tool_id) for parameters
    3. Agent calls calculate_*(params) for calculation
"""

from mcp.server.fastmcp import FastMCP

from ...domain.registry.tool_registry import ToolRegistry, get_registry
from ...domain.services.calculators import CALCULATORS

from .config import default_config
from .handlers import DiscoveryHandler, CalculatorHandler, PromptHandler
from .resources import CalculatorResourceHandler


class MedicalCalculatorServer:
    """
    Main MCP Server for Medical Calculators.
    
    This class orchestrates:
    - FastMCP server initialization
    - Calculator registration
    - Handler registration (Discovery, Calculator)
    - Resource registration
    
    Design Principles:
    - Single Responsibility: Each handler manages its own domain
    - Open/Closed: Easy to add new handlers without modifying existing code
    - Dependency Injection: Registry injected into handlers
    """
    
    def __init__(self, config=None):
        """
        Initialize the MCP server.
        
        Args:
            config: Server configuration (uses default if not provided)
        """
        self._config = config or default_config
        
        # Create FastMCP server
        self._mcp = FastMCP(
            name=self._config.name,
            json_response=self._config.json_response,
            instructions=self._config.instructions
        )
        
        # Use singleton registry for consistency
        self._registry = get_registry()
        
        # Register all calculators
        self._register_calculators()
        
        # Initialize handlers
        self._init_handlers()
    
    def _register_calculators(self) -> None:
        """Register all calculators with the registry"""
        for calculator_cls in CALCULATORS:
            instance = calculator_cls()
            # Skip if already registered (singleton pattern may have existing entries)
            if self._registry.get_calculator(instance.tool_id) is None:
                self._registry.register(instance)
    
    def _init_handlers(self) -> None:
        """Initialize all MCP handlers"""
        # Discovery tools (search_calculators, list_by_specialty, etc.)
        self._discovery_handler = DiscoveryHandler(self._mcp, self._registry)
        
        # Calculator tools (calculate_sofa, calculate_gcs, etc.)
        self._calculator_handler = CalculatorHandler(self._mcp, self._registry)
        
        # Resources (calculator://list, etc.)
        self._resource_handler = CalculatorResourceHandler(self._mcp, self._registry)
        
        # Prompts (clinical workflows)
        self._prompt_handler = PromptHandler(self._mcp, self._registry)
    
    @property
    def mcp(self) -> FastMCP:
        """Get the FastMCP server instance"""
        return self._mcp
    
    @property
    def registry(self) -> ToolRegistry:
        """Get the tool registry"""
        return self._registry
    
    def run(self, transport: str = "stdio") -> None:
        """
        Run the MCP server.
        
        Args:
            transport: Transport type ("stdio" or "streamable-http")
        """
        if transport == "http":
            self._mcp.run(transport="streamable-http")
        else:
            self._mcp.run()


# =============================================================================
# Module-level server instance
# =============================================================================

# Create default server instance for module-level access
_server = MedicalCalculatorServer()

# Export the mcp instance for FastMCP compatibility
mcp = _server.mcp


# =============================================================================
# Entry Point
# =============================================================================

def main():
    """Run the MCP server"""
    import sys
    
    transport = "stdio"
    if "--transport" in sys.argv:
        idx = sys.argv.index("--transport")
        if idx + 1 < len(sys.argv):
            transport = sys.argv[idx + 1]
    
    _server.run(transport)


if __name__ == "__main__":
    main()
