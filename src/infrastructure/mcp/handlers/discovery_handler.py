"""
Discovery Handler

MCP tool handlers for tool discovery operations.

Hierarchical Navigation Design:
==============================
Path A: Specialty-based
  list_specialties() → list_by_specialty("X") → calculate_X(...)

Path B: Context-based
  list_contexts() → list_by_context("X") → calculate_X(...)

Path C: Direct (if tool_id known)
  get_calculator_info("X") → calculate_X(...)
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from ....application.dto import DiscoveryMode, DiscoveryRequest
from ....application.use_cases import DiscoveryUseCase
from ....domain.registry.tool_registry import ToolRegistry


class DiscoveryHandler:
    """
    Handler for discovery-related MCP tools.

    Provides hierarchical navigation for finding calculators.
    """

    def __init__(self, mcp: FastMCP, registry: ToolRegistry):
        self._mcp = mcp
        self._registry = registry
        self._use_case = DiscoveryUseCase(registry)

        # Register tools
        self._register_tools()

    def _register_tools(self) -> None:
        """Register all discovery tools with MCP"""

        # ================================================================
        # STEP 1: Entry Points (選擇導航路徑)
        # ================================================================

        @self._mcp.tool()
        def list_specialties() -> dict[str, Any]:
            """
            📋 Step 1A: 列出所有可用的醫學專科

            這是專科導航的起點。取得專科清單後，
            使用 list_by_specialty(specialty) 查看該專科的工具。

            Returns:
                available_specialties: 專科清單及各專科的工具數量

            ⏭️ 下一步: 選擇一個專科，呼叫 list_by_specialty("專科名稱")

            Example flow:
                1. list_specialties() → 得到 ["critical_care", "anesthesiology", ...]
                2. list_by_specialty("anesthesiology") → 得到工具清單
                3. calculate_rcri(...) 或 get_calculator_info("rcri") 了解參數
            """
            request = DiscoveryRequest(mode=DiscoveryMode.LIST_SPECIALTIES)
            response = self._use_case.execute(request)
            result = response.to_dict()
            result["next_step"] = "呼叫 list_by_specialty(specialty) 查看該專科的工具"
            result["example"] = "list_by_specialty('critical_care')"
            return result

        @self._mcp.tool()
        def list_contexts() -> dict[str, Any]:
            """
            📋 Step 1B: 列出所有可用的臨床情境

            這是情境導航的起點。取得情境清單後，
            使用 list_by_context(context) 查看該情境適用的工具。

            Returns:
                available_contexts: 臨床情境清單及各情境的工具數量

            ⏭️ 下一步: 選擇一個情境，呼叫 list_by_context("情境名稱")

            Example flow:
                1. list_contexts() → 得到 ["preoperative_assessment", "icu_management", ...]
                2. list_by_context("preoperative_assessment") → 得到工具清單
                3. calculate_asa_physical_status(...) 或 get_calculator_info("asa_physical_status")
            """
            request = DiscoveryRequest(mode=DiscoveryMode.LIST_CONTEXTS)
            response = self._use_case.execute(request)
            result = response.to_dict()
            result["next_step"] = "呼叫 list_by_context(context) 查看該情境的工具"
            result["example"] = "list_by_context('preoperative_assessment')"
            return result

        @self._mcp.tool()
        def list_calculators(limit: int = 50) -> dict[str, Any]:
            """
            📋 列出所有可用的醫學計算工具

            直接列出所有工具，適合快速瀏覽或已知大概要找什麼。

            Args:
                limit: 最多回傳幾個結果 (預設 50)

            Returns:
                所有計算器的清單，包含 tool_id, name, purpose

            ⏭️ 下一步:
                - 找到想用的工具後，呼叫 get_calculator_info(tool_id) 查看參數
                - 或直接呼叫 calculate_xxx(...) 進行計算
            """
            request = DiscoveryRequest(
                mode=DiscoveryMode.LIST_ALL,
                limit=limit
            )
            response = self._use_case.execute(request)
            result = response.to_dict()
            result["next_step"] = "呼叫 get_calculator_info(tool_id) 查看工具詳情，或直接使用 calculate_xxx()"
            return result

        # ================================================================
        # STEP 2: Filter by Category (依分類篩選)
        # ================================================================

        @self._mcp.tool()
        def list_by_specialty(specialty: str, limit: int = 20) -> dict[str, Any]:
            """
            📋 Step 2A: 列出指定專科的所有工具

            Args:
                specialty: 專科名稱 (從 list_specialties 取得)
                limit: 最多回傳幾個結果

            Returns:
                該專科的計算工具清單 (tool_id, name, purpose)

            ⏭️ 下一步:
                - get_calculator_info(tool_id) - 查看工具的詳細參數說明
                - calculate_xxx(...) - 直接呼叫計算工具

            ⏮️ 上一步: list_specialties() 查看所有專科
            """
            request = DiscoveryRequest(
                mode=DiscoveryMode.BY_SPECIALTY,
                specialty=specialty,
                limit=limit
            )
            response = self._use_case.execute(request)
            result = response.to_dict()

            if result.get("success"):
                result["next_step"] = "選擇 tool_id，呼叫 get_calculator_info(tool_id) 或直接 calculate_xxx()"
                result["previous_step"] = "list_specialties()"
                # Add example
                if result.get("tools") and len(result["tools"]) > 0:
                    example_id = result["tools"][0]["tool_id"]
                    result["example"] = f"get_calculator_info('{example_id}')"
            else:
                result["hint"] = "請先呼叫 list_specialties() 查看可用的專科名稱"

            return result

        @self._mcp.tool()
        def list_by_context(context: str, limit: int = 20) -> dict[str, Any]:
            """
            📋 Step 2B: 列出指定臨床情境的所有工具

            Args:
                context: 臨床情境 (從 list_contexts 取得)
                limit: 最多回傳幾個結果

            Returns:
                該情境的計算工具清單 (tool_id, name, purpose)

            ⏭️ 下一步:
                - get_calculator_info(tool_id) - 查看工具的詳細參數說明
                - calculate_xxx(...) - 直接呼叫計算工具

            ⏮️ 上一步: list_contexts() 查看所有臨床情境
            """
            request = DiscoveryRequest(
                mode=DiscoveryMode.BY_CONTEXT,
                context=context,
                limit=limit
            )
            response = self._use_case.execute(request)
            result = response.to_dict()

            if result.get("success"):
                result["next_step"] = "選擇 tool_id，呼叫 get_calculator_info(tool_id) 或直接 calculate_xxx()"
                result["previous_step"] = "list_contexts()"
                if result.get("tools") and len(result["tools"]) > 0:
                    example_id = result["tools"][0]["tool_id"]
                    result["example"] = f"get_calculator_info('{example_id}')"
            else:
                result["hint"] = "請先呼叫 list_contexts() 查看可用的情境名稱"

            return result

        # ================================================================
        # STEP 3: Get Tool Details (取得工具詳情)
        # ================================================================

        @self._mcp.tool()
        def get_calculator_info(tool_id: str) -> dict[str, Any]:
            """
            📖 Step 3: 取得計算器的詳細資訊

            查看特定計算器的完整說明，包括：
            - 所有輸入參數及其說明
            - 適用的臨床情境和疾病
            - 參考文獻 (PMID/DOI)

            Args:
                tool_id: 計算器 ID (從 list_by_specialty 或 list_by_context 取得)

            Returns:
                計算器的完整 metadata 和參數說明

            ⏭️ 下一步: 使用對應的 calculate_xxx(...) 函數進行計算

            Example:
                get_calculator_info("rcri")
                → 得到 RCRI 的參數說明
                → 呼叫 calculate_rcri(high_risk_surgery=True, ...)
            """
            request = DiscoveryRequest(
                mode=DiscoveryMode.GET_INFO,
                tool_id=tool_id
            )
            response = self._use_case.execute(request)
            result = response.to_dict()

            if result.get("success"):
                result["next_step"] = f"使用 calculate_{tool_id}(...) 進行計算"
                result["navigation"] = {
                    "back_to_specialties": "list_specialties()",
                    "back_to_contexts": "list_contexts()",
                    "list_all": "list_calculators()"
                }

            return result

        # ================================================================
        # OPTIONAL: Quick Search (快速搜尋 - 已知關鍵字時使用)
        # ================================================================

        @self._mcp.tool()
        def search_calculators(
            keyword: str,
            limit: int = 10
        ) -> dict[str, Any]:
            """
            🔍 快速搜尋 (已知關鍵字時使用)

            用關鍵字直接搜尋工具。適合已經知道要找什麼的情況。

            Args:
                keyword: 搜尋關鍵字
                    Examples: "sofa", "rcri", "gcs", "sepsis", "cardiac"
                limit: 最多回傳幾個結果

            Returns:
                匹配的工具清單

            💡 不確定關鍵字？建議使用階層導航:
                - list_specialties() → list_by_specialty()
                - list_contexts() → list_by_context()
            """
            request = DiscoveryRequest(
                mode=DiscoveryMode.SEARCH,
                query=keyword,
                limit=limit
            )
            response = self._use_case.execute(request)
            result = response.to_dict()

            if result.get("count", 0) == 0:
                result["hint"] = "找不到結果？試試 list_specialties() 或 list_contexts() 瀏覽"
            else:
                result["next_step"] = "選擇 tool_id，呼叫 get_calculator_info(tool_id) 查看詳情"

            return result
