"""
Medical Calculator MCP Server

A Model Context Protocol server providing medical calculators with intelligent
tool discovery for AI agents.

Usage:
    # Development mode
    uv run mcp dev src/infrastructure/mcp/server.py
    
    # Direct execution (stdio)
    python -m src.infrastructure.mcp.server
    
    # HTTP transport
    python -m src.infrastructure.mcp.server --transport http
"""

from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from ...domain.registry.tool_registry import ToolRegistry
from ...domain.services.calculators import (
    CALCULATORS,
    ApacheIiCalculator,
    AsaPhysicalStatusCalculator,
    CkdEpi2021Calculator,
    MallampatiScoreCalculator,
    RassCalculator,
    RcriCalculator,
)


# Create MCP server instance
mcp = FastMCP(
    name="Medical Calculator MCP",
    json_response=True,
    instructions="""
    Medical Calculator MCP Server - 醫學計算工具 MCP 伺服器
    
    This server provides validated medical calculators with:
    - Tool Discovery: Search by specialty, condition, or clinical question
    - Calculators: Execute specific medical calculations
    - References: All tools cite original peer-reviewed papers
    
    使用方式：
    1. 使用 discover_tools 搜尋適合的工具
    2. 使用 list_calculators 查看所有可用計算器
    3. 呼叫特定計算器（如 calculate_ckd_epi_2021）
    """
)


# Initialize registry and register all calculators
registry = ToolRegistry()
calculator_instances: dict[str, Any] = {}

for calculator_cls in CALCULATORS:
    instance = calculator_cls()
    registry.register(instance)
    calculator_instances[instance.tool_id] = instance


# =============================================================================
# Discovery Tools
# =============================================================================

class DiscoveryQuery(BaseModel):
    """Query parameters for tool discovery"""
    query: str = Field(description="搜尋關鍵字、臨床問題或專科名稱")
    limit: int = Field(default=10, description="最多回傳幾個結果")


@mcp.tool()
def discover_tools(query: str, limit: int = 10) -> dict[str, Any]:
    """
    搜尋醫學計算工具
    
    Search for medical calculators by:
    - Clinical question (e.g., "What is the cardiac risk?")
    - Specialty (e.g., "anesthesiology", "nephrology")  
    - Condition (e.g., "difficult airway", "CKD")
    - Keywords (e.g., "eGFR", "ASA", "Mallampati")
    
    Args:
        query: 搜尋關鍵字、臨床問題或專科名稱
        limit: 最多回傳幾個結果 (預設 10)
        
    Returns:
        匹配的計算工具清單，包含 tool_id, name, purpose
    """
    results = registry.search(query, limit=limit)
    
    return {
        "query": query,
        "count": len(results),
        "tools": [
            {
                "tool_id": r.low_level.tool_id,
                "name": r.low_level.name,
                "purpose": r.low_level.purpose,
                "specialties": [s.value for s in r.high_level.specialties],
                "input_params": r.low_level.input_params,
            }
            for r in results
        ]
    }


@mcp.tool()
def list_calculators() -> dict[str, Any]:
    """
    列出所有可用的醫學計算工具
    
    List all available medical calculators with their metadata.
    
    Returns:
        所有計算器的清單，包含 tool_id, name, purpose, specialties
    """
    all_tools = registry.list_all()
    
    return {
        "count": len(all_tools),
        "calculators": [
            {
                "tool_id": meta.low_level.tool_id,
                "name": meta.low_level.name,
                "purpose": meta.low_level.purpose,
                "specialties": [s.value for s in meta.high_level.specialties],
                "input_params": meta.low_level.input_params,
                "output_type": meta.low_level.output_type,
            }
            for meta in all_tools
        ]
    }


@mcp.tool()
def get_calculator_info(tool_id: str) -> dict[str, Any]:
    """
    取得特定計算器的詳細資訊
    
    Get detailed information about a specific calculator including:
    - Input parameters and their descriptions
    - Clinical contexts and conditions
    - Paper references
    
    Args:
        tool_id: 計算器 ID (e.g., "ckd_epi_2021", "asa_physical_status")
        
    Returns:
        計算器的完整 metadata 和使用說明
    """
    metadata = registry.get(tool_id)
    if metadata is None:
        return {
            "error": f"Calculator '{tool_id}' not found",
            "available": [m.low_level.tool_id for m in registry.list_all()]
        }
    
    return {
        "tool_id": metadata.low_level.tool_id,
        "name": metadata.low_level.name,
        "purpose": metadata.low_level.purpose,
        "input_params": metadata.low_level.input_params,
        "output_type": metadata.low_level.output_type,
        "specialties": [s.value for s in metadata.high_level.specialties],
        "conditions": list(metadata.high_level.conditions),
        "clinical_contexts": [c.value for c in metadata.high_level.clinical_contexts],
        "clinical_questions": list(metadata.high_level.clinical_questions),
        "keywords": list(metadata.high_level.keywords),
        "references": [
            {
                "citation": ref.citation,
                "doi": ref.doi,
                "pmid": ref.pmid,
                "year": ref.year,
            }
            for ref in metadata.references
        ],
        "version": metadata.version,
    }


# =============================================================================
# Calculator Tools
# =============================================================================

@mcp.tool()
def calculate_ckd_epi_2021(
    serum_creatinine: float,
    age: int,
    sex: str
) -> dict[str, Any]:
    """
    計算 CKD-EPI 2021 eGFR (腎絲球過濾率)
    
    Calculate estimated GFR using the 2021 CKD-EPI equation (race-free).
    
    Args:
        serum_creatinine: 血清肌酐值 (mg/dL)
        age: 年齡 (歲, 18-120)
        sex: 性別 ("male" 或 "female")
        
    Returns:
        eGFR 值、CKD 分期、臨床解讀和建議
        
    Reference:
        Inker LA, et al. N Engl J Med. 2021;385(19):1737-1749.
    """
    calc = calculator_instances["ckd_epi_2021"]
    result = calc.calculate(
        serum_creatinine=serum_creatinine,
        age=age,
        sex=sex
    )
    return result.to_mcp_response()


@mcp.tool()
def calculate_asa_physical_status(
    asa_class: int,
    is_emergency: bool = False
) -> dict[str, Any]:
    """
    ASA 身體狀態分級
    
    Classify patient using ASA Physical Status Classification (I-VI).
    
    Args:
        asa_class: ASA 分級 (1-6)
            1: 健康病人
            2: 輕度全身性疾病
            3: 嚴重全身性疾病
            4: 持續威脅生命的嚴重全身性疾病
            5: 瀕死病人，不手術無法存活
            6: 腦死器官捐贈者
        is_emergency: 是否為緊急手術 (加 E 字尾)
        
    Returns:
        ASA 分級、描述、周術期死亡率風險估計
        
    Reference:
        Mayhew D, et al. Anaesthesia. 2019;74(3):373-379.
    """
    calc = calculator_instances["asa_physical_status"]
    result = calc.calculate(asa_class=asa_class, is_emergency=is_emergency)
    return result.to_mcp_response()


@mcp.tool()
def calculate_mallampati(mallampati_class: int) -> dict[str, Any]:
    """
    Mallampati 氣道評估分級
    
    Predict difficult intubation using Modified Mallampati Classification.
    
    Args:
        mallampati_class: Mallampati 分級 (1-4)
            1: 可見軟顎、懸雍垂、咽門弓
            2: 可見軟顎、懸雍垂
            3: 可見軟顎、懸雍垂基部
            4: 只可見硬顎
            
    Returns:
        分級、困難插管風險評估、建議
        
    Reference:
        Mallampati SR, et al. Can Anaesth Soc J. 1985;32(4):429-434.
    """
    calc = calculator_instances["mallampati_score"]
    result = calc.calculate(mallampati_class=mallampati_class)
    return result.to_mcp_response()


@mcp.tool()
def calculate_rcri(
    high_risk_surgery: bool = False,
    ischemic_heart_disease: bool = False,
    heart_failure: bool = False,
    cerebrovascular_disease: bool = False,
    insulin_diabetes: bool = False,
    creatinine_above_2: bool = False
) -> dict[str, Any]:
    """
    計算 RCRI 心臟風險指數 (Lee Index)
    
    Estimate risk of major cardiac complications after non-cardiac surgery.
    
    Args:
        high_risk_surgery: 高風險手術（腹腔內、胸腔內、主動脈上血管手術）
        ischemic_heart_disease: 缺血性心臟病史
        heart_failure: 心衰竭病史
        cerebrovascular_disease: 腦血管疾病史
        insulin_diabetes: 需胰島素治療的糖尿病
        creatinine_above_2: 肌酐 >2 mg/dL
        
    Returns:
        RCRI 分數 (0-6)、心臟併發症風險百分比、建議
        
    Reference:
        Lee TH, et al. Circulation. 1999;100(10):1043-1049.
    """
    calc = calculator_instances["rcri"]
    result = calc.calculate(
        high_risk_surgery=high_risk_surgery,
        ischemic_heart_disease=ischemic_heart_disease,
        heart_failure=heart_failure,
        cerebrovascular_disease=cerebrovascular_disease,
        insulin_diabetes=insulin_diabetes,
        creatinine_above_2=creatinine_above_2
    )
    return result.to_mcp_response()


@mcp.tool()
def calculate_apache_ii(
    temperature: float,
    mean_arterial_pressure: float,
    heart_rate: float,
    respiratory_rate: float,
    fio2: float,
    arterial_ph: float = 7.40,
    serum_sodium: float = 140.0,
    serum_potassium: float = 4.0,
    serum_creatinine: float = 1.0,
    hematocrit: float = 40.0,
    wbc_count: float = 10.0,
    gcs_score: int = 15,
    age: int = 50,
    pao2: float | None = None,
    aado2: float | None = None,
    chronic_conditions: list[str] | None = None,
    admission_type: str = "nonoperative",
    acute_renal_failure: bool = False
) -> dict[str, Any]:
    """
    計算 APACHE II 分數 (ICU 嚴重度評估)
    
    Estimate ICU mortality based on acute physiology and chronic health.
    
    Args:
        temperature: 體溫 (°C)
        mean_arterial_pressure: 平均動脈壓 (mmHg)
        heart_rate: 心率 (bpm)
        respiratory_rate: 呼吸速率 (次/分)
        fio2: 吸入氧濃度 (0.21-1.0)
        arterial_ph: 動脈血 pH (預設 7.40)
        serum_sodium: 血鈉 (mEq/L, 預設 140)
        serum_potassium: 血鉀 (mEq/L, 預設 4.0)
        serum_creatinine: 血肌酐 (mg/dL, 預設 1.0)
        hematocrit: 血球容積比 (%, 預設 40)
        wbc_count: 白血球計數 (×10³/µL, 預設 10)
        gcs_score: 格拉斯哥昏迷指數 (3-15, 預設 15)
        age: 年齡 (歲)
        pao2: 動脈血氧分壓 (mmHg, FiO2<0.5 時使用)
        aado2: 肺泡-動脈氧分壓差 (mmHg, FiO2≥0.5 時使用)
        chronic_conditions: 慢性健康問題清單
        admission_type: 入院類型 (nonoperative/emergency_postoperative/elective_postoperative)
        acute_renal_failure: 是否有急性腎衰竭
        
    Returns:
        APACHE II 分數、預估死亡率、建議
        
    Reference:
        Knaus WA, et al. Crit Care Med. 1985;13(10):818-829.
    """
    calc = calculator_instances["apache_ii"]
    result = calc.calculate(
        temperature=temperature,
        mean_arterial_pressure=mean_arterial_pressure,
        heart_rate=heart_rate,
        respiratory_rate=respiratory_rate,
        fio2=fio2,
        arterial_ph=arterial_ph,
        serum_sodium=serum_sodium,
        serum_potassium=serum_potassium,
        serum_creatinine=serum_creatinine,
        hematocrit=hematocrit,
        wbc_count=wbc_count,
        gcs_score=gcs_score,
        age=age,
        pao2=pao2,
        aado2=aado2,
        chronic_health_conditions=tuple(chronic_conditions or []),
        admission_type=admission_type,
        acute_renal_failure=acute_renal_failure
    )
    return result.to_mcp_response()


@mcp.tool()
def calculate_rass(rass_score: int) -> dict[str, Any]:
    """
    RASS 鎮靜躁動評估量表
    
    Assess level of agitation or sedation in ICU patients.
    
    Args:
        rass_score: RASS 分數 (-5 到 +4)
            +4: 好鬥 (Combative)
            +3: 非常躁動 (Very agitated)
            +2: 躁動 (Agitated)
            +1: 不安 (Restless)
             0: 警醒平靜 (Alert and calm)
            -1: 嗜睡 (Drowsy)
            -2: 輕度鎮靜 (Light sedation)
            -3: 中度鎮靜 (Moderate sedation)
            -4: 深度鎮靜 (Deep sedation)
            -5: 無法喚醒 (Unarousable)
            
    Returns:
        RASS 解讀、鎮靜程度評估、建議
        
    Reference:
        Sessler CN, et al. Am J Respir Crit Care Med. 2002;166(10):1338-1344.
    """
    calc = calculator_instances["rass"]
    result = calc.calculate(rass_score=rass_score)
    return result.to_mcp_response()


# =============================================================================
# Resources
# =============================================================================

@mcp.resource("calculator://list")
def get_calculator_list() -> str:
    """Get list of all available calculators"""
    all_tools = registry.list_all()
    lines = ["# Available Medical Calculators\n"]
    for meta in all_tools:
        lines.append(f"- **{meta.low_level.name}** (`{meta.low_level.tool_id}`)")
        lines.append(f"  - Purpose: {meta.low_level.purpose}")
        lines.append(f"  - Specialties: {', '.join(s.value for s in meta.high_level.specialties)}")
        lines.append("")
    return "\n".join(lines)


@mcp.resource("calculator://{tool_id}/references")
def get_calculator_references(tool_id: str) -> str:
    """Get paper references for a specific calculator"""
    metadata = registry.get(tool_id)
    if metadata is None:
        return f"Calculator '{tool_id}' not found"
    
    lines = [f"# References for {metadata.low_level.name}\n"]
    for i, ref in enumerate(metadata.references, 1):
        lines.append(f"## Reference {i}")
        lines.append(f"**Citation:** {ref.citation}")
        if ref.doi:
            lines.append(f"**DOI:** https://doi.org/{ref.doi}")
        if ref.pmid:
            lines.append(f"**PubMed:** https://pubmed.ncbi.nlm.nih.gov/{ref.pmid}/")
        if ref.year:
            lines.append(f"**Year:** {ref.year}")
        lines.append("")
    return "\n".join(lines)


# =============================================================================
# Entry Point
# =============================================================================

def main():
    """Run the MCP server"""
    import sys
    
    transport = "stdio"
    if "--transport" in sys.argv:
        idx = sys.argv.index("--transport")
        if idx + 1 < len(sys.argv):
            transport = sys.argv[idx + 1]
    
    if transport == "http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
