"""
GI Bleeding Calculator MCP Handlers

MCP tool handlers for gastrointestinal bleeding risk assessment:
- Glasgow-Blatchford Score (GBS): Pre-endoscopy risk stratification
- AIMS65 Score: In-hospital mortality prediction
- Rockall Score: Post-endoscopy outcome prediction

References:
- ESGE 2021 Guidelines on GI bleeding
- BSG 2019 Management of acute UGIB
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_gi_bleeding_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all GI bleeding calculator tools"""

    @mcp.tool()
    def calculate_glasgow_blatchford(
        bun_mg_dl: float,
        hemoglobin_g_dl: float,
        systolic_bp: int,
        heart_rate: int,
        sex: str,
        melena: bool = False,
        syncope: bool = False,
        hepatic_disease: bool = False,
        cardiac_failure: bool = False,
    ) -> dict[str, Any]:
        """
        🩸 Glasgow-Blatchford Score (GBS): 上消化道出血風險分層

        **ESGE 2021 推薦的 UGIB 出血前內視鏡風險評估工具**

        用於預測急性上消化道出血患者是否需要內視鏡介入或輸血。
        **GBS = 0 可安全門診追蹤，無需急診內視鏡**

        **評分項目 (總分 0-23):**
        - **BUN**: 6.5-8 +2, 8-10 +3, 10-25 +4, ≥25 +6
        - **Hemoglobin** (男): 12-13 +1, 10-12 +3, <10 +6
        - **Hemoglobin** (女): 10-12 +1, <10 +6
        - **Systolic BP**: 100-109 +1, 90-99 +2, <90 +3
        - **Heart rate ≥100**: +1
        - **Melena**: +1
        - **Syncope**: +2
        - **Hepatic disease**: +2
        - **Cardiac failure**: +2

        **風險分層:**
        - GBS 0: Very low risk - 可考慮門診治療
        - GBS 1-2: Low risk - 住院觀察
        - GBS 3-4: Intermediate risk
        - GBS ≥5: High risk - 需要介入機率高

        **參考文獻:** Blatchford O, et al. Lancet. 2000;356(9238):1318-1321.
        PMID: 11073021

        Returns:
            GBS (0-23)、需要介入機率、ESGE 處置建議
        """
        params = {
            "bun_mg_dl": bun_mg_dl,
            "hemoglobin_g_dl": hemoglobin_g_dl,
            "systolic_bp_mmhg": systolic_bp,
            "heart_rate_bpm": heart_rate,
            "sex": sex,
            "melena": melena,
            "syncope": syncope,
            "hepatic_disease": hepatic_disease,
            "cardiac_failure": cardiac_failure,
        }
        return use_case.execute(CalculateRequest(tool_id="glasgow_blatchford", params=params)).to_dict()

    @mcp.tool()
    def calculate_aims65(
        albumin_lt_3: bool,
        inr_gt_1_5: bool,
        altered_mental_status: bool,
        sbp_lte_90: bool,
        age_gte_65: bool,
    ) -> dict[str, Any]:
        """
        💉 AIMS65 Score: 上消化道出血院內死亡率預測

        簡單的 5 項指標預測 UGIB 院內死亡風險。
        與 GBS 互補使用：GBS 預測需要介入，AIMS65 預測死亡率。

        **AIMS65 五項指標 (各+1分):**
        - **A**lbumin <3.0 g/dL
        - **I**NR >1.5
        - **M**ental status altered
        - **S**ystolic BP ≤90 mmHg
        - **65** years or older

        **院內死亡率:**
        - 0 分: 0.3%
        - 1 分: 1.2%
        - 2 分: 5.3%
        - 3 分: 10.3%
        - 4 分: 23.5%
        - 5 分: 32.0%

        **臨床應用:**
        - Score 0-1: Low risk → 一般病房
        - Score 2: Intermediate → 密切監測
        - Score ≥3: High risk → ICU 考慮

        **參考文獻:** Saltzman JR, et al. Gastrointest Endosc. 2011;74(6):1215-1224.
        PMID: 21907980

        Returns:
            AIMS65 (0-5)、院內死亡率、ICU 需求建議
        """
        params = {
            "albumin_lt_3": albumin_lt_3,
            "inr_gt_1_5": inr_gt_1_5,
            "altered_mental_status": altered_mental_status,
            "sbp_lte_90": sbp_lte_90,
            "age_gte_65": age_gte_65,
        }
        return use_case.execute(CalculateRequest(tool_id="aims65", params=params)).to_dict()
