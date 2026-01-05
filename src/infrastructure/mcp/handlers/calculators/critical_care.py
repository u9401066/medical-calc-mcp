"""
Critical Care / ICU Calculator Tools

MCP tool handlers for critical care and ICU calculators.
Uses Annotated + Field to provide rich parameter descriptions in JSON Schema.
"""

from typing import Annotated, Any, Literal, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_critical_care_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all critical care/ICU calculator tools with MCP"""

    @mcp.tool()
    def calculate_apache_ii(
        temperature: Annotated[float, Field(ge=30.0, le=42.0, description="體溫 Temperature | Unit: °C | Range: 30.0-42.0")],
        mean_arterial_pressure: Annotated[float, Field(ge=20, le=200, description="平均動脈壓 MAP | Unit: mmHg | Range: 20-200")],
        heart_rate: Annotated[float, Field(ge=20, le=250, description="心率 Heart rate | Unit: bpm | Range: 20-250")],
        respiratory_rate: Annotated[float, Field(ge=4, le=60, description="呼吸速率 RR | Unit: breaths/min | Range: 4-60")],
        fio2: Annotated[float, Field(ge=0.21, le=1.0, description="吸入氧濃度 FiO2 | Range: 0.21-1.0")],
        arterial_ph: Annotated[float, Field(ge=6.8, le=8.0, description="動脈血 pH | Range: 6.8-8.0")] = 7.40,
        serum_sodium: Annotated[float, Field(ge=100, le=180, description="血鈉 Sodium | Unit: mEq/L | Range: 100-180")] = 140.0,
        serum_potassium: Annotated[float, Field(ge=1.0, le=10.0, description="血鉀 Potassium | Unit: mEq/L | Range: 1.0-10.0")] = 4.0,
        serum_creatinine: Annotated[float, Field(gt=0, le=20.0, description="血肌酐 Creatinine | Unit: mg/dL | Range: >0-20.0")] = 1.0,
        hematocrit: Annotated[float, Field(ge=10, le=70, description="血球容積比 Hematocrit | Unit: % | Range: 10-70")] = 40.0,
        wbc_count: Annotated[float, Field(ge=0.1, le=100, description="白血球 WBC | Unit: ×10³/µL | Range: 0.1-100")] = 10.0,
        gcs_score: Annotated[int, Field(ge=3, le=15, description="格拉斯哥昏迷指數 GCS | Range: 3-15")] = 15,
        age: Annotated[int, Field(ge=16, le=120, description="年齡 Age | Unit: years | Range: 16-120")] = 50,
        pao2: Annotated[Optional[float], Field(ge=20, le=700, description="動脈血氧分壓 PaO2 | Unit: mmHg (use if FiO2<0.5)")] = None,
        aado2: Annotated[Optional[float], Field(ge=0, le=700, description="肺泡動脈氧分壓差 A-a gradient | Unit: mmHg (if FiO2≥0.5)")] = None,
        chronic_conditions: Annotated[Optional[list[str]], Field(description="慢性健康問題 Chronic conditions list")] = None,
        admission_type: Annotated[
            Literal["nonoperative", "elective_postop", "emergency_postop"],
            Field(description="入院類型 | Options: 'nonoperative', 'elective_postop', 'emergency_postop'")
        ] = "nonoperative",
        acute_renal_failure: Annotated[bool, Field(description="急性腎衰竭 Acute renal failure present")] = False
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
        rass_score: Annotated[
            Literal[-5, -4, -3, -2, -1, 0, 1, 2, 3, 4],
            Field(description="RASS分數 | Options: +4=Combative, +3=Very agitated, +2=Agitated, +1=Restless, 0=Alert and calm, -1=Drowsy, -2=Light sedation, -3=Moderate sedation, -4=Deep sedation, -5=Unarousable")
        ]
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
        pao2_fio2_ratio: Annotated[float, Field(gt=0, le=700, description="PaO2/FiO2比值 | Unit: mmHg | Range: >0-700 (normal >400)")],
        platelets: Annotated[float, Field(gt=0, le=1000, description="血小板 Platelets | Unit: ×10³/µL | Range: >0-1000 (normal 150-400)")],
        bilirubin: Annotated[float, Field(ge=0, le=50, description="總膽紅素 Bilirubin | Unit: mg/dL | Range: 0-50 (normal <1.2)")],
        gcs_score: Annotated[int, Field(ge=3, le=15, description="格拉斯哥昏迷指數 GCS | Range: 3-15 (use lowest in 24h)")],
        creatinine: Annotated[float, Field(gt=0, le=20, description="血清肌酐 Creatinine | Unit: mg/dL | Range: >0-20 (normal 0.7-1.3)")],
        map_value: Annotated[Optional[float], Field(ge=0, le=200, description="平均動脈壓 MAP | Unit: mmHg (if no vasopressors)")] = None,
        dopamine_dose: Annotated[Optional[float], Field(ge=0, le=50, description="Dopamine劑量 | Unit: µg/kg/min")] = None,
        dobutamine_any: Annotated[bool, Field(description="是否使用Dobutamine (any dose)")] = False,
        epinephrine_dose: Annotated[Optional[float], Field(ge=0, le=2, description="Epinephrine劑量 | Unit: µg/kg/min")] = None,
        norepinephrine_dose: Annotated[Optional[float], Field(ge=0, le=2, description="Norepinephrine劑量 | Unit: µg/kg/min")] = None,
        is_mechanically_ventilated: Annotated[bool, Field(description="是否機械通氣 (affects respiratory scoring)")] = False,
        urine_output_24h: Annotated[Optional[float], Field(ge=0, le=10000, description="24h尿量 | Unit: mL (for renal scoring)")] = None,
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
    def calculate_sofa2(
        gcs_score: Annotated[int, Field(ge=3, le=15, description="格拉斯哥昏迷指數 GCS | Range: 3-15")],
        pao2_fio2_ratio: Annotated[float, Field(gt=0, le=700, description="PaO2/FiO2比值 | Unit: mmHg | Range: >0-700 (SOFA-2 thresholds: 300, 225, 150, 75)")],
        bilirubin: Annotated[float, Field(ge=0, le=50, description="總膽紅素 Bilirubin | Unit: mg/dL | Range: 0-50 (SOFA-2 thresholds: 1.2, 3, 6, 12)")],
        creatinine: Annotated[float, Field(gt=0, le=20, description="血清肌酐 Creatinine | Unit: mg/dL | Range: >0-20 (SOFA-2 thresholds: 1.2, 2.0, 3.5)")],
        platelets: Annotated[float, Field(gt=0, le=1000, description="血小板 Platelets | Unit: ×10³/µL | Range: >0-1000 (SOFA-2 thresholds: 150, 100, 80, 50)")],
        map_value: Annotated[Optional[float], Field(ge=0, le=200, description="平均動脈壓 MAP | Unit: mmHg (if no vasopressors, threshold <70)")] = None,
        norepinephrine_epinephrine_dose: Annotated[Optional[float], Field(ge=0, le=5, description="NE+Epi合併劑量 | Unit: µg/kg/min (thresholds: ≤0.2=low, >0.2-0.4=medium, >0.4=high)")] = None,
        receiving_sedation_or_delirium_drugs: Annotated[bool, Field(description="是否接受鎮靜/譫妄藥物 (GCS 15 with sedation = score 1)")] = False,
        advanced_ventilatory_support: Annotated[bool, Field(description="進階呼吸支持 High FiO2 (>0.6), High PEEP, or proning")] = False,
        on_ecmo: Annotated[bool, Field(description="是否使用ECMO (automatically scores 4 for respiratory)")] = False,
        urine_output_6h: Annotated[Optional[float], Field(ge=0, le=10, description="6小時尿量 | Unit: mL/kg/h (< 0.5 for 6-12h = score 1)")] = None,
        urine_output_12h: Annotated[Optional[float], Field(ge=0, le=10, description="12小時尿量 | Unit: mL/kg/h (< 0.5 for ≥12h = score 2)")] = None,
        urine_output_24h: Annotated[Optional[float], Field(ge=0, le=10, description="24小時尿量 | Unit: mL/kg/h (< 0.3 for ≥24h = score 3)")] = None,
        on_rrt: Annotated[bool, Field(description="是否接受RRT (腎臟替代治療, automatically scores 4 for kidney)")] = False,
    ) -> dict[str, Any]:
        """
        計算 SOFA-2 分數 (2025 JAMA 更新版)

        SOFA-2 is the updated 2025 version validated on 3.34 million ICU patients.
        Key updates: New P/F thresholds (300,225,150,75), updated platelet thresholds (150,100,80,50),
        combined NE+Epi dosing, ECMO and RRT criteria.
        Score range: 0-24. AUROC 0.79 for ICU mortality.

        Reference: Ranzani OT, et al. JAMA. 2025. doi:10.1001/jama.2025.20516
        """
        request = CalculateRequest(
            tool_id="sofa2_score",
            params={
                "gcs_score": gcs_score,
                "pao2_fio2_ratio": pao2_fio2_ratio,
                "bilirubin": bilirubin,
                "creatinine": creatinine,
                "platelets": platelets,
                "map_value": map_value,
                "norepinephrine_epinephrine_dose": norepinephrine_epinephrine_dose,
                "receiving_sedation_or_delirium_drugs": receiving_sedation_or_delirium_drugs,
                "advanced_ventilatory_support": advanced_ventilatory_support,
                "on_ecmo": on_ecmo,
                "urine_output_6h": urine_output_6h,
                "urine_output_12h": urine_output_12h,
                "urine_output_24h": urine_output_24h,
                "on_rrt": on_rrt,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_qsofa(
        respiratory_rate: Annotated[int, Field(ge=4, le=60, description="呼吸速率 RR | Unit: breaths/min | Range: 4-60 (≥22 scores 1)")],
        systolic_bp: Annotated[int, Field(ge=30, le=250, description="收縮壓 SBP | Unit: mmHg | Range: 30-250 (≤100 scores 1)")],
        altered_mentation: Annotated[bool, Field(description="意識改變 GCS<15 or acute change (scores 1)")] = False,
        gcs_score: Annotated[int, Field(ge=3, le=15, description="GCS分數 | Range: 3-15 (alternative to altered_mentation)")] = 15,
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
        respiratory_rate: Annotated[int, Field(ge=4, le=60, description="呼吸速率 RR | Unit: breaths/min | Range: 4-60 (normal 8-25)")],
        spo2: Annotated[int, Field(ge=50, le=100, description="血氧飽和度 SpO2 | Unit: % | Range: 50-100 (normal 94-100 on room air)")],
        on_supplemental_o2: Annotated[bool, Field(description="是否使用氧氣 On supplemental O2 (scores 2 if on O2)")],
        temperature: Annotated[float, Field(ge=30.0, le=42.0, description="體溫 Temperature | Unit: °C | Range: 30.0-42.0 (normal 36.1-38.0)")],
        systolic_bp: Annotated[int, Field(ge=40, le=250, description="收縮壓 SBP | Unit: mmHg | Range: 40-250 (normal 111-219)")],
        heart_rate: Annotated[int, Field(ge=20, le=220, description="心率 HR | Unit: bpm | Range: 20-220 (normal 51-90)")],
        consciousness: Annotated[
            Literal["A", "V", "P", "U", "C"],
            Field(description="AVPU意識 | Options: 'A'=Alert, 'V'=Voice, 'P'=Pain, 'U'=Unresponsive, 'C'=Confusion")
        ] = "A",
        use_scale_2: Annotated[bool, Field(description="使用Scale 2 (for hypercapnic respiratory failure patients)")] = False,
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
        eye_response: Annotated[
            Literal[1, 2, 3, 4],
            Field(description="眼睛反應 Eye Response | Options: 1=None, 2=To pain, 3=To voice, 4=Spontaneous")
        ],
        verbal_response: Annotated[
            Literal[1, 2, 3, 4, 5],
            Field(description="語言反應 Verbal Response | Options: 1=None, 2=Sounds, 3=Words, 4=Confused, 5=Oriented")
        ],
        motor_response: Annotated[
            Literal[1, 2, 3, 4, 5, 6],
            Field(description="運動反應 Motor Response | Options: 1=None, 2=Extension, 3=Flexion, 4=Withdrawal, 5=Localizes, 6=Obeys")
        ],
        is_intubated: Annotated[bool, Field(description="是否插管 Intubated (verbal not testable)")] = False,
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
        rass_score: Annotated[
            Literal[-5, -4, -3, -2, -1, 0, 1, 2, 3, 4],
            Field(description="當前RASS | Range: -5 to +4 (CAM-ICU requires RASS≥-3)")
        ],
        acute_onset_fluctuation: Annotated[bool, Field(description="Feature 1: 急性發作或波動病程 Acute onset or fluctuating course")],
        inattention_score: Annotated[int, Field(ge=0, le=10, description="Feature 2: ASE注意力錯誤數 | Range: 0-10 (≥3 = positive)")],
        altered_loc: Annotated[bool, Field(description="Feature 3: 意識改變 Altered level of consciousness (RASS≠0)")] = False,
        disorganized_thinking_errors: Annotated[int, Field(ge=0, le=5, description="Feature 4: 思維障礙錯誤數 | Range: 0-5 (≥1 = positive)")] = 0,
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
