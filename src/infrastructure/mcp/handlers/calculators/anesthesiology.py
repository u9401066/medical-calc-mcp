"""
Anesthesiology / Preoperative Calculator Tools

MCP tool handlers for anesthesiology and preoperative calculators.
Uses Annotated + Field for rich parameter descriptions in JSON Schema.
"""

from typing import Any, Annotated, Literal

from pydantic import Field
from mcp.server.fastmcp import FastMCP

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_anesthesiology_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all anesthesiology/preoperative calculator tools with MCP"""
    
    @mcp.tool()
    def calculate_asa_physical_status(
        asa_class: Annotated[
            Literal[1, 2, 3, 4, 5, 6],
            Field(description="ASA分級 ASA Physical Status | Options: 1=健康Healthy, 2=輕度Mild, 3=嚴重Severe, 4=致命Life-threatening, 5=瀕死Moribund, 6=腦死Brain-dead")
        ],
        is_emergency: Annotated[bool, Field(description="是否緊急手術 Emergency surgery (adds 'E' suffix)")] = False
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
    def calculate_apfel_ponv(
        female_gender: Annotated[bool, Field(description="女性 Female gender")],
        history_motion_sickness_or_ponv: Annotated[bool, Field(description="暈動病或PONV病史 History of motion sickness or previous PONV")],
        non_smoker: Annotated[bool, Field(description="不吸菸 Non-smoker (does NOT currently smoke)")],
        postoperative_opioids: Annotated[bool, Field(description="術後使用鴉片類藥物 Postoperative opioids planned/anticipated")]
    ) -> dict[str, Any]:
        """
        🤢 Apfel Score: 術後噁心嘔吐風險評估 (PONV Risk Score)
        
        預測成人全身麻醉後發生術後噁心嘔吐的風險，指導預防性止吐藥使用。
        
        **四個風險因子 (各+1分):**
        - **F**emale gender: 女性
        - **H**istory: 暈動病或 PONV 病史
        - **N**on-smoking: 不吸菸者
        - **O**pioids: 術後使用鴉片類藥物
        
        **PONV 風險:**
        - 0 因子: ~10%
        - 1 因子: ~21%
        - 2 因子: ~39% → 考慮預防
        - 3 因子: ~61% → 建議多重預防
        - 4 因子: ~79% → 積極多重預防
        
        **預防策略:**
        - ≥2 風險因子: 雙重止吐預防 (Ondansetron + Dexamethasone)
        - ≥3 風險因子: 多重預防 + TIVA + 減少鴉片類
        
        **參考文獻:** Apfel CC, et al. Anesthesiology. 1999;91(3):693-700.
        PMID: 10485781
        
        Returns:
            Apfel 分數 (0-4)、PONV 風險百分比、預防建議
        """
        request = CalculateRequest(
            tool_id="apfel_ponv",
            params={
                "female_gender": female_gender,
                "history_motion_sickness_or_ponv": history_motion_sickness_or_ponv,
                "non_smoker": non_smoker,
                "postoperative_opioids": postoperative_opioids
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
    
    @mcp.tool()
    def calculate_mallampati(
        mallampati_class: Annotated[
            Literal[1, 2, 3, 4],
            Field(description="Mallampati分級 Mallampati Class | Options: 1=全視野Full visibility, 2=部分懸雍垂Partial uvula, 3=軟顎Soft palate only, 4=硬顎Hard palate only")
        ]
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
        high_risk_surgery: Annotated[bool, Field(description="高風險手術 High-risk surgery (intra-abdominal/thoracic/suprainguinal vascular)")] = False,
        ischemic_heart_disease: Annotated[bool, Field(description="缺血性心臟病 Ischemic heart disease (MI/angina/positive stress test)")] = False,
        heart_failure: Annotated[bool, Field(description="心衰竭 Heart failure (CHF/pulmonary edema/S3/rales)")] = False,
        cerebrovascular_disease: Annotated[bool, Field(description="腦血管疾病 Cerebrovascular disease (TIA or stroke history)")] = False,
        insulin_diabetes: Annotated[bool, Field(description="胰島素糖尿病 Insulin-dependent diabetes mellitus")] = False,
        creatinine_above_2: Annotated[bool, Field(description="肌酐>2 Preoperative Cr >2.0 mg/dL")] = False
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
