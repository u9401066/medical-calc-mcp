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
# Phase 4: ICU/Emergency Calculators
# =============================================================================

@mcp.tool()
def calculate_sofa(
    pao2_fio2_ratio: float,
    platelets: float,
    bilirubin: float,
    gcs_score: int,
    creatinine: float,
    map_value: float | None = None,
    dopamine_dose: float | None = None,
    dobutamine_any: bool = False,
    epinephrine_dose: float | None = None,
    norepinephrine_dose: float | None = None,
    is_mechanically_ventilated: bool = False,
    urine_output_24h: float | None = None,
) -> dict[str, Any]:
    """
    計算 SOFA 分數 (Sequential Organ Failure Assessment)
    
    SOFA 評估六個器官系統功能，是 Sepsis-3 診斷標準的核心。
    SOFA ≥2 分在懷疑感染時符合敗血症定義。
    
    Args:
        pao2_fio2_ratio: PaO2/FiO2 比值 (mmHg)
        platelets: 血小板計數 (×10³/µL)
        bilirubin: 總膽紅素 (mg/dL)
        gcs_score: 格拉斯哥昏迷指數 (3-15)
        creatinine: 血清肌酐 (mg/dL)
        map_value: 平均動脈壓 (mmHg)，無血管加壓藥時使用
        dopamine_dose: Dopamine 劑量 (µg/kg/min)
        dobutamine_any: 是否使用 Dobutamine
        epinephrine_dose: Epinephrine 劑量 (µg/kg/min)
        norepinephrine_dose: Norepinephrine 劑量 (µg/kg/min)
        is_mechanically_ventilated: 是否使用機械通氣
        urine_output_24h: 24 小時尿量 (mL)
        
    Returns:
        SOFA 分數 (0-24)、各器官分數、死亡率預測
        
    References:
        Vincent JL, et al. Intensive Care Med. 1996;22(7):707-710.
        Singer M, et al. JAMA. 2016;315(8):801-810. (Sepsis-3)
    """
    calc = calculator_instances["sofa_score"]
    result = calc.calculate(
        pao2_fio2_ratio=pao2_fio2_ratio,
        platelets=platelets,
        bilirubin=bilirubin,
        gcs_score=gcs_score,
        creatinine=creatinine,
        map_value=map_value,
        dopamine_dose=dopamine_dose,
        dobutamine_any=dobutamine_any,
        epinephrine_dose=epinephrine_dose,
        norepinephrine_dose=norepinephrine_dose,
        is_mechanically_ventilated=is_mechanically_ventilated,
        urine_output_24h=urine_output_24h,
    )
    return result.to_mcp_response()


@mcp.tool()
def calculate_qsofa(
    respiratory_rate: int,
    systolic_bp: int,
    altered_mentation: bool = False,
    gcs_score: int = 15,
) -> dict[str, Any]:
    """
    計算 qSOFA 分數 (Quick SOFA)
    
    qSOFA 是一個快速床邊評估工具，用於識別感染風險較高的病患。
    注意：依據 SSC 2021 指引，不建議單獨使用 qSOFA 作為敗血症篩檢工具。
    
    Args:
        respiratory_rate: 呼吸速率 (次/分)
        systolic_bp: 收縮壓 (mmHg)
        altered_mentation: 意識改變 (GCS <15 或急性意識變化)
        gcs_score: GCS 分數 (3-15)，若未指定 altered_mentation 則使用
        
    Returns:
        qSOFA 分數 (0-3) 和風險評估
        
    References:
        Singer M, et al. JAMA. 2016;315(8):801-810. (Sepsis-3)
        SSC 2021: 強烈建議不單獨使用 qSOFA 作為篩檢工具
    """
    calc = calculator_instances["qsofa_score"]
    result = calc.calculate(
        respiratory_rate=respiratory_rate,
        systolic_bp=systolic_bp,
        altered_mentation=altered_mentation,
        gcs_score=gcs_score,
    )
    return result.to_mcp_response()


@mcp.tool()
def calculate_news2(
    respiratory_rate: int,
    spo2: int,
    on_supplemental_o2: bool,
    temperature: float,
    systolic_bp: int,
    heart_rate: int,
    consciousness: str = "A",
    use_scale_2: bool = False,
) -> dict[str, Any]:
    """
    計算 NEWS2 分數 (National Early Warning Score 2)
    
    NEWS2 用於偵測住院病患的臨床惡化，觸發適當的臨床反應。
    
    Args:
        respiratory_rate: 呼吸速率 (次/分)
        spo2: 血氧飽和度 (%)
        on_supplemental_o2: 是否使用氧氣
        temperature: 體溫 (°C)
        systolic_bp: 收縮壓 (mmHg)
        heart_rate: 心率 (次/分)
        consciousness: AVPU 意識狀態
            A = Alert (清醒)
            V = Voice (對聲音有反應)
            P = Pain (對疼痛有反應)
            U = Unresponsive (無反應)
            C = Confusion (意識混亂)
        use_scale_2: 是否使用 Scale 2（用於高碳酸血症呼吸衰竭，目標 SpO2 88-92%）
        
    Returns:
        NEWS2 分數 (0-20) 和臨床反應建議
        
    Reference:
        Royal College of Physicians. NEWS2, 2017.
    """
    calc = calculator_instances["news2_score"]
    result = calc.calculate(
        respiratory_rate=respiratory_rate,
        spo2=spo2,
        on_supplemental_o2=on_supplemental_o2,
        temperature=temperature,
        systolic_bp=systolic_bp,
        heart_rate=heart_rate,
        consciousness=consciousness,
        use_scale_2=use_scale_2,
    )
    return result.to_mcp_response()


@mcp.tool()
def calculate_gcs(
    eye_response: int,
    verbal_response: int,
    motor_response: int,
    is_intubated: bool = False,
) -> dict[str, Any]:
    """
    計算 GCS 分數 (Glasgow Coma Scale)
    
    GCS 評估意識程度，是最廣泛使用的昏迷量表。
    
    Args:
        eye_response: 眼睛反應 (1-4)
            1 = 無反應
            2 = 對疼痛有反應
            3 = 對聲音有反應
            4 = 自發性睜眼
        verbal_response: 語言反應 (1-5)
            1 = 無反應
            2 = 無法理解的聲音
            3 = 不恰當的言語
            4 = 混亂但可對話
            5 = 定向力正常
        motor_response: 運動反應 (1-6)
            1 = 無反應
            2 = 伸展姿勢（去腦強直）
            3 = 屈曲姿勢（去皮質強直）
            4 = 退縮反應
            5 = 定位疼痛
            6 = 服從命令
        is_intubated: 是否已插管（無法評估語言反應）
        
    Returns:
        GCS 分數 (3-15) 和腦傷嚴重度分級
        
    Reference:
        Teasdale G, Jennett B. Lancet. 1974;2(7872):81-84.
    """
    calc = calculator_instances["glasgow_coma_scale"]
    result = calc.calculate(
        eye_response=eye_response,
        verbal_response=verbal_response,
        motor_response=motor_response,
        is_intubated=is_intubated,
    )
    return result.to_mcp_response()


@mcp.tool()
def calculate_cam_icu(
    rass_score: int,
    acute_onset_fluctuation: bool,
    inattention_score: int,
    altered_loc: bool = False,
    disorganized_thinking_errors: int = 0,
) -> dict[str, Any]:
    """
    計算 CAM-ICU (Confusion Assessment Method for ICU)
    
    CAM-ICU 是 ICU 病患譫妄篩檢的標準工具。
    
    Args:
        rass_score: RASS 分數 (-5 到 +4)
            若 RASS ≤ -4，病患昏迷，無法評估 CAM-ICU
        acute_onset_fluctuation: Feature 1 - 急性發作或波動病程
        inattention_score: Feature 2 - ASE 注意力測試錯誤數 (≥3 為不專注)
        altered_loc: Feature 3 - 意識程度改變 (RASS ≠ 0)
        disorganized_thinking_errors: Feature 4 - 思維障礙測試錯誤數 (≥2 為陽性)
        
    Returns:
        CAM-ICU 結果（陽性/陰性/無法評估）和建議
        
    References:
        Ely EW, et al. JAMA. 2001;286(21):2703-2710.
        PADIS Guidelines: Crit Care Med. 2018;46(9):e825-e873.
    """
    calc = calculator_instances["cam_icu"]
    result = calc.calculate(
        rass_score=rass_score,
        acute_onset_fluctuation=acute_onset_fluctuation,
        inattention_score=inattention_score,
        altered_loc=altered_loc,
        disorganized_thinking_errors=disorganized_thinking_errors,
    )
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
