"""
Calculator Handler

MCP tool handlers for calculator operations.

Modular design: Each specialty has its own handler module in the 
`calculators/` subdirectory for better maintainability.
"""

from mcp.server.fastmcp import FastMCP

from ....application.use_cases import CalculateUseCase
from ....domain.registry.tool_registry import ToolRegistry

# Import modular calculator handlers
from .calculators import (
    register_nephrology_tools,
    register_anesthesiology_tools,
    register_critical_care_tools,
    register_pediatric_tools,
)


class CalculatorHandler:
    """
    Handler for calculator-related MCP tools.
    
    Registers all calculator tools with the MCP server.
    Each calculator gets its own dedicated MCP tool with typed parameters.
    
    Tools are organized by specialty in separate modules:
    - calculators/nephrology.py     - Kidney function (CKD-EPI, etc.)
    - calculators/anesthesiology.py - Preoperative (ASA, RCRI, Mallampati)
    - calculators/critical_care.py  - ICU scores (APACHE, SOFA, NEWS2, etc.)
    - calculators/pediatric.py      - Pediatric (drug dosing, transfusion, MABL)
    """
    
    def __init__(self, mcp: FastMCP, registry: ToolRegistry):
        self._mcp = mcp
        self._registry = registry
        self._use_case = CalculateUseCase(registry)
        
        # Register all specialty tools
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register all calculator tools with MCP by specialty"""
        
        # Nephrology calculators
        register_nephrology_tools(self._mcp, self._use_case)
        
        # Anesthesiology / Preoperative calculators
        register_anesthesiology_tools(self._mcp, self._use_case)
        
        # Critical Care / ICU calculators
        register_critical_care_tools(self._mcp, self._use_case)
        
        # Pediatric & Transfusion calculators
        register_pediatric_tools(self._mcp, self._use_case)
