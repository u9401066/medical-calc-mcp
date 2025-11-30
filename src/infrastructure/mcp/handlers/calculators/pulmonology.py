"""
Pulmonology Calculator Handlers

MCP tool handlers for pulmonology/respiratory medicine calculators.
"""

from typing import Annotated, Any, Optional

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
            description="BUN >19 mg/dL 或 Urea >7 mmol/L (Blood urea nitrogen elevated)"
        )],
        respiratory_rate_gte_30: Annotated[bool, Field(
            description="呼吸速率 ≥30/min Respiratory rate ≥30 breaths per minute"
        )],
        sbp_lt_90_or_dbp_lte_60: Annotated[bool, Field(
            description="低血壓 Low BP: Systolic <90 mmHg OR Diastolic ≤60 mmHg"
        )],
        age_gte_65: Annotated[bool, Field(
            description="年齡 ≥65歲 Age ≥65 years"
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
    
    @mcp.tool()
    def calculate_psi_port(
        age_years: Annotated[int, Field(ge=18, le=120, description="年齡 Age | Unit: years | Range: 18-120")],
        female: Annotated[bool, Field(description="女性 Female (age -10 points)")] = False,
        nursing_home_resident: Annotated[bool, Field(description="護理之家住民 Nursing home resident (+10)")] = False,
        # Comorbidities
        neoplastic_disease: Annotated[bool, Field(description="惡性腫瘤 Active neoplastic disease (+30)")] = False,
        liver_disease: Annotated[bool, Field(description="肝病 Liver disease (+20)")] = False,
        chf: Annotated[bool, Field(description="心衰竭 Congestive heart failure (+10)")] = False,
        cerebrovascular_disease: Annotated[bool, Field(description="腦血管疾病 Cerebrovascular disease (+10)")] = False,
        renal_disease: Annotated[bool, Field(description="腎病 Renal disease (+10)")] = False,
        # Physical exam findings
        altered_mental_status: Annotated[bool, Field(description="意識改變 Altered mental status (+20)")] = False,
        respiratory_rate_gte_30: Annotated[bool, Field(description="呼吸速率 ≥30/min (+20)")] = False,
        systolic_bp_lt_90: Annotated[bool, Field(description="收縮壓 <90 mmHg (+20)")] = False,
        temperature_abnormal: Annotated[bool, Field(description="體溫 <35°C 或 ≥40°C (+15)")] = False,
        pulse_gte_125: Annotated[bool, Field(description="心跳 ≥125/min (+10)")] = False,
        # Laboratory/radiology findings
        arterial_ph_lt_7_35: Annotated[bool, Field(description="動脈血 pH <7.35 (+30)")] = False,
        bun_gte_30: Annotated[bool, Field(description="BUN ≥30 mg/dL 或 ≥11 mmol/L (+20)")] = False,
        sodium_lt_130: Annotated[bool, Field(description="鈉 <130 mEq/L (+20)")] = False,
        glucose_gte_250: Annotated[bool, Field(description="血糖 ≥250 mg/dL (+10)")] = False,
        hematocrit_lt_30: Annotated[bool, Field(description="血比容 <30% (+10)")] = False,
        pao2_lt_60_or_sao2_lt_90: Annotated[bool, Field(description="PaO2 <60 mmHg 或 SaO2 <90% (+10)")] = False,
        pleural_effusion: Annotated[bool, Field(description="肋膜積液 Pleural effusion (+10)")] = False,
    ) -> dict[str, Any]:
        """
        🫁 PSI/PORT Score: 肺炎嚴重度指數
        
        評估社區型肺炎 (CAP) 患者的死亡風險，協助決定門診或住院治療。
        
        **計分方式:**
        - 人口學：男性=年齡，女性=年齡-10，護理之家+10
        - 共病：惡性腫瘤+30、肝病+20、心衰+10、腦血管病+10、腎病+10
        - 理學檢查：意識改變+20、RR≥30+20、SBP<90+20、體溫異常+15、HR≥125+10
        - 實驗室：pH<7.35+30、BUN≥30+20、Na<130+20、Glucose≥250+10、Hct<30%+10、低血氧+10、肋膜積液+10
        
        **風險分級與 30 天死亡率:**
        - Class I: ≤50歲無共病無異常生命徵象 → 0.1-0.4% → 門診
        - Class II: ≤70 分 → 0.6-0.7% → 門診  
        - Class III: 71-90 分 → 0.9-2.8% → 短期住院/觀察
        - Class IV: 91-130 分 → 8.2-9.3% → 住院
        - Class V: >130 分 → 27-31% → 住院/考慮 ICU
        
        **參考文獻:** Fine MJ, et al. N Engl J Med. 1997;336(4):243-250.
        PMID: 8995086
        
        Returns:
            PSI 分數、風險等級、30 天死亡率、處置建議
        """
        request = CalculateRequest(
            tool_id="psi_port",
            params={
                "age_years": age_years,
                "female": female,
                "nursing_home_resident": nursing_home_resident,
                "neoplastic_disease": neoplastic_disease,
                "liver_disease": liver_disease,
                "chf": chf,
                "cerebrovascular_disease": cerebrovascular_disease,
                "renal_disease": renal_disease,
                "altered_mental_status": altered_mental_status,
                "respiratory_rate_gte_30": respiratory_rate_gte_30,
                "systolic_bp_lt_90": systolic_bp_lt_90,
                "temperature_abnormal": temperature_abnormal,
                "pulse_gte_125": pulse_gte_125,
                "arterial_ph_lt_7_35": arterial_ph_lt_7_35,
                "bun_gte_30": bun_gte_30,
                "sodium_lt_130": sodium_lt_130,
                "glucose_gte_250": glucose_gte_250,
                "hematocrit_lt_30": hematocrit_lt_30,
                "pao2_lt_60_or_sao2_lt_90": pao2_lt_60_or_sao2_lt_90,
                "pleural_effusion": pleural_effusion,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
    
    @mcp.tool()
    def calculate_aa_gradient(
        pao2: Annotated[float, Field(
            ge=10, le=700,
            description="動脈血氧分壓 Arterial PaO₂ | Unit: mmHg | Range: 10-700"
        )],
        paco2: Annotated[float, Field(
            ge=10, le=150,
            description="動脈血二氧化碳分壓 Arterial PaCO₂ | Unit: mmHg | Range: 10-150"
        )],
        fio2: Annotated[float, Field(
            ge=0.21, le=1.0,
            description="吸入氧濃度 FiO₂ | Range: 0.21-1.0 (e.g., 0.21 = room air)"
        )],
        age: Annotated[Optional[int], Field(
            ge=0, le=120,
            description="年齡 Age (for expected normal calculation) | Unit: years | Range: 0-120"
        )] = None,
        atmospheric_pressure: Annotated[float, Field(
            ge=500, le=800,
            description="大氣壓力 Atmospheric pressure | Unit: mmHg | Default: 760 (sea level)"
        )] = 760.0,
        respiratory_quotient: Annotated[float, Field(
            ge=0.7, le=1.0,
            description="呼吸商 Respiratory quotient (RQ) | Default: 0.8"
        )] = 0.8,
    ) -> dict[str, Any]:
        """
        🫁 A-a Gradient: 肺泡-動脈氧氣梯度
        
        計算肺泡氧分壓 (PAO₂) 與動脈氧分壓 (PaO₂) 的差值，
        用於評估低血氧原因與氣體交換效率。
        
        **公式:**
        A-a Gradient = PAO₂ - PaO₂
        
        PAO₂ = FiO₂ × (Patm - PH₂O) - (PaCO₂ / RQ)
        - PH₂O = 47 mmHg (37°C 水蒸氣壓)
        - RQ = 0.8 (呼吸商)
        
        **年齡校正正常值:**
        Expected A-a = 2.5 + (0.21 × 年齡)
        
        正常上限 (室內空氣):
        - < 40 歲: < 15-20 mmHg
        - ≥ 40 歲: 約 (年齡/4) + 4
        
        **臨床判讀:**
        - **正常 A-a + 低血氧**: 低通氣 (CNS抑制、神經肌肉疾病)、低吸入氧 (高海拔)
        - **升高 A-a + 低血氧**: 
          - V/Q 不配合 (COPD, 氣喘, PE)
          - 分流 (ARDS, 肺炎, 肺不張, AVM)
          - 擴散障礙 (間質性肺病, 肺水腫)
        
        **參考文獻:** West Respiratory Physiology 2016, Kanber 1968. PMID: 5638666
        
        Returns:
            A-a 梯度 (mmHg)、是否升高、鑑別診斷方向
        """
        request = CalculateRequest(
            tool_id="aa_gradient",
            params={
                "pao2": pao2,
                "paco2": paco2,
                "fio2": fio2,
                "age": age,
                "atmospheric_pressure": atmospheric_pressure,
                "respiratory_quotient": respiratory_quotient,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
