"""
Pediatric & Anesthesia Calculator Tools

MCP tool handlers for pediatric and anesthesia calculators.
Uses Annotated + Field for rich parameter descriptions in JSON Schema.
"""

from typing import Any, Optional, Annotated

from pydantic import Field
from mcp.server.fastmcp import FastMCP

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_pediatric_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all pediatric and anesthesia calculator tools with MCP"""
    
    @mcp.tool()
    def calculate_pediatric_drug_dose(
        drug_name: Annotated[str, Field(description="藥物: acetaminophen, ibuprofen, amoxicillin, ceftriaxone, ondansetron, morphine, fentanyl, ketamine")],
        weight_kg: Annotated[float, Field(description="體重 Weight kg (0.5-150)")],
        route: Annotated[str, Field(description="給藥途徑: iv, po, im, pr", default="iv")],
        indication: Annotated[Optional[str], Field(description="適應症 (may affect dose)", default=None)],
    ) -> dict[str, Any]:
        """
        小兒藥物劑量計算器 (Pediatric Drug Dosing)
        
        Weight-based dosing with safety limits.
        ⚠️ Always verify: dose≤max, age-appropriate, interactions.
        
        References: Lexicomp Pediatric Handbook, Nelson Textbook.
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
        weight_kg: Annotated[float, Field(description="體重 Weight kg (0.5-200)")],
        initial_hematocrit: Annotated[float, Field(description="術前Hct Initial hematocrit % (20-60)")],
        target_hematocrit: Annotated[float, Field(description="目標Hct Min acceptable hematocrit % (15-40)")],
        patient_type: Annotated[str, Field(description="病患: preterm_neonate(90), term_neonate(85), infant(80), child(75), adult_male(70), adult_female(65)", default="adult_male")],
    ) -> dict[str, Any]:
        """
        計算 MABL 最大允許失血量 (Maximum Allowable Blood Loss)
        
        Formula: MABL = EBV × (Hi - Hf) / Havg
        EBV varies by patient type (mL/kg in parentheses).
        
        Reference: Miller's Anesthesia 9th ed.
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
        weight_kg: Annotated[float, Field(description="體重 Weight kg (0.5-200)")],
        product_type: Annotated[str, Field(description="血品: prbc, whole_blood, platelets, platelet_concentrate, ffp, cryoprecipitate", default="prbc")],
        patient_type: Annotated[str, Field(description="病患類型 for EBV calculation", default="adult_male")],
        current_hematocrit: Annotated[Optional[float], Field(description="目前Hct Current hematocrit %", default=None)],
        target_hematocrit: Annotated[Optional[float], Field(description="目標Hct Target hematocrit %", default=None)],
        current_hemoglobin: Annotated[Optional[float], Field(description="目前Hgb Current hemoglobin g/dL", default=None)],
        target_hemoglobin: Annotated[Optional[float], Field(description="目標Hgb Target hemoglobin g/dL", default=None)],
        current_platelet: Annotated[Optional[float], Field(description="目前血小板 Current platelet ×10⁹/L", default=None)],
        target_platelet: Annotated[Optional[float], Field(description="目標血小板 Target platelet ×10⁹/L", default=None)],
    ) -> dict[str, Any]:
        """
        輸血量計算器 (Transfusion Volume Calculator)
        
        Calculate blood product volume for target Hct/Hgb/Plt.
        pRBC: 10-15mL/kg raises Hgb ~2-3 g/dL.
        
        References: Roseff 2002, New 2016.
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
