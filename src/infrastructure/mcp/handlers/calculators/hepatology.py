"""
Hepatology Calculator Handlers

MCP tool handlers for hepatology/gastroenterology calculators.
"""

from typing import Annotated, Any, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_hepatology_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all hepatology calculator tools with MCP"""
    
    @mcp.tool()
    def calculate_meld_score(
        creatinine: Annotated[float, Field(
            gt=0, le=15.0,
            description="血清肌酸酐 Serum creatinine | Unit: mg/dL | Range: 0.5-15.0"
        )],
        bilirubin: Annotated[float, Field(
            gt=0, le=50.0,
            description="總膽紅素 Total bilirubin | Unit: mg/dL | Range: 0.1-50.0"
        )],
        inr: Annotated[float, Field(
            gt=0, le=10.0,
            description="國際標準化比值 INR | Range: 1.0-10.0"
        )],
        sodium: Annotated[float, Field(
            ge=100, le=160,
            description="血清鈉 Serum sodium | Unit: mEq/L | Range: 100-160 (用於 MELD-Na)"
        )] = 137.0,
        on_dialysis: Annotated[bool, Field(
            description="透析狀態 Dialyzed ≥2x/week or CVVHD? | If true, Cr is set to 4.0"
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

    @mcp.tool()
    def calculate_child_pugh(
        bilirubin: Annotated[float, Field(
            gt=0, le=30.0,
            description="總膽紅素 Total bilirubin | Unit: mg/dL | Range: 0.1-30.0"
        )],
        albumin: Annotated[float, Field(
            gt=0, le=6.0,
            description="血清白蛋白 Serum albumin | Unit: g/dL | Range: 1.0-6.0"
        )],
        inr: Annotated[float, Field(
            gt=0, le=6.0,
            description="國際標準化比值 INR | Range: 1.0-6.0"
        )],
        ascites: Annotated[
            Literal["none", "mild", "moderate_severe"],
            Field(description="腹水狀態 Ascites status | Options: 'none'=無, 'mild'=輕度/可控, 'moderate_severe'=中重度")
        ],
        encephalopathy_grade: Annotated[
            Literal[0, 1, 2, 3, 4],
            Field(description="肝腦病變分級 Hepatic encephalopathy | 0=無, 1=輕度混亂, 2=嗜睡, 3=半昏迷, 4=昏迷")
        ],
    ) -> dict[str, Any]:
        """
        🫀 Child-Pugh Score: 肝硬化嚴重度評估
        
        評估慢性肝病（肝硬化）的嚴重程度，用於預後及治療決策。
        
        **計分標準 (5項指標，每項1-3分):**
        
        | 參數 | 1分 | 2分 | 3分 |
        |------|-----|-----|-----|
        | Bilirubin (mg/dL) | <2 | 2-3 | >3 |
        | Albumin (g/dL) | >3.5 | 2.8-3.5 | <2.8 |
        | INR | <1.7 | 1.7-2.2 | >2.2 |
        | 腹水 | 無 | 輕度 | 中重度 |
        | 肝腦病變 | 無 | I-II級 | III-IV級 |
        
        **分級與預後:**
        - Class A (5-6分): 代償良好，1年存活率 ~100%
        - Class B (7-9分): 功能受損，1年存活率 ~80%
        - Class C (10-15分): 失代償，1年存活率 ~45%
        
        **臨床應用:**
        - 肝硬化預後評估
        - 手術風險分層（圍手術期死亡率）
        - 肝移植評估（常與 MELD 互補）
        - 肝功能不全時藥物劑量調整
        
        **參考文獻:** 
        - Pugh RNH, et al. Br J Surg. 1973;60(8):646-649. PMID: 4541913
        - Child CG, Turcotte JG. The Liver and Portal Hypertension. 1964.
        
        Returns:
            Child-Pugh 分數 (5-15)、分級 (A/B/C)、存活率估計
        """
        request = CalculateRequest(
            tool_id="child_pugh",
            params={
                "bilirubin": bilirubin,
                "albumin": albumin,
                "inr": inr,
                "ascites": ascites,
                "encephalopathy_grade": encephalopathy_grade,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
