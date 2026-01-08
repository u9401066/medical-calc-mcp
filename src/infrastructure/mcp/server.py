"""
Medical Calculator MCP Server

A Model Context Protocol server providing medical calculators with intelligent
tool discovery for AI agents.

Architecture:
    This server follows DDD principles with clear separation:
    - Domain Layer: Calculators, Registry, Value Objects
    - Application Layer: Use Cases, DTOs
    - Infrastructure Layer: MCP Handlers, Resources, Security

Security Features (Optional):
    - Rate Limiting: Throttle requests to prevent abuse
    - API Authentication: API Key based authentication

    All security features are DISABLED by default.
    Enable via environment variables:
        SECURITY_RATE_LIMIT_ENABLED=true
        SECURITY_AUTH_ENABLED=true
        SECURITY_API_KEYS=your-key

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

import logging
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from ...domain.registry.tool_registry import ToolRegistry, get_registry
from ...domain.services.calculators import CALCULATORS
from ..security import SecurityConfig, SecurityMiddleware
from .config import McpServerConfig, default_config
from .handlers import CalculatorHandler, DiscoveryHandler, PromptHandler
from .resources import CalculatorResourceHandler

logger = logging.getLogger(__name__)


class MedicalCalculatorServer:
    """
    Main MCP Server for Medical Calculators.

    This class orchestrates:
    - FastMCP server initialization
    - Calculator registration
    - Handler registration (Discovery, Calculator)
    - Resource registration
    - Security middleware (optional)

    Design Principles:
    - Single Responsibility: Each handler manages its own domain
    - Open/Closed: Easy to add new handlers without modifying existing code
    - Dependency Injection: Registry injected into handlers

    Security (Optional):
    - Rate Limiting: Enable with SECURITY_RATE_LIMIT_ENABLED=true
    - Authentication: Enable with SECURITY_AUTH_ENABLED=true
    """

    def __init__(self, config: Optional[McpServerConfig] = None, security_config: Optional[SecurityConfig] = None) -> None:
        """
        Initialize the MCP server.

        Args:
            config: Server configuration (uses default if not provided)
            security_config: Security configuration (loads from env if not provided)
        """
        self._config = config or default_config

        # Initialize security middleware (optional, disabled by default)
        self._security_config = security_config or SecurityConfig.from_env()
        self._security = SecurityMiddleware(self._security_config)

        # Log security status
        if self._security.is_enabled():
            logger.info(f"Security features enabled:\n{self._security_config}")
        else:
            logger.info("Security features: DISABLED (default)")

        # Create FastMCP server with network settings
        self._mcp = FastMCP(
            name=self._config.name,
            json_response=self._config.json_response,
            instructions=self._config.instructions,
            host=self._config.host,  # For SSE/HTTP transport
            port=self._config.port,  # For SSE/HTTP transport
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

        # Health check endpoint for Docker/Kubernetes liveness probes
        self._init_health_endpoint()

    def _init_health_endpoint(self) -> None:
        """Initialize health check endpoint for container orchestration."""
        from starlette.requests import Request
        from starlette.responses import JSONResponse

        @self._mcp.custom_route("/health", methods=["GET", "HEAD"])
        async def health_check(request: Request) -> JSONResponse:
            """
            Health check endpoint for Docker/Kubernetes liveness probes.

            Returns:
                JSON response with service status and calculator count
            """
            return JSONResponse(
                content={
                    "status": "healthy",
                    "service": self._config.name,
                    "version": "1.2.0",
                    "calculators_loaded": len(self._registry.list_all()),
                },
                status_code=200,
            )

    @property
    def mcp(self) -> FastMCP:
        """Get the FastMCP server instance"""
        return self._mcp

    @property
    def registry(self) -> ToolRegistry:
        """Get the tool registry"""
        return self._registry

    @property
    def security(self) -> SecurityMiddleware:
        """Get the security middleware"""
        return self._security

    def run(self, transport: str = "stdio") -> None:
        """
        Run the MCP server.

        Args:
            transport: Transport type ("stdio", "sse", or "http")
        """
        if transport == "http":
            self._mcp.run(transport="streamable-http")
        elif transport == "sse":
            self._mcp.run(transport="sse")
        else:
            self._mcp.run(transport="stdio")


# =============================================================================
# Module-level server instance
# =============================================================================

# Create default server instance for module-level access
# Lazy initialization to avoid import order issues
_server: Optional[MedicalCalculatorServer] = None

def get_server() -> MedicalCalculatorServer:
    """Get or create the server instance"""
    global _server
    if _server is None:
        _server = MedicalCalculatorServer()
    return _server

# Export the mcp instance for FastMCP compatibility
# This is accessed after module is fully loaded
def _get_mcp() -> FastMCP:
    return get_server().mcp

# For backward compatibility - lazy property
class _McpProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_server().mcp, name)

mcp = _McpProxy()


# =============================================================================
# Entry Point
# =============================================================================

def main() -> None:
    """Run the MCP server"""
    import sys

    transport = "stdio"
    if "--transport" in sys.argv:
        idx = sys.argv.index("--transport")
        if idx + 1 < len(sys.argv):
            transport = sys.argv[idx + 1]

    get_server().run(transport)


if __name__ == "__main__":
    main()
