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
    register_pulmonology_tools,
    register_cardiology_tools,
    register_emergency_tools,
    register_hepatology_tools,
    register_surgery_tools,
    register_acid_base_tools,
    register_hematology_tools,
    register_neurology_tools,
    register_general_tools,
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
    - calculators/pulmonology.py    - Respiratory (CURB-65, etc.)
    - calculators/cardiology.py     - Cardiac (CHA₂DS₂-VASc, HEART, etc.)
    - calculators/emergency.py      - ED tools (Wells DVT/PE, etc.)
    - calculators/hepatology.py     - Liver (MELD, Child-Pugh, etc.)
    - calculators/surgery.py        - Perioperative (Caprini VTE, etc.)
    - calculators/acid_base.py      - Acid-base (Anion Gap, Delta Ratio, etc.)
    - calculators/hematology.py     - Hematology (4Ts HIT, etc.)
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
        
        # Pulmonology / Respiratory calculators
        register_pulmonology_tools(self._mcp, self._use_case)
        
        # Cardiology calculators
        register_cardiology_tools(self._mcp, self._use_case)
        
        # Emergency Medicine calculators
        register_emergency_tools(self._mcp, self._use_case)
        
        # Hepatology / GI calculators
        register_hepatology_tools(self._mcp, self._use_case)
        
        # Surgery / Perioperative calculators
        register_surgery_tools(self._mcp, self._use_case)
        
        # Acid-Base / Metabolic calculators
        register_acid_base_tools(self._mcp, self._use_case)
        
        # Hematology calculators
        register_hematology_tools(self._mcp, self._use_case)
        
        # Neurology calculators
        register_neurology_tools(self._mcp, self._use_case)
        
        # General calculators (BSA, Cockcroft-Gault, Corrected Ca, Parkland)
        register_general_tools(self._mcp, self._use_case)
