"""
MCP Server Implementation

Provides the FastMCP-based server for exposing medical calculators
via the Model Context Protocol.
"""

from .server import mcp, main

__all__ = ["mcp", "main"]
