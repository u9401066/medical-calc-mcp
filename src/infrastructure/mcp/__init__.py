"""
MCP Server Implementation

Provides the FastMCP-based server for exposing medical calculators
via the Model Context Protocol.

Architecture:
    - server.py: Main server orchestration (MedicalCalculatorServer)
    - config.py: Server configuration
    - handlers/: MCP tool handlers (Discovery, Calculator)
    - resources/: MCP resource handlers
"""

from .server import mcp, main, MedicalCalculatorServer
from .config import McpServerConfig, default_config

__all__ = [
    "mcp",
    "main",
    "MedicalCalculatorServer",
    "McpServerConfig",
    "default_config",
]
