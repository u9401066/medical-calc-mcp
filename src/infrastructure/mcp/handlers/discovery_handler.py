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
        def discover_tools(query: str, limit: int = 10) -> dict[str, Any]:
            """
            搜尋醫學計算工具
            
            Search for medical calculators by:
            - Clinical question (e.g., "What is the cardiac risk?")
            - Specialty (e.g., "anesthesiology", "critical care")
            - Condition (e.g., "sepsis", "difficult airway")
            - Keywords (e.g., "SOFA", "qSOFA", "eGFR")
            
            Args:
                query: 搜尋關鍵字、臨床問題或專科名稱
                limit: 最多回傳幾個結果 (預設 10)
                
            Returns:
                匹配的計算工具清單
            """
            request = DiscoveryRequest(
                mode=DiscoveryMode.SEARCH,
                query=query,
                limit=limit
            )
            response = self._use_case.execute(request)
            return response.to_dict()
        
        @self._mcp.tool()
        def list_by_specialty(specialty: str, limit: int = 20) -> dict[str, Any]:
            """
            依專科列出工具
            
            List calculators for a specific medical specialty.
            
            Args:
                specialty: 專科名稱 (e.g., "critical_care", "anesthesiology", "nephrology")
                limit: 最多回傳幾個結果 (預設 20)
                
            Returns:
                該專科的計算工具清單
                
            Available specialties (可用專科):
                - critical_care: 重症加護
                - anesthesiology: 麻醉科
                - emergency_medicine: 急診醫學
                - nephrology: 腎臟科
                - cardiology: 心臟科
                - internal_medicine: 內科
                - pulmonology: 胸腔內科
                - neurology: 神經科
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
            依臨床情境列出工具
            
            List calculators for a specific clinical context.
            
            Args:
                context: 臨床情境 (e.g., "preoperative_assessment", "severity_assessment")
                limit: 最多回傳幾個結果 (預設 20)
                
            Returns:
                該情境的計算工具清單
                
            Available contexts (可用情境):
                - preoperative_assessment: 術前評估
                - severity_assessment: 嚴重度評估
                - prognosis: 預後評估
                - diagnosis: 診斷
                - risk_stratification: 風險分層
                - sedation_assessment: 鎮靜評估
                - delirium_assessment: 譫妄評估
                - airway_management: 氣道管理
                - icu_management: ICU 管理
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
