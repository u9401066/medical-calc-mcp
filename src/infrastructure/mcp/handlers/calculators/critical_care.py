"""
Critical Care / ICU Calculator Tools

MCP tool handlers for critical care and ICU calculators.
"""

from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_critical_care_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all critical care/ICU calculator tools with MCP"""
    
    @mcp.tool()
    def calculate_apache_ii(
        temperature: float,
        mean_arterial_pressure: float,
        heart_rate: float,
        respiratory_rate: float,
        fio2: float,
        arterial_ph: float = 7.40,
        serum_sodium: float = 140.0,
        serum_potassium: float = 4.0,
        serum_creatinine: float = 1.0,
        hematocrit: float = 40.0,
        wbc_count: float = 10.0,
        gcs_score: int = 15,
        age: int = 50,
        pao2: Optional[float] = None,
        aado2: Optional[float] = None,
        chronic_conditions: Optional[list[str]] = None,
        admission_type: str = "nonoperative",
        acute_renal_failure: bool = False
    ) -> dict[str, Any]:
        """
        計算 APACHE II 分數 (ICU 嚴重度評估)
        
        Estimate ICU mortality based on acute physiology and chronic health.
        
        Args:
            temperature: 體溫 (°C)
            mean_arterial_pressure: 平均動脈壓 (mmHg)
            heart_rate: 心率 (bpm)
            respiratory_rate: 呼吸速率 (次/分)
            fio2: 吸入氧濃度 (0.21-1.0)
            arterial_ph: 動脈血 pH (預設 7.40)
            serum_sodium: 血鈉 (mEq/L, 預設 140)
            serum_potassium: 血鉀 (mEq/L, 預設 4.0)
            serum_creatinine: 血肌酐 (mg/dL, 預設 1.0)
            hematocrit: 血球容積比 (%, 預設 40)
            wbc_count: 白血球計數 (×10³/µL, 預設 10)
            gcs_score: 格拉斯哥昏迷指數 (3-15, 預設 15)
            age: 年齡 (歲)
            pao2: 動脈血氧分壓 (mmHg, FiO2<0.5 時使用)
            aado2: 肺泡-動脈氧分壓差 (mmHg, FiO2≥0.5 時使用)
            chronic_conditions: 慢性健康問題清單
            admission_type: 入院類型
            acute_renal_failure: 是否有急性腎衰竭
            
        Returns:
            APACHE II 分數、預估死亡率、建議
        """
        request = CalculateRequest(
            tool_id="apache_ii",
            params={
                "temperature": temperature,
                "mean_arterial_pressure": mean_arterial_pressure,
                "heart_rate": heart_rate,
                "respiratory_rate": respiratory_rate,
                "fio2": fio2,
                "arterial_ph": arterial_ph,
                "serum_sodium": serum_sodium,
                "serum_potassium": serum_potassium,
                "serum_creatinine": serum_creatinine,
                "hematocrit": hematocrit,
                "wbc_count": wbc_count,
                "gcs_score": gcs_score,
                "age": age,
                "pao2": pao2,
                "aado2": aado2,
                "chronic_health_conditions": tuple(chronic_conditions or []),
                "admission_type": admission_type,
                "acute_renal_failure": acute_renal_failure
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
    
    @mcp.tool()
    def calculate_rass(rass_score: int) -> dict[str, Any]:
        """
        RASS 鎮靜躁動評估量表
        
        Assess level of agitation or sedation in ICU patients.
        
        Args:
            rass_score: RASS 分數 (-5 到 +4)
                +4: 好鬥 (Combative)
                +3: 非常躁動 (Very agitated)
                +2: 躁動 (Agitated)
                +1: 不安 (Restless)
                 0: 警醒平靜 (Alert and calm)
                -1: 嗜睡 (Drowsy)
                -2: 輕度鎮靜 (Light sedation)
                -3: 中度鎮靜 (Moderate sedation)
                -4: 深度鎮靜 (Deep sedation)
                -5: 無法喚醒 (Unarousable)
                
        Returns:
            RASS 解讀、鎮靜程度評估、建議
        """
        request = CalculateRequest(
            tool_id="rass",
            params={"rass_score": rass_score}
        )
        response = use_case.execute(request)
        return response.to_dict()
    
    @mcp.tool()
    def calculate_sofa(
        pao2_fio2_ratio: float,
        platelets: float,
        bilirubin: float,
        gcs_score: int,
        creatinine: float,
        map_value: Optional[float] = None,
        dopamine_dose: Optional[float] = None,
        dobutamine_any: bool = False,
        epinephrine_dose: Optional[float] = None,
        norepinephrine_dose: Optional[float] = None,
        is_mechanically_ventilated: bool = False,
        urine_output_24h: Optional[float] = None,
    ) -> dict[str, Any]:
        """
        計算 SOFA 分數 (Sequential Organ Failure Assessment)
        
        SOFA 評估六個器官系統功能，是 Sepsis-3 診斷標準的核心。
        SOFA ≥2 分在懷疑感染時符合敗血症定義。
        
        Args:
            pao2_fio2_ratio: PaO2/FiO2 比值 (mmHg)
            platelets: 血小板計數 (×10³/µL)
            bilirubin: 總膽紅素 (mg/dL)
            gcs_score: 格拉斯哥昏迷指數 (3-15)
            creatinine: 血清肌酐 (mg/dL)
            map_value: 平均動脈壓 (mmHg)
            dopamine_dose: Dopamine 劑量 (µg/kg/min)
            dobutamine_any: 是否使用 Dobutamine
            epinephrine_dose: Epinephrine 劑量 (µg/kg/min)
            norepinephrine_dose: Norepinephrine 劑量 (µg/kg/min)
            is_mechanically_ventilated: 是否使用機械通氣
            urine_output_24h: 24 小時尿量 (mL)
            
        Returns:
            SOFA 分數 (0-24)、各器官分數、死亡率預測
            
        References:
            Vincent JL, et al. Intensive Care Med. 1996.
            Singer M, et al. JAMA. 2016. (Sepsis-3)
        """
        request = CalculateRequest(
            tool_id="sofa_score",
            params={
                "pao2_fio2_ratio": pao2_fio2_ratio,
                "platelets": platelets,
                "bilirubin": bilirubin,
                "gcs_score": gcs_score,
                "creatinine": creatinine,
                "map_value": map_value,
                "dopamine_dose": dopamine_dose,
                "dobutamine_any": dobutamine_any,
                "epinephrine_dose": epinephrine_dose,
                "norepinephrine_dose": norepinephrine_dose,
                "is_mechanically_ventilated": is_mechanically_ventilated,
                "urine_output_24h": urine_output_24h,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
    
    @mcp.tool()
    def calculate_qsofa(
        respiratory_rate: int,
        systolic_bp: int,
        altered_mentation: bool = False,
        gcs_score: int = 15,
    ) -> dict[str, Any]:
        """
        計算 qSOFA 分數 (Quick SOFA)
        
        qSOFA 是一個快速床邊評估工具，用於識別感染風險較高的病患。
        注意：依據 SSC 2021 指引，不建議單獨使用 qSOFA 作為敗血症篩檢工具。
        
        Args:
            respiratory_rate: 呼吸速率 (次/分)
            systolic_bp: 收縮壓 (mmHg)
            altered_mentation: 意識改變 (GCS <15 或急性意識變化)
            gcs_score: GCS 分數 (3-15)
            
        Returns:
            qSOFA 分數 (0-3) 和風險評估
        """
        request = CalculateRequest(
            tool_id="qsofa_score",
            params={
                "respiratory_rate": respiratory_rate,
                "systolic_bp": systolic_bp,
                "altered_mentation": altered_mentation,
                "gcs_score": gcs_score,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
    
    @mcp.tool()
    def calculate_news2(
        respiratory_rate: int,
        spo2: int,
        on_supplemental_o2: bool,
        temperature: float,
        systolic_bp: int,
        heart_rate: int,
        consciousness: str = "A",
        use_scale_2: bool = False,
    ) -> dict[str, Any]:
        """
        計算 NEWS2 分數 (National Early Warning Score 2)
        
        NEWS2 用於偵測住院病患的臨床惡化，觸發適當的臨床反應。
        
        Args:
            respiratory_rate: 呼吸速率 (次/分)
            spo2: 血氧飽和度 (%)
            on_supplemental_o2: 是否使用氧氣
            temperature: 體溫 (°C)
            systolic_bp: 收縮壓 (mmHg)
            heart_rate: 心率 (次/分)
            consciousness: AVPU 意識狀態 (A/V/P/U/C)
            use_scale_2: 是否使用 Scale 2（高碳酸血症呼吸衰竭）
            
        Returns:
            NEWS2 分數 (0-20) 和臨床反應建議
        """
        request = CalculateRequest(
            tool_id="news2_score",
            params={
                "respiratory_rate": respiratory_rate,
                "spo2": spo2,
                "on_supplemental_o2": on_supplemental_o2,
                "temperature": temperature,
                "systolic_bp": systolic_bp,
                "heart_rate": heart_rate,
                "consciousness": consciousness,
                "use_scale_2": use_scale_2,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
    
    @mcp.tool()
    def calculate_gcs(
        eye_response: int,
        verbal_response: int,
        motor_response: int,
        is_intubated: bool = False,
    ) -> dict[str, Any]:
        """
        計算 GCS 分數 (Glasgow Coma Scale)
        
        GCS 評估意識程度，是最廣泛使用的昏迷量表。
        
        Args:
            eye_response: 眼睛反應 (1-4)
            verbal_response: 語言反應 (1-5)
            motor_response: 運動反應 (1-6)
            is_intubated: 是否已插管
            
        Returns:
            GCS 分數 (3-15) 和腦傷嚴重度分級
        """
        request = CalculateRequest(
            tool_id="glasgow_coma_scale",
            params={
                "eye_response": eye_response,
                "verbal_response": verbal_response,
                "motor_response": motor_response,
                "is_intubated": is_intubated,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
    
    @mcp.tool()
    def calculate_cam_icu(
        rass_score: int,
        acute_onset_fluctuation: bool,
        inattention_score: int,
        altered_loc: bool = False,
        disorganized_thinking_errors: int = 0,
    ) -> dict[str, Any]:
        """
        計算 CAM-ICU (Confusion Assessment Method for ICU)
        
        CAM-ICU 是 ICU 病患譫妄篩檢的標準工具。
        
        Args:
            rass_score: RASS 分數 (-5 到 +4)
            acute_onset_fluctuation: Feature 1 - 急性發作或波動病程
            inattention_score: Feature 2 - ASE 注意力測試錯誤數
            altered_loc: Feature 3 - 意識程度改變
            disorganized_thinking_errors: Feature 4 - 思維障礙測試錯誤數
            
        Returns:
            CAM-ICU 結果和建議
        """
        request = CalculateRequest(
            tool_id="cam_icu",
            params={
                "rass_score": rass_score,
                "acute_onset_fluctuation": acute_onset_fluctuation,
                "inattention_score": inattention_score,
                "altered_loc": altered_loc,
                "disorganized_thinking_errors": disorganized_thinking_errors,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
