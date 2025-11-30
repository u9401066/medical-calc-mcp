"""
Hepatology Calculator Handlers

MCP tool handlers for hepatology/gastroenterology calculators.
"""

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_hepatology_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all hepatology calculator tools with MCP"""
    
    @mcp.tool()
    def calculate_meld_score(
        creatinine: Annotated[float, Field(
            gt=0,
            description="血清肌酸酐 Serum creatinine (mg/dL)"
        )],
        bilirubin: Annotated[float, Field(
            gt=0,
            description="總膽紅素 Total bilirubin (mg/dL)"
        )],
        inr: Annotated[float, Field(
            gt=0,
            description="國際標準化比值 International Normalized Ratio (INR)"
        )],
        sodium: Annotated[float, Field(
            default=137.0,
            description="血清鈉 Serum sodium (mEq/L), default 137"
        )] = 137.0,
        on_dialysis: Annotated[bool, Field(
            description="透析 Dialyzed ≥2x in past week or CVVHD (sets Cr to 4.0)"
        )] = False,
    ) -> dict[str, Any]:
        """
        🫀 MELD Score: 末期肝病預後評估
        
        預測末期肝病患者的 90 天死亡率，用於肝臟移植優先排序。
        
        **輸入參數:**
        - Creatinine (mg/dL): 最小 1.0, 最大 4.0
        - Bilirubin (mg/dL): 最小 1.0
        - INR: 最小 1.0
        - Sodium (mEq/L): 範圍 125-137 (用於 MELD-Na)
        - 透析: 若每週 ≥2 次透析，Cr 設為 4.0
        
        **MELD 公式:**
        MELD = 10 × [0.957×ln(Cr) + 0.378×ln(Bili) + 1.120×ln(INR)] + 6.43
        
        **MELD-Na 公式 (UNOS 2016):**
        MELD-Na = MELD + 1.32×(137-Na) - 0.033×MELD×(137-Na)
        
        **90 天死亡率:**
        - <10: 1.9%
        - 10-19: 6.0%
        - 20-29: 19.6%
        - 30-39: 52.6%
        - ≥40: 71.3%
        
        **參考文獻:** 
        - Kamath PS, et al. Hepatology. 2001;33(2):464-470. PMID: 11172350
        - Kim WR, et al. N Engl J Med. 2008;359(10):1018-1026. PMID: 18768945
        
        Returns:
            MELD 分數、MELD-Na 分數、90 天死亡率、移植建議
        """
        request = CalculateRequest(
            tool_id="meld_score",
            params={
                "creatinine": creatinine,
                "bilirubin": bilirubin,
                "inr": inr,
                "sodium": sodium,
                "on_dialysis": on_dialysis,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
