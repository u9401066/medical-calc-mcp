"""
Anesthesiology / Preoperative Calculator Tools

MCP tool handlers for anesthesiology and preoperative calculators.
Uses Annotated + Field for rich parameter descriptions in JSON Schema.
"""

from typing import Any, Annotated

from pydantic import Field
from mcp.server.fastmcp import FastMCP

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_anesthesiology_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all anesthesiology/preoperative calculator tools with MCP"""
    
    @mcp.tool()
    def calculate_asa_physical_status(
        asa_class: Annotated[int, Field(description="ASA分級 1-6: 1=健康, 2=輕度, 3=嚴重, 4=致命, 5=瀕死, 6=腦死")],
        is_emergency: Annotated[bool, Field(description="是否緊急手術 (adds 'E' suffix)", default=False)]
    ) -> dict[str, Any]:
        """
        ASA 身體狀態分級 (ASA Physical Status Classification)
        
        Classify patient overall health for perioperative risk.
        I=Healthy, II=Mild, III=Severe, IV=Life-threatening, V=Moribund, VI=Brain-dead.
        """
        request = CalculateRequest(
            tool_id="asa_physical_status",
            params={"asa_class": asa_class, "is_emergency": is_emergency}
        )
        response = use_case.execute(request)
        return response.to_dict()
    
    @mcp.tool()
    def calculate_mallampati(
        mallampati_class: Annotated[int, Field(description="Mallampati分級 1-4: 1=全視野, 2=部分懸雍垂, 3=軟顎, 4=硬顎")]
    ) -> dict[str, Any]:
        """
        Mallampati 氣道評估分級 (Modified Mallampati Classification)
        
        Predict difficult intubation. Higher class = higher difficulty.
        I=Easy, IV=Most difficult.
        """
        request = CalculateRequest(
            tool_id="mallampati_score",
            params={"mallampati_class": mallampati_class}
        )
        response = use_case.execute(request)
        return response.to_dict()
    
    @mcp.tool()
    def calculate_rcri(
        high_risk_surgery: Annotated[bool, Field(description="高風險手術 Intra-abdominal/thoracic/suprainguinal vascular", default=False)],
        ischemic_heart_disease: Annotated[bool, Field(description="缺血性心臟病 MI/angina/positive stress test", default=False)],
        heart_failure: Annotated[bool, Field(description="心衰竭 CHF/pulmonary edema/S3/rales", default=False)],
        cerebrovascular_disease: Annotated[bool, Field(description="腦血管疾病 TIA or stroke history", default=False)],
        insulin_diabetes: Annotated[bool, Field(description="胰島素糖尿病 Preop insulin use", default=False)],
        creatinine_above_2: Annotated[bool, Field(description="肌酐>2 Preop Cr >2.0 mg/dL", default=False)]
    ) -> dict[str, Any]:
        """
        計算 RCRI 心臟風險指數 (Revised Cardiac Risk Index)
        
        Cardiac risk for non-cardiac surgery. Score 0-6.
        0=0.4%, 1=0.9%, 2=6.6%, ≥3=11% major cardiac event.
        
        Reference: Lee TH, Circulation 1999.
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
