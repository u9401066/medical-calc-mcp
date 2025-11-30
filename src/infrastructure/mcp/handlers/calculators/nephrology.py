"""
Nephrology Calculator Tools

MCP tool handlers for nephrology calculators.
Uses Annotated + Field for rich parameter descriptions in JSON Schema.
"""

from typing import Any, Annotated

from pydantic import Field
from mcp.server.fastmcp import FastMCP

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_nephrology_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all nephrology calculator tools with MCP"""
    
    @mcp.tool()
    def calculate_ckd_epi_2021(
        serum_creatinine: Annotated[float, Field(description="血清肌酐 Creatinine mg/dL (0.5-15.0)")],
        age: Annotated[int, Field(description="年齡 Age years (18-120)")],
        sex: Annotated[str, Field(description="性別 Sex: 'male' or 'female'")]
    ) -> dict[str, Any]:
        """
        計算 CKD-EPI 2021 eGFR (腎絲球過濾率)
        
        Race-free equation. Returns eGFR in mL/min/1.73m².
        G1≥90, G2:60-89, G3a:45-59, G3b:30-44, G4:15-29, G5<15.
        
        Reference: Inker LA, et al. NEJM 2021.
        """
        request = CalculateRequest(
            tool_id="ckd_epi_2021",
            params={"serum_creatinine": serum_creatinine, "age": age, "sex": sex}
        )
        response = use_case.execute(request)
        return response.to_dict()
