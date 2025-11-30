"""
Pediatric & Anesthesia Calculator Tools

MCP tool handlers for pediatric and anesthesia calculators.
"""

from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_pediatric_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all pediatric and anesthesia calculator tools with MCP"""
    
    @mcp.tool()
    def calculate_pediatric_drug_dose(
        drug_name: str,
        weight_kg: float,
        route: str = "iv",
        indication: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        小兒藥物劑量計算器
        
        根據體重計算常見小兒藥物的建議劑量，包含安全上限檢查。
        
        Args:
            drug_name: 藥物名稱 (例如: acetaminophen, ibuprofen, amoxicillin, 
                       ceftriaxone, ondansetron, morphine, fentanyl, ketamine)
            weight_kg: 體重 (公斤)
            route: 給藥途徑 (iv, po, im, pr)
            indication: 適應症 (可選，用於選擇適當劑量)
            
        Returns:
            建議劑量範圍、最大劑量、給藥頻率和注意事項
            
        References:
            Lexicomp Pediatric & Neonatal Dosage Handbook
            Nelson Textbook of Pediatrics, 21st ed
        """
        request = CalculateRequest(
            tool_id="pediatric_dosing",
            params={
                "drug_name": drug_name,
                "weight_kg": weight_kg,
                "route": route,
                "indication": indication,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
    
    @mcp.tool()
    def calculate_mabl(
        weight_kg: float,
        initial_hematocrit: float,
        target_hematocrit: float,
        patient_type: str = "adult_male",
    ) -> dict[str, Any]:
        """
        計算最大允許失血量 (Maximum Allowable Blood Loss)
        
        MABL 用於術前評估，決定何時需要輸血。
        
        公式: MABL = EBV × (Hi - Hf) / Havg
        
        Args:
            weight_kg: 體重 (公斤)
            initial_hematocrit: 術前血球容積比 (%)
            target_hematocrit: 目標/最低可接受血球容積比 (%)
            patient_type: 病患類型
                - preterm_neonate: 早產兒 (EBV 90 mL/kg)
                - term_neonate: 足月新生兒 (EBV 85 mL/kg)
                - infant: 嬰兒 (EBV 80 mL/kg)
                - child: 兒童 (EBV 75 mL/kg)
                - adult_male: 成年男性 (EBV 70 mL/kg)
                - adult_female: 成年女性 (EBV 65 mL/kg)
                
        Returns:
            MABL (mL)、EBV、允許失血百分比和輸血建議
            
        Reference:
            Miller's Anesthesia, 9th ed, Chapter 49
            Gross JB. Anesthesiology 1983;58(3):277-280
        """
        request = CalculateRequest(
            tool_id="mabl",
            params={
                "weight_kg": weight_kg,
                "initial_hematocrit": initial_hematocrit,
                "target_hematocrit": target_hematocrit,
                "patient_type": patient_type,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
    
    @mcp.tool()
    def calculate_transfusion_volume(
        weight_kg: float,
        product_type: str = "prbc",
        patient_type: str = "adult_male",
        current_hematocrit: Optional[float] = None,
        target_hematocrit: Optional[float] = None,
        current_hemoglobin: Optional[float] = None,
        target_hemoglobin: Optional[float] = None,
        current_platelet: Optional[float] = None,
        target_platelet: Optional[float] = None,
    ) -> dict[str, Any]:
        """
        輸血量計算器
        
        計算達到目標 Hct/Hgb/Plt 所需的血品量。
        
        Args:
            weight_kg: 體重 (公斤)
            product_type: 血品類型
                - prbc: 濃縮紅血球
                - whole_blood: 全血
                - platelets: 分離術血小板
                - platelet_concentrate: 濃縮血小板
                - ffp: 新鮮冷凍血漿
                - cryoprecipitate: 冷凍沉澱品
            patient_type: 病患類型 (用於計算 EBV)
            current_hematocrit: 目前 Hct (%)
            target_hematocrit: 目標 Hct (%)
            current_hemoglobin: 目前 Hgb (g/dL) - 替代 Hct
            target_hemoglobin: 目標 Hgb (g/dL)
            current_platelet: 目前血小板 (×10⁹/L)
            target_platelet: 目標血小板 (×10⁹/L)
            
        Returns:
            所需輸血量 (mL)、血品單位數、預期上升值
            
        References:
            Roseff SD, et al. Transfusion. 2002.
            New HV, et al. Br J Haematol. 2016.
        """
        request = CalculateRequest(
            tool_id="transfusion_calc",
            params={
                "weight_kg": weight_kg,
                "product_type": product_type,
                "patient_type": patient_type,
                "current_hematocrit": current_hematocrit,
                "target_hematocrit": target_hematocrit,
                "current_hemoglobin": current_hemoglobin,
                "target_hemoglobin": target_hemoglobin,
                "current_platelet": current_platelet,
                "target_platelet": target_platelet,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
