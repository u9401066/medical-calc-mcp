"""
Critical Care / ICU Calculator Tools

MCP tool handlers for critical care and ICU calculators.
Uses Annotated + Field to provide rich parameter descriptions in JSON Schema.
"""

from typing import Any, Optional, Annotated, List

from pydantic import Field
from mcp.server.fastmcp import FastMCP

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_critical_care_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all critical care/ICU calculator tools with MCP"""
    
    @mcp.tool()
    def calculate_apache_ii(
        temperature: Annotated[float, Field(description="體溫 Temperature in °C (36.0-40.0)")],
        mean_arterial_pressure: Annotated[float, Field(description="平均動脈壓 MAP in mmHg (50-160)")],
        heart_rate: Annotated[float, Field(description="心率 Heart rate in bpm (40-180)")],
        respiratory_rate: Annotated[float, Field(description="呼吸速率 RR in breaths/min (10-50)")],
        fio2: Annotated[float, Field(description="吸入氧濃度 FiO2 (0.21-1.0)")],
        arterial_ph: Annotated[float, Field(description="動脈血 pH (7.15-7.70)", default=7.40)],
        serum_sodium: Annotated[float, Field(description="血鈉 Sodium in mEq/L (120-160)", default=140.0)],
        serum_potassium: Annotated[float, Field(description="血鉀 Potassium in mEq/L (2.5-7.0)", default=4.0)],
        serum_creatinine: Annotated[float, Field(description="血肌酐 Creatinine in mg/dL (0.5-15.0)", default=1.0)],
        hematocrit: Annotated[float, Field(description="血球容積比 Hematocrit in % (20-60)", default=40.0)],
        wbc_count: Annotated[float, Field(description="白血球 WBC in ×10³/µL (1-40)", default=10.0)],
        gcs_score: Annotated[int, Field(description="格拉斯哥昏迷指數 GCS (3-15)", default=15)],
        age: Annotated[int, Field(description="年齡 Age in years (18-100)", default=50)],
        pao2: Annotated[Optional[float], Field(description="動脈血氧分壓 PaO2 in mmHg (use if FiO2<0.5)", default=None)],
        aado2: Annotated[Optional[float], Field(description="肺泡動脈氧分壓差 A-a gradient mmHg (if FiO2≥0.5)", default=None)],
        chronic_conditions: Annotated[Optional[List[str]], Field(description="慢性健康問題 Chronic conditions list", default=None)],
        admission_type: Annotated[str, Field(description="入院類型: nonoperative, elective_postop, emergency_postop", default="nonoperative")],
        acute_renal_failure: Annotated[bool, Field(description="急性腎衰竭 Acute renal failure present", default=False)]
    ) -> dict[str, Any]:
        """
        計算 APACHE II 分數 (ICU 嚴重度評估)
        
        Estimate ICU mortality based on acute physiology and chronic health.
        Score range: 0-71. Higher scores indicate greater severity.
        
        Reference: Knaus WA, et al. Crit Care Med. 1985.
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
    def calculate_rass(
        rass_score: Annotated[int, Field(description="RASS分數 (-5到+4): +4=好鬥, 0=清醒平靜, -5=無法喚醒")]
    ) -> dict[str, Any]:
        """
        RASS 鎮靜躁動評估量表 (Richmond Agitation-Sedation Scale)
        
        Assess level of agitation or sedation in ICU patients.
        Target RASS: Usually 0 to -2 per PADIS guidelines.
        """
        request = CalculateRequest(
            tool_id="rass",
            params={"rass_score": rass_score}
        )
        response = use_case.execute(request)
        return response.to_dict()
    
    @mcp.tool()
    def calculate_sofa(
        pao2_fio2_ratio: Annotated[float, Field(description="PaO2/FiO2比值 mmHg (normal>400, use worst in 24h)")],
        platelets: Annotated[float, Field(description="血小板 Platelets ×10³/µL (normal 150-400)")],
        bilirubin: Annotated[float, Field(description="總膽紅素 Bilirubin mg/dL (normal <1.2)")],
        gcs_score: Annotated[int, Field(description="格拉斯哥昏迷指數 GCS 3-15 (use lowest)")],
        creatinine: Annotated[float, Field(description="血清肌酐 Creatinine mg/dL (normal 0.7-1.3)")],
        map_value: Annotated[Optional[float], Field(description="平均動脈壓 MAP mmHg (if no vasopressors)", default=None)],
        dopamine_dose: Annotated[Optional[float], Field(description="Dopamine劑量 µg/kg/min", default=None)],
        dobutamine_any: Annotated[bool, Field(description="是否使用Dobutamine (any dose)", default=False)],
        epinephrine_dose: Annotated[Optional[float], Field(description="Epinephrine劑量 µg/kg/min", default=None)],
        norepinephrine_dose: Annotated[Optional[float], Field(description="Norepinephrine劑量 µg/kg/min", default=None)],
        is_mechanically_ventilated: Annotated[bool, Field(description="是否機械通氣 (affects respiratory scoring)", default=False)],
        urine_output_24h: Annotated[Optional[float], Field(description="24h尿量 mL (for renal scoring)", default=None)],
    ) -> dict[str, Any]:
        """
        計算 SOFA 分數 (Sequential Organ Failure Assessment)
        
        SOFA evaluates 6 organ systems. Core criterion for Sepsis-3.
        SOFA ≥2 with suspected infection = Sepsis diagnosis.
        Score range: 0-24 (each organ 0-4)
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
        respiratory_rate: Annotated[int, Field(description="呼吸速率 RR breaths/min (≥22 scores 1)")],
        systolic_bp: Annotated[int, Field(description="收縮壓 SBP mmHg (≤100 scores 1)")],
        altered_mentation: Annotated[bool, Field(description="意識改變 GCS<15 or acute change (scores 1)", default=False)],
        gcs_score: Annotated[int, Field(description="GCS分數 3-15 (alt to altered_mentation)", default=15)],
    ) -> dict[str, Any]:
        """
        計算 qSOFA 分數 (Quick SOFA)
        
        Quick bedside assessment for infection risk. Score: 0-3.
        qSOFA ≥2 suggests higher risk.
        ⚠️ Per SSC 2021: Do NOT use qSOFA alone for sepsis screening.
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
        respiratory_rate: Annotated[int, Field(description="呼吸速率 RR breaths/min (8-25 normal)")],
        spo2: Annotated[int, Field(description="血氧飽和度 SpO2 % (94-100 normal on room air)")],
        on_supplemental_o2: Annotated[bool, Field(description="是否使用氧氣 (scores 2 if on O2)")],
        temperature: Annotated[float, Field(description="體溫 °C (36.1-38.0 normal)")],
        systolic_bp: Annotated[int, Field(description="收縮壓 SBP mmHg (111-219 normal)")],
        heart_rate: Annotated[int, Field(description="心率 HR bpm (51-90 normal)")],
        consciousness: Annotated[str, Field(description="AVPU意識: A=Alert, V=Voice, P=Pain, U=Unresponsive, C=Confusion", default="A")],
        use_scale_2: Annotated[bool, Field(description="使用Scale 2 (hypercapnic respiratory failure)", default=False)],
    ) -> dict[str, Any]:
        """
        計算 NEWS2 分數 (National Early Warning Score 2)
        
        Detect clinical deterioration. Score: 0-20.
        0-4=Routine, 5-6/single3=Urgent, ≥7=Emergency.
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
        eye_response: Annotated[int, Field(description="眼睛反應 1=None, 2=Pain, 3=Voice, 4=Spontaneous")],
        verbal_response: Annotated[int, Field(description="語言反應 1=None, 2=Sounds, 3=Words, 4=Confused, 5=Oriented")],
        motor_response: Annotated[int, Field(description="運動反應 1=None, 2=Extension, 3=Flexion, 4=Withdrawal, 5=Localizes, 6=Obeys")],
        is_intubated: Annotated[bool, Field(description="是否插管 (verbal not testable)", default=False)],
    ) -> dict[str, Any]:
        """
        計算 GCS 分數 (Glasgow Coma Scale)
        
        Assess consciousness. Score: 3-15 (or 3T-11T if intubated).
        13-15=Mild, 9-12=Moderate, 3-8=Severe.
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
        rass_score: Annotated[int, Field(description="當前RASS (-5到+4), CAM-ICU requires RASS≥-3")],
        acute_onset_fluctuation: Annotated[bool, Field(description="Feature1: 急性發作或波動病程")],
        inattention_score: Annotated[int, Field(description="Feature2: ASE注意力錯誤數 0-10 (≥3=positive)")],
        altered_loc: Annotated[bool, Field(description="Feature3: 意識改變 (RASS≠0)", default=False)],
        disorganized_thinking_errors: Annotated[int, Field(description="Feature4: 思維障礙錯誤數 0-5 (≥1=positive)", default=0)],
    ) -> dict[str, Any]:
        """
        計算 CAM-ICU (Confusion Assessment Method for ICU)
        
        Standard delirium screening for ICU. Requires RASS≥-3.
        Positive = Delirium if: F1+F2 AND (F3 OR F4).
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
