"""
Anesthesiology / Preoperative Calculator Tools

MCP tool handlers for anesthesiology and preoperative calculators.
"""

from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_anesthesiology_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all anesthesiology/preoperative calculator tools with MCP"""
    
    @mcp.tool()
    def calculate_asa_physical_status(
        asa_class: int,
        is_emergency: bool = False
    ) -> dict[str, Any]:
        """
        ASA 身體狀態分級
        
        Classify patient using ASA Physical Status Classification (I-VI).
        
        Args:
            asa_class: ASA 分級 (1-6)
                1: 健康病人
                2: 輕度全身性疾病
                3: 嚴重全身性疾病
                4: 持續威脅生命的嚴重全身性疾病
                5: 瀕死病人，不手術無法存活
                6: 腦死器官捐贈者
            is_emergency: 是否為緊急手術 (加 E 字尾)
            
        Returns:
            ASA 分級、描述、周術期死亡率風險估計
        """
        request = CalculateRequest(
            tool_id="asa_physical_status",
            params={"asa_class": asa_class, "is_emergency": is_emergency}
        )
        response = use_case.execute(request)
        return response.to_dict()
    
    @mcp.tool()
    def calculate_mallampati(mallampati_class: int) -> dict[str, Any]:
        """
        Mallampati 氣道評估分級
        
        Predict difficult intubation using Modified Mallampati Classification.
        
        Args:
            mallampati_class: Mallampati 分級 (1-4)
                1: 可見軟顎、懸雍垂、咽門弓
                2: 可見軟顎、懸雍垂
                3: 可見軟顎、懸雍垂基部
                4: 只可見硬顎
                
        Returns:
            分級、困難插管風險評估、建議
        """
        request = CalculateRequest(
            tool_id="mallampati_score",
            params={"mallampati_class": mallampati_class}
        )
        response = use_case.execute(request)
        return response.to_dict()
    
    @mcp.tool()
    def calculate_rcri(
        high_risk_surgery: bool = False,
        ischemic_heart_disease: bool = False,
        heart_failure: bool = False,
        cerebrovascular_disease: bool = False,
        insulin_diabetes: bool = False,
        creatinine_above_2: bool = False
    ) -> dict[str, Any]:
        """
        計算 RCRI 心臟風險指數 (Lee Index)
        
        Estimate risk of major cardiac complications after non-cardiac surgery.
        
        Args:
            high_risk_surgery: 高風險手術（腹腔內、胸腔內、主動脈上血管手術）
            ischemic_heart_disease: 缺血性心臟病史
            heart_failure: 心衰竭病史
            cerebrovascular_disease: 腦血管疾病史
            insulin_diabetes: 需胰島素治療的糖尿病
            creatinine_above_2: 肌酐 >2 mg/dL
            
        Returns:
            RCRI 分數 (0-6)、心臟併發症風險百分比、建議
        """
        request = CalculateRequest(
            tool_id="rcri",
            params={
                "high_risk_surgery": high_risk_surgery,
                "ischemic_heart_disease": ischemic_heart_disease,
                "heart_failure": heart_failure,
                "cerebrovascular_disease": cerebrovascular_disease,
                "insulin_diabetes": insulin_diabetes,
                "creatinine_above_2": creatinine_above_2
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
