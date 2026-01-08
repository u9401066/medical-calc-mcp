"""
Calculator Handler

MCP tool handlers for calculator operations.

v3.0 CONSOLIDATED DESIGN (保持 High-Level / Low-Level 分層):
============================================================

LOW-LEVEL TOOLS (計算執行層) - 3 個:
├── get_tool_schema()    - 取得工具詳情 + 參數 Schema + 來源提示
├── calculate()          - 單一工具計算
└── calculate_batch()    - 批次計算多工具

這些工具執行實際計算:
1. get_tool_schema: 提供完整的參數資訊和來源提示 (整併自 get_calculator_info + get_calculation_schema)
2. calculate: 執行單一計算
3. calculate_batch: 批次執行多個計算，含跨工具分析

整併說明:
- get_calculator_info() + get_calculation_schema() → get_tool_schema()
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from ....application.dto import CalculateRequest, DiscoveryMode, DiscoveryRequest
from ....application.use_cases import CalculateUseCase, DiscoveryUseCase
from ....domain.registry.tool_registry import ToolRegistry
from ....infrastructure.logging import get_logger

# ============================================================================
# OLD DESIGN: 75 個獨立工具 (已註解以節省 token)
# ============================================================================
# from .calculators import (
#     register_acid_base_tools,
#     register_anesthesiology_tools,
#     register_cardiology_tools,
#     register_critical_care_tools,
#     register_emergency_tools,
#     register_general_tools,
#     register_gi_bleeding_tools,
#     register_hematology_tools,
#     register_hepatology_tools,
#     register_infectious_disease_tools,
#     register_nephrology_tools,
#     register_neurology_tools,
#     register_obstetrics_tools,
#     register_pediatric_score_tools,
#     register_pediatric_tools,
#     register_pulmonology_tools,
#     register_surgery_tools,
#     register_trauma_tools,
# )


class CalculatorHandler:
    """
    Handler for calculator-related MCP tools.

    v3.0: Consolidated Low-Level Tools
    ==================================
    - get_tool_schema(tool_id) - 工具詳情 + 參數 Schema + 來源提示
    - calculate(tool_id, params) - 單一計算
    - calculate_batch(calculations) - 批次計算

    整併自:
    - get_calculator_info() + get_calculation_schema() → get_tool_schema()
    """

    def __init__(self, mcp: FastMCP, registry: ToolRegistry):
        self._mcp = mcp
        self._registry = registry
        self._use_case = CalculateUseCase(registry)
        self._discovery_use_case = DiscoveryUseCase(registry)
        self._logger = get_logger()

        # Register the unified calculate tool
        self._register_tools()

    def _register_tools(self) -> None:
        """Register the unified calculate tool with MCP"""

        @self._mcp.tool()
        def calculate(tool_id: str, params: dict[str, Any]) -> dict[str, Any]:
            """
            🧮 通用醫學計算工具

            使用指定的計算器執行計算。支援所有 75+ 種醫學計算器。

            **使用流程:**
            1. 先用 search_calculators("關鍵字") 或 list_by_specialty("專科") 找工具
            2. 用 get_calculator_info(tool_id) 查看需要的參數
            3. 呼叫 calculate(tool_id, params) 執行計算

            Args:
                tool_id: 計算器 ID (例如: "sofa", "apache_ii", "ckd_epi_2021")
                params: 計算參數字典 (從 get_calculator_info 取得參數名稱)

            Returns:
                計算結果，包含:
                - success: 是否成功
                - score_name: 評分名稱
                - result: 計算結果 (分數或數值)
                - unit: 單位
                - interpretation: 臨床解讀
                - references: 參考文獻

            **Examples:**

            Example 1 - SOFA Score:
            ```
            calculate("sofa_score", {
                "pao2_fio2_ratio": 300,
                "is_mechanically_ventilated": False,
                "platelets": 150,
                "bilirubin": 1.2,
                "map_value": 70,
                "gcs_score": 15,
                "creatinine": 1.0,
                "urine_output_24h": 1500
            })
            ```

            Example 2 - CKD-EPI 2021:
            ```
            calculate("ckd_epi_2021", {
                "serum_creatinine": 1.2,
                "age": 65,
                "sex": "male"
            })
            ```

            Example 3 - RCRI (Revised Cardiac Risk Index):
            ```
            calculate("rcri", {
                "high_risk_surgery": True,
                "ischemic_heart_disease": False,
                "heart_failure": False,
                "cerebrovascular_disease": False,
                "insulin_therapy": True,
                "creatinine_above_2": False
            })
            ```

            **常用計算器:**
            - Critical Care: sofa_score, apache_ii, news2_score, qsofa_score, glasgow_coma_scale
            - Cardiology: chads2_vasc, heart_score, rcri
            - Nephrology: ckd_epi_2021, kdigo_aki
            - Anesthesiology: asa_physical_status, mallampati_score, stop_bang
            - Hepatology: meld_score, child_pugh

            ⏮️ 上一步: get_calculator_info(tool_id) 查看完整參數說明
            """
            # Create request and execute
            request = CalculateRequest(tool_id=tool_id, params=params)
            response = self._use_case.execute(request)

            # Convert to dict for MCP response
            result = {
                "success": response.success,
                "tool_id": response.tool_id,
                "score_name": response.score_name,
                "result": response.result,
                "unit": response.unit,
            }

            if response.error:
                result["error"] = response.error
                result["hint"] = f"使用 get_calculator_info('{tool_id}') 查看正確的參數格式"

            if response.interpretation:
                result["interpretation"] = {
                    "summary": response.interpretation.summary,
                    "severity": response.interpretation.severity,
                    "recommendation": response.interpretation.recommendation,
                }
                if response.interpretation.details:
                    result["interpretation"]["details"] = response.interpretation.details

            if response.component_scores:
                result["component_scores"] = response.component_scores

            if response.references:
                result["references"] = [
                    {
                        "citation": ref.citation,
                        "pmid": ref.pmid,
                        "doi": ref.doi,
                    }
                    for ref in response.references
                ]

            return result

        # ====================================================================
        # NEW: Batch Calculation (v2.1)
        # ====================================================================

        @self._mcp.tool()
        def calculate_batch(calculations: list[dict[str, Any]]) -> dict[str, Any]:
            """
            🧮 批次計算多個工具 - 減少 round-trip，提高效率

            一次執行多個計算，並提供結果間的事實關係分析。
            適合需要同時評估多個指標的臨床情境。

            Args:
                calculations: 計算請求列表，每個元素包含:
                    - tool_id: 計算器 ID
                    - params: 參數字典

            Returns:
                - results: 各計算的結果
                - summary: 結果摘要
                - cross_analysis: 結果間的事實關係 (非臨床推理)
                - all_success: 是否全部成功

            **Example - Sepsis 評估:**
            ```
            calculate_batch([
                {"tool_id": "qsofa_score", "params": {
                    "respiratory_rate": 24,
                    "systolic_bp": 95,
                    "altered_mentation": True
                }},
                {"tool_id": "sofa_score", "params": {
                    "pao2_fio2_ratio": 200,
                    "platelets": 80,
                    "bilirubin": 2.5,
                    "gcs_score": 13,
                    "creatinine": 2.0
                }}
            ])
            ```

            **Cross-analysis 提供的事實判斷 (非推理):**
            - "qSOFA ≥ 2 且 SOFA ≥ 2: 符合 Sepsis-3 定義標準"
            - "RCRI ≥ 2: 符合高心臟風險標準"

            💡 這不是臨床建議，只是根據指引標準的事實陳述
            """
            results: list[dict[str, Any]] = []
            tool_ids: list[str] = []
            scores: dict[str, Any] = {}

            for calc in calculations:
                tool_id = calc.get("tool_id", "")
                params = calc.get("params", {})
                tool_ids.append(tool_id)

                # Execute calculation
                request = CalculateRequest(tool_id=tool_id, params=params)
                response = self._use_case.execute(request)

                result = {
                    "tool_id": tool_id,
                    "success": response.success,
                    "score_name": response.score_name,
                    "result": response.result,
                    "unit": response.unit,
                }

                if response.error:
                    result["error"] = response.error

                if response.interpretation:
                    result["interpretation"] = response.interpretation.summary

                results.append(result)

                # Store for cross-analysis
                if response.success and response.result is not None:
                    scores[tool_id] = response.result

            # Generate cross-analysis (fact-based, not clinical reasoning)
            cross_analysis = _generate_cross_analysis(scores)

            return {
                "all_success": all(r["success"] for r in results),
                "count": len(results),
                "results": results,
                "summary": {
                    "tools_executed": tool_ids,
                    "successful": sum(1 for r in results if r["success"]),
                    "failed": sum(1 for r in results if not r["success"]),
                },
                "cross_analysis": cross_analysis,
                "note": "cross_analysis 是事實陳述，非臨床建議。Agent 應根據臨床情境做判斷。",
            }

        # ====================================================================
        # LOW-LEVEL TOOL 3: Get Tool Schema (整併自 get_calculator_info + get_calculation_schema)
        # ====================================================================

        @self._mcp.tool()
        def get_tool_schema(tool_id: str, include_references: bool = True, include_param_sources: bool = True) -> dict[str, Any]:
            """
            📋 取得工具完整資訊 + 參數 Schema + 來源提示 (Low-Level)

            整併了原本的 get_calculator_info 和 get_calculation_schema，
            提供 Agent 執行計算所需的所有資訊:

            1. **工具基本資訊**: 名稱、用途、專科、情境
            2. **參數 Schema**: 每個參數的類型、單位、正常範圍
            3. **來源提示**: 參數通常從哪裡取得 (Parameter Provenance)
            4. **參考文獻**: PMID/DOI (100% 覆蓋率，Vancouver style)

            Args:
                tool_id: 計算器 ID (從 discover() 取得)
                include_references: 是否包含參考文獻 (預設 True)
                    - True: 包含完整參考文獻 (citation, PMID, DOI)
                    - False: 省略以節省 tokens
                include_param_sources: 是否包含參數來源提示 (預設 True)
                    - True: 包含 clinical_hint, common_sources, normal_range
                    - False: 只返回基本 type/unit

            Returns:
                完整的工具資訊，包含:
                - tool_id, name, purpose
                - specialties, contexts (High-Level 分類)
                - required_params (必要參數列表)
                - param_schemas (每個參數的詳細 Schema)
                - references (參考文獻，若 include_references=True)

            **Example:**
            ```python
            # 完整資訊 (預設)
            get_tool_schema("ckd_epi_2021")

            # 只要基本資訊 (節省 tokens)
            get_tool_schema("ckd_epi_2021", include_references=False, include_param_sources=False)
            ```

            ⏭️ 下一步: calculate(tool_id, params) 執行計算
            """
            calculator = self._registry.get_calculator(tool_id)
            if not calculator:
                return {"success": False, "error": f"找不到工具: {tool_id}", "hint": "使用 discover(by='keyword', value='關鍵字') 搜尋工具"}

            metadata = calculator.metadata
            low_level = metadata.low_level
            high_level = metadata.high_level

            # Build parameter schemas with source mapping
            if include_param_sources:
                param_schemas = _build_param_schemas(calculator)
            else:
                # Minimal schema (just type info)
                param_schemas = {param: {"type": "number", "required": True} for param in low_level.input_params}

            result: dict[str, Any] = {
                "success": True,
                "tool_id": tool_id,
                "name": low_level.name,
                "purpose": low_level.purpose,
                # High-Level 分類資訊
                "clinical_context": {
                    "specialties": [s.value for s in high_level.specialties],
                    "contexts": [c.value for c in high_level.clinical_contexts],
                    "conditions": list(high_level.conditions) if high_level.conditions else [],
                },
                # Low-Level 參數資訊
                "required_params": list(low_level.input_params),
                "param_schemas": param_schemas,
                "output": {
                    "type": low_level.output_type,
                },
                # 導航
                "next_step": f"calculate('{tool_id}', {{...params}})",
            }

            # 參考文獻 (可選)
            if include_references:
                request = DiscoveryRequest(mode=DiscoveryMode.GET_INFO, tool_id=tool_id)
                discovery_response = self._discovery_use_case.execute(request)
                if discovery_response.tool_detail and discovery_response.tool_detail.references:
                    result["references"] = discovery_response.tool_detail.references

            return result

        # ====================================================================
        # OLD DESIGN: 75 個獨立工具 (已註解以節省 token)
        # ====================================================================
        # 如需恢復舊設計，取消以下註解:
        #
        # # Nephrology calculators
        # register_nephrology_tools(self._mcp, self._use_case)
        #
        # # Anesthesiology / Preoperative calculators
        # register_anesthesiology_tools(self._mcp, self._use_case)
        #
        # # Critical Care / ICU calculators
        # register_critical_care_tools(self._mcp, self._use_case)
        #
        # # Pediatric & Transfusion calculators
        # register_pediatric_tools(self._mcp, self._use_case)
        #
        # # Pulmonology / Respiratory calculators
        # register_pulmonology_tools(self._mcp, self._use_case)
        #
        # # Cardiology calculators
        # register_cardiology_tools(self._mcp, self._use_case)
        #
        # # Emergency Medicine calculators
        # register_emergency_tools(self._mcp, self._use_case)
        #
        # # Hepatology / GI calculators
        # register_hepatology_tools(self._mcp, self._use_case)
        #
        # # Surgery / Perioperative calculators
        # register_surgery_tools(self._mcp, self._use_case)
        #
        # # Acid-Base / Metabolic calculators
        # register_acid_base_tools(self._mcp, self._use_case)
        #
        # # Hematology calculators
        # register_hematology_tools(self._mcp, self._use_case)
        #
        # # Neurology calculators
        # register_neurology_tools(self._mcp, self._use_case)
        #
        # # General calculators (BSA, Cockcroft-Gault, Corrected Ca, Parkland)
        # register_general_tools(self._mcp, self._use_case)
        #
        # # Pediatric Score calculators (APGAR, PEWS, pSOFA, PIM3, Pediatric GCS)
        # register_pediatric_score_tools(self._mcp, self._use_case)
        #
        # # Infectious Disease calculators (MASCC, Pitt Bacteremia, Centor, CPIS)
        # register_infectious_disease_tools(self._mcp, self._use_case)
        #
        # # Obstetrics calculators (Bishop Score, Ballard Score)
        # register_obstetrics_tools(self._mcp, self._use_case)
        #
        # # GI Bleeding calculators (Glasgow-Blatchford, AIMS65)
        # register_gi_bleeding_tools(self._mcp, self._use_case)
        #
        # # Trauma calculators (TBSA, ISS, sPESI)
        # register_trauma_tools(self._mcp, self._use_case)


# =============================================================================
# Helper Functions for Batch Calculation and Schema
# =============================================================================


def _generate_cross_analysis(scores: dict[str, Any]) -> list[dict[str, str]]:
    """
    Generate fact-based cross-analysis of multiple scores.

    This is NOT clinical reasoning - just factual statements based on
    established criteria from clinical guidelines.

    Args:
        scores: Dictionary of tool_id -> score value

    Returns:
        List of factual observations
    """
    analysis: list[dict[str, str]] = []

    # Sepsis-3 criteria
    qsofa = scores.get("qsofa_score")
    sofa = scores.get("sofa_score")
    if qsofa is not None and sofa is not None:
        if qsofa >= 2 and sofa >= 2:
            analysis.append(
                {
                    "observation": "qSOFA ≥ 2 且 SOFA ≥ 2",
                    "criteria": "Sepsis-3",
                    "fact": "符合 Sepsis-3 定義標準 (疑似感染 + 器官功能障礙)",
                    "reference": "Singer M, et al. JAMA 2016",
                }
            )
        elif qsofa >= 2:
            analysis.append(
                {"observation": "qSOFA ≥ 2", "criteria": "Sepsis-3", "fact": "qSOFA 陽性，建議進一步評估 SOFA", "reference": "Singer M, et al. JAMA 2016"}
            )

    # RCRI cardiac risk
    rcri = scores.get("rcri")
    if rcri is not None:
        if rcri >= 3:
            analysis.append(
                {
                    "observation": f"RCRI = {rcri}",
                    "criteria": "Lee Index",
                    "fact": "RCRI Class IV: 高心臟風險 (>11% MACE)",
                    "reference": "Lee TH, et al. Circulation 1999",
                }
            )
        elif rcri >= 2:
            analysis.append(
                {
                    "observation": f"RCRI = {rcri}",
                    "criteria": "Lee Index",
                    "fact": "RCRI Class III: 中等心臟風險 (6.6% MACE)",
                    "reference": "Lee TH, et al. Circulation 1999",
                }
            )

    # CHA2DS2-VASc for AF stroke risk
    chads = scores.get("chads2_vasc")
    if chads is not None:
        if chads >= 2:
            analysis.append(
                {
                    "observation": f"CHA₂DS₂-VASc = {chads}",
                    "criteria": "ESC AF Guidelines",
                    "fact": "分數 ≥ 2: 根據 ESC 指引，建議考慮抗凝治療",
                    "reference": "Lip GY, et al. Chest 2010",
                }
            )

    # GCS severity
    gcs = scores.get("glasgow_coma_scale")
    if gcs is not None:
        if gcs <= 8:
            analysis.append(
                {"observation": f"GCS = {gcs}", "criteria": "Teasdale-Jennett", "fact": "GCS ≤ 8: 符合重度意識障礙標準", "reference": "Teasdale G, Lancet 1974"}
            )

    # eGFR staging
    egfr = scores.get("ckd_epi_2021")
    if egfr is not None:
        if egfr < 15:
            analysis.append(
                {"observation": f"eGFR = {egfr} mL/min/1.73m²", "criteria": "KDIGO CKD", "fact": "eGFR < 15: CKD G5 (腎衰竭)", "reference": "KDIGO 2012"}
            )
        elif egfr < 30:
            analysis.append(
                {"observation": f"eGFR = {egfr} mL/min/1.73m²", "criteria": "KDIGO CKD", "fact": "eGFR 15-29: CKD G4 (重度下降)", "reference": "KDIGO 2012"}
            )

    # NEWS2 escalation
    news2 = scores.get("news2_score")
    if news2 is not None:
        if news2 >= 7:
            analysis.append(
                {
                    "observation": f"NEWS2 = {news2}",
                    "criteria": "RCP 2017",
                    "fact": "NEWS2 ≥ 7: 符合緊急呼叫標準 (Red alert)",
                    "reference": "Royal College of Physicians 2017",
                }
            )

    if not analysis:
        analysis.append({"observation": "無特殊交叉分析", "criteria": "-", "fact": "各項分數獨立，無特定跨工具標準適用", "reference": "-"})

    return analysis


def _build_param_schemas(calculator: Any) -> dict[str, dict[str, Any]]:
    """
    Build detailed parameter schemas with source mapping.

    Args:
        calculator: Calculator instance

    Returns:
        Dictionary of param_name -> schema details
    """
    # Parameter source mapping (where to find these values clinically)
    PARAM_SOURCES: dict[str, dict[str, Any]] = {
        # Lab values
        "serum_creatinine": {
            "type": "number",
            "unit": "mg/dL",
            "description": "Serum creatinine level",
            "clinical_hint": "Measured from blood sample",
            "normal_range": [0.6, 1.2],
            "common_sources": ["BMP", "CMP", "Renal panel"],
        },
        "creatinine": {
            "type": "number",
            "unit": "mg/dL",
            "description": "Serum creatinine",
            "clinical_hint": "From metabolic panel",
            "normal_range": [0.6, 1.2],
            "common_sources": ["BMP", "CMP", "Renal panel"],
        },
        "bilirubin": {
            "type": "number",
            "unit": "mg/dL",
            "description": "Total bilirubin",
            "clinical_hint": "From liver function tests",
            "normal_range": [0.1, 1.2],
            "common_sources": ["LFT", "Hepatic panel"],
        },
        "platelets": {
            "type": "number",
            "unit": "×10³/µL",
            "description": "Platelet count",
            "clinical_hint": "From complete blood count",
            "normal_range": [150, 400],
            "common_sources": ["CBC"],
        },
        "inr": {
            "type": "number",
            "unit": "",
            "description": "International Normalized Ratio",
            "clinical_hint": "From coagulation panel",
            "normal_range": [0.9, 1.1],
            "common_sources": ["PT/INR", "Coag panel"],
        },
        "sodium": {
            "type": "number",
            "unit": "mEq/L",
            "description": "Serum sodium",
            "clinical_hint": "From metabolic panel",
            "normal_range": [136, 145],
            "common_sources": ["BMP", "CMP"],
        },
        "potassium": {
            "type": "number",
            "unit": "mEq/L",
            "description": "Serum potassium",
            "clinical_hint": "From metabolic panel",
            "normal_range": [3.5, 5.0],
            "common_sources": ["BMP", "CMP"],
        },
        "glucose": {
            "type": "number",
            "unit": "mg/dL",
            "description": "Blood glucose",
            "clinical_hint": "From metabolic panel or point-of-care",
            "normal_range": [70, 100],
            "common_sources": ["BMP", "CMP", "POC glucose"],
        },
        "albumin": {
            "type": "number",
            "unit": "g/dL",
            "description": "Serum albumin",
            "clinical_hint": "From liver function tests",
            "normal_range": [3.5, 5.0],
            "common_sources": ["LFT", "CMP"],
        },
        # Vital signs
        "heart_rate": {
            "type": "number",
            "unit": "bpm",
            "description": "Heart rate",
            "clinical_hint": "From vital signs monitor",
            "normal_range": [60, 100],
            "common_sources": ["Vital signs", "ECG monitor", "Pulse oximeter"],
        },
        "systolic_bp": {
            "type": "number",
            "unit": "mmHg",
            "description": "Systolic blood pressure",
            "clinical_hint": "From vital signs",
            "normal_range": [90, 140],
            "common_sources": ["Vital signs", "Arterial line"],
        },
        "respiratory_rate": {
            "type": "number",
            "unit": "/min",
            "description": "Respiratory rate",
            "clinical_hint": "Count breaths per minute",
            "normal_range": [12, 20],
            "common_sources": ["Vital signs", "Bedside observation"],
        },
        "temperature": {
            "type": "number",
            "unit": "°C",
            "description": "Body temperature",
            "clinical_hint": "From vital signs",
            "normal_range": [36.5, 37.5],
            "common_sources": ["Vital signs"],
        },
        "spo2": {
            "type": "number",
            "unit": "%",
            "description": "Oxygen saturation",
            "clinical_hint": "From pulse oximeter",
            "normal_range": [95, 100],
            "common_sources": ["Pulse oximeter", "Vital signs"],
        },
        # Blood gas
        "pao2_fio2_ratio": {
            "type": "number",
            "unit": "mmHg",
            "description": "PaO2/FiO2 ratio (P/F ratio)",
            "clinical_hint": "Calculate: PaO2 ÷ FiO2 (as decimal)",
            "normal_range": [400, 500],
            "common_sources": ["ABG + Ventilator FiO2"],
        },
        "ph": {
            "type": "number",
            "unit": "",
            "description": "Arterial blood pH",
            "clinical_hint": "From arterial blood gas",
            "normal_range": [7.35, 7.45],
            "common_sources": ["ABG"],
        },
        "pco2": {
            "type": "number",
            "unit": "mmHg",
            "description": "Partial pressure of CO2",
            "clinical_hint": "From arterial blood gas",
            "normal_range": [35, 45],
            "common_sources": ["ABG"],
        },
        "hco3": {
            "type": "number",
            "unit": "mEq/L",
            "description": "Bicarbonate",
            "clinical_hint": "From ABG or metabolic panel",
            "normal_range": [22, 26],
            "common_sources": ["ABG", "BMP"],
        },
        # Demographics
        "age": {
            "type": "number",
            "unit": "years",
            "description": "Patient age",
            "clinical_hint": "From patient demographics",
            "normal_range": [0, 120],
            "common_sources": ["EMR demographics", "Patient interview"],
        },
        "sex": {
            "type": "string",
            "unit": "",
            "description": "Biological sex",
            "clinical_hint": "male or female",
            "valid_values": ["male", "female"],
            "common_sources": ["EMR demographics"],
        },
        "weight": {
            "type": "number",
            "unit": "kg",
            "description": "Body weight",
            "clinical_hint": "Measured weight in kilograms",
            "normal_range": [2, 300],
            "common_sources": ["Nursing assessment", "Admission weight"],
        },
        "height": {
            "type": "number",
            "unit": "cm",
            "description": "Height",
            "clinical_hint": "Measured height in centimeters",
            "normal_range": [50, 250],
            "common_sources": ["Nursing assessment"],
        },
        # Scores
        "gcs_score": {
            "type": "number",
            "unit": "",
            "description": "Glasgow Coma Scale total",
            "clinical_hint": "Sum of E + V + M components",
            "normal_range": [3, 15],
            "common_sources": ["Neurological assessment", "calculate_gcs"],
        },
    }

    # Get required params from calculator
    param_names = list(calculator.metadata.low_level.input_params)

    schemas: dict[str, dict[str, Any]] = {}
    for param in param_names:
        if param in PARAM_SOURCES:
            schemas[param] = PARAM_SOURCES[param]
        else:
            # Generate generic schema
            schemas[param] = {
                "type": "number",
                "unit": "",
                "description": param.replace("_", " ").title(),
                "clinical_hint": "See calculator documentation",
                "common_sources": ["Clinical assessment"],
            }

    return schemas
