"""
Pediatric Scores MCP Handlers - 兒科評分工具

Handlers for pediatric assessment calculators:
- APGAR Score (Newborn assessment)
- PEWS (Pediatric Early Warning Score)
- pSOFA (Pediatric SOFA)
- PIM3 (Pediatric Index of Mortality 3)
- Pediatric GCS (Age-adapted Glasgow Coma Scale)
"""

from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_pediatric_score_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register pediatric score calculator tools with MCP server."""

    # ========================================
    # APGAR Score
    # ========================================
    @mcp.tool()
    def calculate_apgar_score(appearance: int, pulse: int, grimace: int, activity: int, respiration: int, assessment_time: str = "1_minute") -> dict[str, Any]:
        """
        👶 APGAR Score: 新生兒評估量表

        在出生後 1 分鐘和 5 分鐘評估新生兒狀況，預測復甦需求。

        **APGAR 五項評估 (各 0-2 分):**
        - **A**ppearance (膚色): 0=全身發紺, 1=軀幹粉紅四肢發紺, 2=全身粉紅
        - **P**ulse (心率): 0=無, 1=<100 bpm, 2=≥100 bpm
        - **G**rimace (反射): 0=無反應, 1=皺眉/弱哭, 2=咳嗽/打噴嚏/大哭
        - **A**ctivity (肌張力): 0=鬆軟, 1=部分屈曲, 2=活動良好
        - **R**espiration (呼吸): 0=無, 1=慢/不規則, 2=良好/大哭

        **分數解讀:**
        - 7-10: 正常 (常規照護)
        - 4-6: 中度抑制 (可能需要介入)
        - 0-3: 嚴重抑制 (需要立即復甦)

        **參考文獻:** Apgar 1953, AAP/ACOG 2015. PMID: 26416932

        Args:
            appearance: 膚色評分 (0-2)
            pulse: 心率評分 (0-2)
            grimace: 反射評分 (0-2)
            activity: 肌張力評分 (0-2)
            respiration: 呼吸評分 (0-2)
            assessment_time: 評估時間 "1_minute", "5_minute", "10_minute"

        Returns:
            APGAR 分數 (0-10) 及臨床建議
        """
        params = {
            "appearance": appearance,
            "pulse": pulse,
            "grimace": grimace,
            "activity": activity,
            "respiration": respiration,
            "assessment_time": assessment_time,
        }
        return use_case.execute(CalculateRequest(tool_id="apgar_score", params=params)).to_dict()

    # ========================================
    # PEWS (Pediatric Early Warning Score)
    # ========================================
    @mcp.tool()
    def calculate_pews(
        behavior_score: int,
        cardiovascular_score: int,
        respiratory_score: int,
        age_group: Optional[str] = None,
        heart_rate: Optional[int] = None,
        respiratory_rate: Optional[int] = None,
        spo2: Optional[float] = None,
        supplemental_oxygen: bool = False,
    ) -> dict[str, Any]:
        """
        🚨 PEWS: 兒童早期預警評分 (Pediatric Early Warning Score)

        識別住院兒童臨床惡化風險，指導升級照護決策。

        **三大評估面向 (各 0-3 分):**
        - **行為/神經**: 0=玩耍正常, 1=睡眠, 2=煩躁/混亂, 3=對痛反應減弱
        - **心血管**: 0=粉紅/CRT≤2s, 1=蒼白/CRT 3s, 2=灰色/CRT 4s/心搏過速, 3=發紺/CRT≥5s
        - **呼吸**: 0=正常, 1=輕度費力, 2=中度費力/SpO2 90-94%, 3=嚴重費力/SpO2<90%

        **附加分數:** 使用氧氣 +2 分

        **風險分層:**
        - 0-2: 低風險 (常規監測 q4h)
        - 3-4: 中等風險 (增加監測 q2h)
        - ≥5: 高風險 (立即醫師評估)
        - ≥7: 危急 (啟動快速反應團隊/考慮 PICU)

        **參考文獻:** Parshuram 2009, NICE NG51. PMID: 19678924

        Args:
            behavior_score: 行為/神經評分 (0-3)
            cardiovascular_score: 心血管評分 (0-3)
            respiratory_score: 呼吸評分 (0-3)
            age_group: 年齡組 "0-3m", "3-12m", "1-4y", "4-12y", "12-18y"
            heart_rate: 實際心率 (bpm)
            respiratory_rate: 實際呼吸速率
            spo2: 血氧飽和度 (%)
            supplemental_oxygen: 是否使用氧氣

        Returns:
            PEWS 分數及升級照護建議
        """
        params = {
            "behavior_score": behavior_score,
            "cardiovascular_score": cardiovascular_score,
            "respiratory_score": respiratory_score,
            "age_group": age_group,
            "heart_rate": heart_rate,
            "respiratory_rate": respiratory_rate,
            "spo2": spo2,
            "supplemental_oxygen": supplemental_oxygen,
        }
        return use_case.execute(CalculateRequest(tool_id="pews", params=params)).to_dict()

    # ========================================
    # Pediatric SOFA (pSOFA)
    # ========================================
    @mcp.tool()
    def calculate_pediatric_sofa(
        age_group: str,
        pao2_fio2_ratio: float,
        platelets: float,
        bilirubin: float,
        gcs_score: int,
        creatinine: float,
        map_value: Optional[float] = None,
        vasopressor_type: Optional[str] = None,
        vasopressor_dose: Optional[float] = None,
        on_mechanical_ventilation: bool = False,
    ) -> dict[str, Any]:
        """
        🏥 pSOFA: 兒童器官衰竭評估 (Pediatric SOFA)

        適應年齡的 SOFA 評分，用於兒童敗血症及器官功能障礙評估。
        基於 Sepsis-3 標準適應兒童，經 2017 JAMA Pediatrics 驗證。

        **六大器官系統 (各 0-4 分，總分 0-24):**
        1. 呼吸 (PaO2/FiO2)
        2. 凝血 (血小板)
        3. 肝臟 (膽紅素)
        4. 心血管 (MAP/升壓藥，年齡調整)
        5. 神經 (GCS，年齡調整)
        6. 腎臟 (肌酐，年齡調整)

        **年齡組別:**
        "0-1m", "1-12m", "1-2y", "2-5y", "5-12y", "12-18y"

        **敗血症標準:** ≥2 分增加提示敗血症相關器官功能障礙

        **參考文獻:** Matics 2017, Phoenix Criteria 2024. PMID: 28783810

        Args:
            age_group: 年齡組別
            pao2_fio2_ratio: PaO2/FiO2 比值 (mmHg)
            platelets: 血小板 (×10³/µL)
            bilirubin: 總膽紅素 (mg/dL)
            gcs_score: GCS 分數 (3-15)
            creatinine: 血清肌酐 (mg/dL)
            map_value: 平均動脈壓 (mmHg)
            vasopressor_type: 升壓藥類型
            vasopressor_dose: 升壓藥劑量 (mcg/kg/min)
            on_mechanical_ventilation: 是否使用機械通氣

        Returns:
            pSOFA 分數及器官特異性評估
        """
        params = {
            "age_group": age_group,
            "pao2_fio2_ratio": pao2_fio2_ratio,
            "platelets": platelets,
            "bilirubin": bilirubin,
            "gcs_score": gcs_score,
            "creatinine": creatinine,
            "map_value": map_value,
            "vasopressor_type": vasopressor_type,
            "vasopressor_dose": vasopressor_dose,
            "on_mechanical_ventilation": on_mechanical_ventilation,
        }
        return use_case.execute(CalculateRequest(tool_id="pediatric_sofa", params=params)).to_dict()

    # ========================================
    # PIM3 (Pediatric Index of Mortality 3)
    # ========================================
    @mcp.tool()
    def calculate_pim3(
        systolic_bp: float,
        pupillary_reaction: str,
        mechanical_ventilation: bool,
        base_excess: float,
        elective_admission: bool = False,
        recovery_post_procedure: bool = False,
        cardiac_bypass: bool = False,
        high_risk_diagnosis: bool = False,
        low_risk_diagnosis: bool = False,
        very_high_risk_diagnosis: bool = False,
    ) -> dict[str, Any]:
        """
        📊 PIM3: 兒童死亡指數第三版 (Pediatric Index of Mortality 3)

        預測 PICU 死亡率，用於品質基準比較而非個別病人預後溝通。
        使用入 ICU 時首次接觸資料計算。

        **10 項變數:**
        1. 收縮壓 (心跳停止=0, 過低無法測量=30, 未測量=120)
        2. 瞳孔反應 (both_react, one_fixed, both_fixed)
        3. 第一小時機械通氣
        4. 鹼基過剩絕對值 (未測量=0)
        5. 擇期入院
        6. 術後恢復入院
        7. 心臟繞道手術
        8. 高風險診斷 (腦出血、心肌病、HLHS等)
        9. 低風險診斷 (氣喘、細支氣管炎、DKA等)
        10. 極高風險診斷 (心跳停止、SCID、白血病首次誘導等)

        **用途:** PICU 品質基準，計算 SMR = 觀察死亡/預期死亡

        **參考文獻:** Straney 2013. PMID: 23863821

        Args:
            systolic_bp: 收縮壓 (mmHg)
            pupillary_reaction: 瞳孔反應
            mechanical_ventilation: 第一小時機械通氣
            base_excess: 鹼基過剩 (mEq/L)
            elective_admission: 擇期入院
            recovery_post_procedure: 術後恢復入院
            cardiac_bypass: 心臟繞道手術
            high_risk_diagnosis: 高風險診斷
            low_risk_diagnosis: 低風險診斷
            very_high_risk_diagnosis: 極高風險診斷

        Returns:
            預測死亡率百分比及風險類別
        """
        params = {
            "systolic_bp": systolic_bp,
            "pupillary_reaction": pupillary_reaction,
            "mechanical_ventilation": mechanical_ventilation,
            "base_excess": base_excess,
            "elective_admission": elective_admission,
            "recovery_post_procedure": recovery_post_procedure,
            "cardiac_bypass": cardiac_bypass,
            "high_risk_diagnosis": high_risk_diagnosis,
            "low_risk_diagnosis": low_risk_diagnosis,
            "very_high_risk_diagnosis": very_high_risk_diagnosis,
        }
        return use_case.execute(CalculateRequest(tool_id="pim3", params=params)).to_dict()

    # ========================================
    # Pediatric GCS
    # ========================================
    @mcp.tool()
    def calculate_pediatric_gcs(
        eye_response: int, verbal_response: int, motor_response: int, age_group: str = "child", intubated: bool = False
    ) -> dict[str, Any]:
        """
        🧠 Pediatric GCS: 兒童格拉斯哥昏迷指數

        適應年齡的 GCS，用於無法遵循口頭指令的嬰幼兒意識評估。

        **眼睛反應 (E, 1-4):**
        4=自發睜眼, 3=對聲音/呼喚睜眼, 2=對痛睜眼, 1=無

        **語言反應 (V, 1-5):**
        嬰兒 (<1歲): 5=咕咕叫/咿呀學語, 4=煩躁哭泣但可安撫, 3=對痛哭泣, 2=呻吟, 1=無
        兒童 (≥1歲): 5=正常對答, 4=混亂, 3=不恰當詞彙, 2=無法理解的聲音, 1=無

        **運動反應 (M, 1-6):**
        6=遵從指令/正常動作, 5=定位痛/觸摸縮回, 4=退縮, 3=異常屈曲, 2=伸展, 1=無

        **解讀:**
        - 13-15: 輕度 (觀察)
        - 9-12: 中度 (密切監測)
        - 3-8: 嚴重 (考慮氣道保護)

        **參考文獻:** Reilly 1988, Holmes 2005. PMID: 16141014

        Args:
            eye_response: 眼睛反應 (1-4)
            verbal_response: 語言反應 (1-5)
            motor_response: 運動反應 (1-6)
            age_group: "infant" (<1歲) 或 "child" (≥1歲)
            intubated: 是否插管

        Returns:
            Pediatric GCS 分數及臨床建議
        """
        params = {
            "eye_response": eye_response,
            "verbal_response": verbal_response,
            "motor_response": motor_response,
            "age_group": age_group,
            "intubated": intubated,
        }
        return use_case.execute(CalculateRequest(tool_id="pediatric_gcs", params=params)).to_dict()
