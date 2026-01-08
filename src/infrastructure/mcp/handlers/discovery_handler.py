"""
Discovery Handler

MCP tool handlers for tool discovery operations.

v3.0 CONSOLIDATED DESIGN (保持 High-Level / Low-Level 分層):
============================================================

HIGH-LEVEL TOOLS (Agent 決策層) - 3 個:
├── discover()           - 統一的工具發現入口
├── get_related_tools()  - 語義關聯推薦
└── find_tools_by_params() - 反向參數查找

這些工具幫助 Agent:
1. 理解有哪些分類 (專科、情境)
2. 在分類中找到合適的工具
3. 發現相關工具和參數匹配

整併說明:
- list_specialties() + list_contexts() + list_calculators() → discover(by="all")
- list_by_specialty() + list_by_context() → discover(by="specialty/context")
- search_calculators() → discover(by="keyword")
- get_calculator_info() → 移至 calculator_handler 的 get_tool_schema()
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from ....application.dto import DiscoveryMode, DiscoveryRequest
from ....application.use_cases import DiscoveryUseCase
from ....domain.registry.tool_registry import ToolRegistry


class DiscoveryHandler:
    """
    Handler for discovery-related MCP tools.

    v3.0: Consolidated to 3 high-level tools while maintaining
    the high-level / low-level separation.
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
        # HIGH-LEVEL TOOL 1: Unified Discovery
        # ================================================================

        @self._mcp.tool()
        def discover(by: str = "all", value: str | None = None, limit: int = 20) -> dict[str, Any]:
            """
            🔍 統一的工具發現入口 (High-Level)

            幫助 Agent 找到合適的醫學計算器。支援多種發現模式。

            Args:
                by: 發現模式
                    - "all": 列出所有分類 (專科和臨床情境) - 預設
                    - "specialty": 依專科篩選工具
                    - "context": 依臨床情境篩選工具
                    - "keyword": 關鍵字搜尋
                    - "tools": 列出所有工具
                value: 篩選值 (當 by 不是 "all" 或 "tools" 時必填)
                limit: 最多回傳幾個結果

            Returns:
                根據模式返回不同內容:
                - all: 可用的專科和情境清單
                - specialty/context: 該分類下的工具清單
                - keyword: 匹配的工具清單
                - tools: 所有工具清單

            **Examples:**

            ```python
            # 查看所有分類 (起點)
            discover()
            # → {"specialties": [...], "contexts": [...]}

            # 依專科篩選
            discover(by="specialty", value="critical_care")
            # → {"tools": [{"tool_id": "sofa_score", ...}, ...]}

            # 依臨床情境篩選
            discover(by="context", value="preoperative_assessment")
            # → {"tools": [{"tool_id": "rcri", ...}, ...]}

            # 關鍵字搜尋
            discover(by="keyword", value="sepsis")
            # → {"tools": [{"tool_id": "qsofa_score", ...}, ...]}

            # 列出所有工具
            discover(by="tools", limit=50)
            # → {"tools": [...], "count": 75}
            ```

            ⏭️ 下一步: 找到工具後，使用 get_tool_schema(tool_id) 查看參數
            """
            # Route to appropriate discovery mode
            if by == "all":
                # List all specialties and contexts
                spec_request = DiscoveryRequest(mode=DiscoveryMode.LIST_SPECIALTIES)
                spec_response = self._use_case.execute(spec_request)

                ctx_request = DiscoveryRequest(mode=DiscoveryMode.LIST_CONTEXTS)
                ctx_response = self._use_case.execute(ctx_request)

                return {
                    "success": True,
                    "mode": "all",
                    "specialties": {
                        "available": spec_response.available_specialties,
                        "count": len(spec_response.available_specialties),
                    },
                    "contexts": {
                        "available": ctx_response.available_contexts,
                        "count": len(ctx_response.available_contexts),
                    },
                    "next_step": "discover(by='specialty', value='專科名稱') 或 discover(by='context', value='情境名稱')",
                    "examples": [
                        "discover(by='specialty', value='critical_care')",
                        "discover(by='context', value='preoperative_assessment')",
                        "discover(by='keyword', value='sepsis')",
                    ],
                }

            elif by == "specialty":
                if not value:
                    return {"success": False, "error": "specialty 模式需要提供 value 參數", "hint": "先呼叫 discover() 查看可用的專科名稱"}
                request = DiscoveryRequest(mode=DiscoveryMode.BY_SPECIALTY, specialty=value, limit=limit)
                response = self._use_case.execute(request)
                result = response.to_dict()

                if result.get("success"):
                    result["filter"] = {"by": "specialty", "value": value}
                    result["next_step"] = "get_tool_schema(tool_id) 查看參數，然後 calculate(tool_id, params)"
                    if result.get("tools") and len(result["tools"]) > 0:
                        result["example"] = f"get_tool_schema('{result['tools'][0]['tool_id']}')"
                else:
                    result["hint"] = "呼叫 discover() 查看可用的專科名稱"

                return result

            elif by == "context":
                if not value:
                    return {"success": False, "error": "context 模式需要提供 value 參數", "hint": "先呼叫 discover() 查看可用的情境名稱"}
                request = DiscoveryRequest(mode=DiscoveryMode.BY_CONTEXT, context=value, limit=limit)
                response = self._use_case.execute(request)
                result = response.to_dict()

                if result.get("success"):
                    result["filter"] = {"by": "context", "value": value}
                    result["next_step"] = "get_tool_schema(tool_id) 查看參數，然後 calculate(tool_id, params)"
                    if result.get("tools") and len(result["tools"]) > 0:
                        result["example"] = f"get_tool_schema('{result['tools'][0]['tool_id']}')"
                else:
                    result["hint"] = "呼叫 discover() 查看可用的情境名稱"

                return result

            elif by == "keyword":
                if not value:
                    return {"success": False, "error": "keyword 模式需要提供 value 參數", "hint": "提供搜尋關鍵字，例如 'sepsis', 'cardiac', 'renal'"}
                request = DiscoveryRequest(mode=DiscoveryMode.SEARCH, query=value, limit=limit)
                response = self._use_case.execute(request)
                result = response.to_dict()

                if result.get("count", 0) == 0:
                    result["hint"] = "找不到結果？試試 discover() 瀏覽分類"
                else:
                    result["next_step"] = "get_tool_schema(tool_id) 查看參數"

                result["filter"] = {"by": "keyword", "value": value}
                return result

            elif by == "tools":
                request = DiscoveryRequest(mode=DiscoveryMode.LIST_ALL, limit=limit)
                response = self._use_case.execute(request)
                result = response.to_dict()
                result["next_step"] = "get_tool_schema(tool_id) 查看工具詳情"
                return result

            else:
                return {
                    "success": False,
                    "error": f"未知的 by 參數: {by}",
                    "valid_values": ["all", "specialty", "context", "keyword", "tools"],
                    "examples": [
                        "discover()  # 列出所有分類",
                        "discover(by='specialty', value='critical_care')",
                        "discover(by='context', value='preoperative_assessment')",
                        "discover(by='keyword', value='sepsis')",
                        "discover(by='tools')  # 列出所有工具",
                    ],
                }

        # ================================================================
        # HIGH-LEVEL TOOL 2: Related Tools (Semantic Discovery)
        # ================================================================

        @self._mcp.tool()
        def get_related_tools(tool_id: str, limit: int = 5) -> dict[str, Any]:
            """
            🔗 取得相關工具 (High-Level 語義發現)

            基於共享參數和專科自動發現相關工具。
            純 Python 算法，無 ML 依賴。

            Args:
                tool_id: 工具 ID
                limit: 最多回傳幾個相關工具

            Returns:
                相關工具清單及相似度分數

            **Example:**
            ```python
            get_related_tools("sofa_score")
            # → {"related_tools": [
            #      {"tool_id": "qsofa_score", "similarity": 0.85},
            #      {"tool_id": "apache_ii", "similarity": 0.72},
            #      ...
            #    ]}
            ```

            💡 相關性基於: 共享參數、相同專科、相同臨床情境
            """
            related = self._registry.get_related_tools(tool_id, limit)

            if not related:
                return {"success": False, "error": f"找不到工具: {tool_id}", "hint": "請先使用 discover(by='keyword', value='關鍵字') 找到工具"}

            # Enrich with metadata
            tools = []
            for rel_id, score in related:
                calc = self._registry.get_calculator(rel_id)
                if calc:
                    tools.append(
                        {
                            "tool_id": rel_id,
                            "name": calc.metadata.low_level.name,
                            "purpose": calc.metadata.low_level.purpose,
                            "similarity": round(score, 3),
                        }
                    )

            return {
                "success": True,
                "source_tool": tool_id,
                "related_tools": tools,
                "count": len(tools),
                "note": "相關性基於: 共享參數、相同專科、相同臨床情境",
                "next_step": "get_tool_schema(tool_id) 查看詳情，然後 calculate(tool_id, params)",
            }

        # ================================================================
        # HIGH-LEVEL TOOL 3: Reverse Parameter Lookup
        # ================================================================

        @self._mcp.tool()
        def find_tools_by_params(params: list[str]) -> dict[str, Any]:
            """
            🔍 根據已有參數找工具 (High-Level 反向查找)

            「我有這些數值，可以計算什麼？」

            Args:
                params: 參數名稱列表
                    Examples: ["creatinine", "age", "weight"]
                             ["gcs", "pupil", "motor"]
                             ["bilirubin", "inr", "ascites"]

            Returns:
                可使用這些參數的工具清單

            **Example:**
            ```python
            find_tools_by_params(["age", "creatinine", "bilirubin"])
            # → {"tools": [
            #      {"tool_id": "meld_score", "input_params": [...]},
            #      {"tool_id": "ckd_epi_2021", "input_params": [...]},
            #      ...
            #    ]}
            ```

            💡 適合場景: 已有病患數據，想知道能計算哪些評分
            """
            results = self._registry.find_tools_by_params(params)

            if not results:
                return {"success": True, "tools": [], "count": 0, "input_params": params, "hint": "沒有找到匹配的工具。試試更多參數或不同的參數名稱。"}

            tools = [
                {
                    "tool_id": m.low_level.tool_id,
                    "name": m.low_level.name,
                    "purpose": m.low_level.purpose,
                    "input_params": list(m.low_level.input_params),
                }
                for m in results[:10]  # Limit to 10
            ]

            return {"success": True, "input_params": params, "tools": tools, "count": len(tools), "next_step": "get_tool_schema(tool_id) 查看完整參數需求"}
