"""
Cardiology Calculator Handlers

MCP tool handlers for cardiology calculators.
"""

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_cardiology_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all cardiology calculator tools with MCP"""
    
    @mcp.tool()
    def calculate_chads2_vasc(
        chf_or_lvef_lte_40: Annotated[bool, Field(
            description="心衰竭或 LVEF ≤40% CHF or LVEF ≤40%"
        )],
        hypertension: Annotated[bool, Field(
            description="高血壓病史 History of hypertension"
        )],
        age_gte_75: Annotated[bool, Field(
            description="年齡 ≥75 歲 Age ≥75 years (+2 points)"
        )],
        diabetes: Annotated[bool, Field(
            description="糖尿病 Diabetes mellitus"
        )],
        stroke_tia_or_te_history: Annotated[bool, Field(
            description="中風/TIA/血栓栓塞病史 Prior stroke, TIA, or thromboembolism (+2 points)"
        )],
        vascular_disease: Annotated[bool, Field(
            description="血管疾病 Prior MI, PAD, or aortic plaque"
        )],
        age_65_to_74: Annotated[bool, Field(
            description="年齡 65-74 歲 Age 65-74 years (if not ≥75)"
        )],
        female_sex: Annotated[bool, Field(
            description="女性 Female sex"
        )],
    ) -> dict[str, Any]:
        """
        🫀 CHA₂DS₂-VASc: 心房顫動中風風險評估
        
        評估非瓣膜性心房顫動患者的年中風風險，指導抗凝治療決策。
        
        **計分項目:**
        - **C**HF/LVEF ≤40%: +1
        - **H**ypertension: +1
        - **A₂**ge ≥75: +2
        - **D**iabetes: +1
        - **S₂**troke/TIA/TE: +2
        - **V**ascular disease: +1
        - **A**ge 65-74: +1
        - **S**ex category (female): +1
        
        **抗凝建議 (ESC 2020):**
        - 0分 (男) / 1分 (女): 不需抗凝
        - 1分 (男): 考慮抗凝
        - ≥2分: 建議抗凝 (DOAC 優先於 Warfarin)
        
        **參考文獻:** Lip GY, et al. Chest. 2010;137(2):263-272.
        PMID: 19762550
        
        Returns:
            CHA₂DS₂-VASc 分數 (0-9)、年中風風險、抗凝建議
        """
        request = CalculateRequest(
            tool_id="chads2_vasc",
            params={
                "chf_or_lvef_lte_40": chf_or_lvef_lte_40,
                "hypertension": hypertension,
                "age_gte_75": age_gte_75,
                "diabetes": diabetes,
                "stroke_tia_or_te_history": stroke_tia_or_te_history,
                "vascular_disease": vascular_disease,
                "age_65_to_74": age_65_to_74,
                "female_sex": female_sex,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
    
    @mcp.tool()
    def calculate_heart_score(
        history_score: Annotated[int, Field(
            ge=0, le=2,
            description="病史可疑程度 History: 0=slightly suspicious, 1=moderately, 2=highly suspicious"
        )],
        ecg_score: Annotated[int, Field(
            ge=0, le=2,
            description="心電圖 ECG: 0=normal, 1=non-specific changes, 2=significant ST deviation"
        )],
        age_score: Annotated[int, Field(
            ge=0, le=2,
            description="年齡 Age: 0=<45y, 1=45-64y, 2=≥65y"
        )],
        risk_factors_score: Annotated[int, Field(
            ge=0, le=2,
            description="危險因子 Risk factors: 0=none, 1=1-2, 2=≥3 or known atherosclerosis"
        )],
        troponin_score: Annotated[int, Field(
            ge=0, le=2,
            description="肌鈣蛋白 Troponin: 0=normal, 1=1-3× ULN, 2=>3× ULN"
        )],
    ) -> dict[str, Any]:
        """
        🫀 HEART Score: 急診胸痛 MACE 風險分層
        
        評估急診胸痛患者發生主要心臟不良事件 (MACE) 的風險，
        協助決定出院或住院。
        
        **HEART 組成要素 (每項 0-2 分):**
        - **H**istory: 病史可疑程度
        - **E**CG: 心電圖變化
        - **A**ge: 年齡
        - **R**isk factors: 危險因子
        - **T**roponin: 肌鈣蛋白
        
        **風險分層 (6週 MACE):**
        - 0-3 分: 低風險 (0.9-1.7%) → 考慮早期出院
        - 4-6 分: 中度風險 (12-16.6%) → 住院觀察
        - 7-10 分: 高風險 (50-65%) → 住院介入
        
        **危險因子包括:** HTN, DM, hyperlipidemia, 
        current smoking, family history of CAD, obesity (BMI>30)
        
        **參考文獻:** Six AJ, et al. Neth Heart J. 2008;16(6):191-196.
        PMID: 18665203
        
        Returns:
            HEART Score (0-10)、6 週 MACE 風險、處置建議
        """
        request = CalculateRequest(
            tool_id="heart_score",
            params={
                "history_score": history_score,
                "ecg_score": ecg_score,
                "age_score": age_score,
                "risk_factors_score": risk_factors_score,
                "troponin_score": troponin_score,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
