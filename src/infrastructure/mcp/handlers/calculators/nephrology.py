"""
Nephrology Calculator Tools

MCP tool handlers for nephrology calculators.
"""

from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_nephrology_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all nephrology calculator tools with MCP"""
    
    @mcp.tool()
    def calculate_ckd_epi_2021(
        serum_creatinine: float,
        age: int,
        sex: str
    ) -> dict[str, Any]:
        """
        計算 CKD-EPI 2021 eGFR (腎絲球過濾率)
        
        Calculate estimated GFR using the 2021 CKD-EPI equation (race-free).
        
        Args:
            serum_creatinine: 血清肌酐值 (mg/dL)
            age: 年齡 (歲, 18-120)
            sex: 性別 ("male" 或 "female")
            
        Returns:
            eGFR 值、CKD 分期、臨床解讀和建議
            
        Reference:
            Inker LA, et al. N Engl J Med. 2021;385(19):1737-1749.
        """
        request = CalculateRequest(
            tool_id="ckd_epi_2021",
            params={"serum_creatinine": serum_creatinine, "age": age, "sex": sex}
        )
        response = use_case.execute(request)
        return response.to_dict()
