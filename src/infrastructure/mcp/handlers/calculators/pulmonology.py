"""
Pulmonology Calculator Handlers

MCP tool handlers for pulmonology/respiratory medicine calculators.
"""

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_pulmonology_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all pulmonology calculator tools with MCP"""
    
    @mcp.tool()
    def calculate_curb65(
        confusion: Annotated[bool, Field(
            description="新發意識混亂 New mental confusion (disorientation in person, place, or time)"
        )],
        bun_gt_19_or_urea_gt_7: Annotated[bool, Field(
            description="BUN >19 mg/dL 或 Urea >7 mmol/L"
        )],
        respiratory_rate_gte_30: Annotated[bool, Field(
            description="呼吸速率 ≥30 次/分 Respiratory rate ≥30/min"
        )],
        sbp_lt_90_or_dbp_lte_60: Annotated[bool, Field(
            description="收縮壓 <90 mmHg 或 舒張壓 ≤60 mmHg (Systolic BP <90 OR Diastolic BP ≤60)"
        )],
        age_gte_65: Annotated[bool, Field(
            description="年齡 ≥65 歲 Age ≥65 years"
        )],
    ) -> dict[str, Any]:
        """
        🫁 CURB-65: 社區型肺炎嚴重度評估
        
        預測社區型肺炎 (CAP) 的 30 天死亡率，協助決定住院與否。
        
        **CURB-65 組成要素 (每項 1 分):**
        - **C**onfusion: 新發意識混亂
        - **U**rea >7 mmol/L (BUN >19 mg/dL)
        - **R**espiratory rate ≥30/min
        - **B**lood pressure: SBP <90 或 DBP ≤60 mmHg
        - **65**: 年齡 ≥65 歲
        
        **風險分層:**
        - 0-1 分: 低風險 (死亡率 <3%) → 門診治療
        - 2 分: 中度風險 (死亡率 ~9%) → 考慮住院
        - 3-5 分: 高風險 (死亡率 15-57%) → 住院/ICU
        
        **參考文獻:** Lim WS, et al. Thorax. 2003;58(5):377-382.
        PMID: 12728155
        
        Returns:
            CURB-65 分數 (0-5)、30 天死亡率、處置建議
        """
        request = CalculateRequest(
            tool_id="curb65",
            params={
                "confusion": confusion,
                "bun_gt_19_or_urea_gt_7": bun_gt_19_or_urea_gt_7,
                "respiratory_rate_gte_30": respiratory_rate_gte_30,
                "sbp_lt_90_or_dbp_lte_60": sbp_lt_90_or_dbp_lte_60,
                "age_gte_65": age_gte_65,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
