"""
Calculator Handler

MCP tool handlers for calculator operations.

NEW DESIGN (v2.0): 單一 calculate() 工具 + Discovery 工具
======================================================
原先 75 個獨立的 calculate_xxx() 工具已被整合為一個通用的 calculate() 函數，
這大幅減少了 token 消耗，同時保持完整的計算功能。

工作流程:
1. 使用 discovery 工具找到需要的計算器 (list_by_specialty, search_calculators 等)
2. 使用 get_calculator_info(tool_id) 查看參數
3. 使用 calculate(tool_id, params) 執行計算

OLD DESIGN (已註解): 每個計算器有獨立的 MCP tool
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from ....application.dto import CalculateRequest
from ....application.use_cases import CalculateUseCase
from ....domain.registry.tool_registry import ToolRegistry

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

    NEW DESIGN: 單一 calculate() 工具
    ================================
    - calculate(tool_id, params) - 通用計算函數，支援所有 75+ 計算器

    舊設計的 75 個獨立工具已註解，可在需要時恢復。
    """

    def __init__(self, mcp: FastMCP, registry: ToolRegistry):
        self._mcp = mcp
        self._registry = registry
        self._use_case = CalculateUseCase(registry)

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
