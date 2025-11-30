"""
Discovery Handler

MCP tool handlers for tool discovery operations.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from ....application.dto import DiscoveryMode, DiscoveryRequest
from ....application.use_cases import DiscoveryUseCase
from ....domain.registry.tool_registry import ToolRegistry


class DiscoveryHandler:
    """
    Handler for discovery-related MCP tools.
    
    Registers all discovery tools with the MCP server.
    """
    
    def __init__(self, mcp: FastMCP, registry: ToolRegistry):
        self._mcp = mcp
        self._registry = registry
        self._use_case = DiscoveryUseCase(registry)
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register all discovery tools with MCP"""
        
        @self._mcp.tool()
        def discover_tools(
            keyword: str = "",
            specialty: str = "",
            context: str = "",
            condition: str = "",
            limit: int = 10
        ) -> dict[str, Any]:
            """
            🔍 搜尋醫學計算工具 (Menu-Based Discovery)
            
            這是一個結構化的搜尋工具。請使用以下其中一種方式搜尋:
            
            ## 搜尋方式 (擇一使用):
            
            1. **keyword** - 用關鍵字搜尋 (必須完全匹配)
               Examples: "rcri", "sofa", "gcs", "cardiac risk", "sepsis"
               
            2. **specialty** - 依專科篩選
               Options: "critical_care", "anesthesiology", "nephrology", 
                        "cardiology", "surgery", "emergency_medicine",
                        "internal_medicine", "neurology", "pediatrics"
                        
            3. **context** - 依臨床情境篩選  
               Options: "preoperative_assessment", "severity_assessment",
                        "prognosis", "risk_stratification", "icu_management",
                        "sedation_assessment", "delirium_assessment",
                        "transfusion_decision", "drug_dosing", "screening"
                        
            4. **condition** - 依疾病/狀況篩選
               Examples: "sepsis", "head injury", "difficult airway",
                         "perioperative mi", "delirium", "hemorrhage"
            
            ## 建議流程:
            1. 先用 list_specialties() 或 list_contexts() 查看可用選項
            2. 再用此工具搭配正確的參數搜尋
            3. 或直接呼叫已知的計算工具 (如 calculate_rcri)
            
            Args:
                keyword: 關鍵字 (如 "rcri", "sofa", "cardiac risk")
                specialty: 專科名稱 (如 "anesthesiology")
                context: 臨床情境 (如 "preoperative_assessment")
                condition: 疾病/狀況 (如 "sepsis")
                limit: 最多回傳幾個結果 (預設 10)
                
            Returns:
                匹配的計算工具清單，包含 tool_id 供後續呼叫使用
            """
            # Determine search mode based on provided parameters
            if specialty:
                request = DiscoveryRequest(
                    mode=DiscoveryMode.BY_SPECIALTY,
                    specialty=specialty,
                    limit=limit
                )
            elif context:
                request = DiscoveryRequest(
                    mode=DiscoveryMode.BY_CONTEXT,
                    context=context,
                    limit=limit
                )
            elif condition:
                request = DiscoveryRequest(
                    mode=DiscoveryMode.BY_CONDITION,
                    condition=condition,
                    limit=limit
                )
            elif keyword:
                request = DiscoveryRequest(
                    mode=DiscoveryMode.SEARCH,
                    query=keyword,
                    limit=limit
                )
            else:
                # No parameters - list all
                request = DiscoveryRequest(
                    mode=DiscoveryMode.LIST_ALL,
                    limit=limit
                )
            
            response = self._use_case.execute(request)
            return response.to_dict()
        
        @self._mcp.tool()
        def list_by_specialty(specialty: str, limit: int = 20) -> dict[str, Any]:
            """
            依專科列出工具 (先用 list_specialties 查看可用選項)
            
            Args:
                specialty: 專科名稱 - 必須是以下其中之一:
                    - critical_care (重症加護)
                    - anesthesiology (麻醉科)
                    - surgery (外科)
                    - emergency_medicine (急診醫學)
                    - nephrology (腎臟科)
                    - cardiology (心臟科)
                    - internal_medicine (內科)
                    - pulmonology (胸腔內科)
                    - neurology (神經科)
                    - pediatrics (小兒科)
                    - hematology (血液科)
                limit: 最多回傳幾個結果
                
            Returns:
                該專科的計算工具清單 (包含 tool_id)
                
            Tip: 不確定有哪些專科？先呼叫 list_specialties()
            """
            request = DiscoveryRequest(
                mode=DiscoveryMode.BY_SPECIALTY,
                specialty=specialty,
                limit=limit
            )
            response = self._use_case.execute(request)
            return response.to_dict()
        
        @self._mcp.tool()
        def list_by_context(context: str, limit: int = 20) -> dict[str, Any]:
            """
            依臨床情境列出工具 (先用 list_contexts 查看可用選項)
            
            Args:
                context: 臨床情境 - 必須是以下其中之一:
                    - preoperative_assessment (術前評估)
                    - severity_assessment (嚴重度評估)
                    - risk_stratification (風險分層)
                    - prognosis (預後評估)
                    - icu_management (ICU 管理)
                    - sedation_assessment (鎮靜評估)
                    - delirium_assessment (譫妄評估)
                    - transfusion_decision (輸血決策)
                    - drug_dosing (藥物劑量)
                    - screening (篩檢)
                    - monitoring (監測)
                    - airway_management (氣道管理)
                limit: 最多回傳幾個結果
                
            Returns:
                該情境的計算工具清單 (包含 tool_id)
                
            Tip: 不確定有哪些情境？先呼叫 list_contexts()
            """
            request = DiscoveryRequest(
                mode=DiscoveryMode.BY_CONTEXT,
                context=context,
                limit=limit
            )
            response = self._use_case.execute(request)
            return response.to_dict()
        
        @self._mcp.tool()
        def list_calculators(limit: int = 50) -> dict[str, Any]:
            """
            列出所有可用的醫學計算工具
            
            List all available medical calculators.
            
            Args:
                limit: 最多回傳幾個結果 (預設 50)
                
            Returns:
                所有計算器的清單，包含 tool_id, name, purpose, specialties
            """
            request = DiscoveryRequest(
                mode=DiscoveryMode.LIST_ALL,
                limit=limit
            )
            response = self._use_case.execute(request)
            return response.to_dict()
        
        @self._mcp.tool()
        def get_calculator_info(tool_id: str) -> dict[str, Any]:
            """
            取得特定計算器的詳細資訊
            
            Get detailed information about a specific calculator including:
            - Input parameters and their descriptions
            - Clinical contexts and conditions
            - Paper references with PMID/DOI
            
            Args:
                tool_id: 計算器 ID (e.g., "sofa_score", "ckd_epi_2021", "rcri")
                
            Returns:
                計算器的完整 metadata 和使用說明
            """
            request = DiscoveryRequest(
                mode=DiscoveryMode.GET_INFO,
                tool_id=tool_id
            )
            response = self._use_case.execute(request)
            return response.to_dict()
        
        @self._mcp.tool()
        def list_specialties() -> dict[str, Any]:
            """
            列出所有可用的專科
            
            List all medical specialties that have registered calculators.
            Use this to see what specialties are available for filtering.
            
            Returns:
                可用專科清單
            """
            request = DiscoveryRequest(mode=DiscoveryMode.LIST_SPECIALTIES)
            response = self._use_case.execute(request)
            return response.to_dict()
        
        @self._mcp.tool()
        def list_contexts() -> dict[str, Any]:
            """
            列出所有可用的臨床情境
            
            List all clinical contexts that have registered calculators.
            Use this to see what contexts are available for filtering.
            
            Returns:
                可用臨床情境清單
            """
            request = DiscoveryRequest(mode=DiscoveryMode.LIST_CONTEXTS)
            response = self._use_case.execute(request)
            return response.to_dict()
