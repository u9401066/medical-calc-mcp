"""
Nephrology Calculator Tools

MCP tool handlers for nephrology calculators.
Uses Annotated + Field for rich parameter descriptions in JSON Schema.
"""

from typing import Annotated, Any, Literal, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_nephrology_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all nephrology calculator tools with MCP"""

    @mcp.tool()
    def calculate_ckd_epi_2021(
        serum_creatinine: Annotated[float, Field(gt=0, le=20.0, description="血清肌酐 Serum creatinine | Unit: mg/dL | Range: 0.1-20.0")],
        age: Annotated[int, Field(ge=18, le=120, description="年齡 Age | Unit: years | Range: 18-120")],
        sex: Annotated[Literal["male", "female"], Field(description="性別 Sex | Options: 'male' or 'female'")],
    ) -> dict[str, Any]:
        """
        計算 CKD-EPI 2021 eGFR (腎絲球過濾率)

        Race-free equation. Returns eGFR in mL/min/1.73m².
        G1≥90, G2:60-89, G3a:45-59, G3b:30-44, G4:15-29, G5<15.

        Reference: Inker LA, et al. NEJM 2021.
        """
        request = CalculateRequest(tool_id="ckd_epi_2021", params={"serum_creatinine": serum_creatinine, "age": age, "sex": sex})
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_kdigo_aki(
        current_creatinine: Annotated[float, Field(gt=0, description="目前血清肌酸酐 Current serum creatinine (mg/dL)")],
        baseline_creatinine: Annotated[Optional[float], Field(default=None, description="基準肌酸酐 Baseline creatinine (mg/dL), if known")] = None,
        creatinine_increase_48h: Annotated[Optional[float], Field(default=None, description="48小時內肌酸酐上升量 Absolute Cr increase in 48h (mg/dL)")] = None,
        urine_output_ml_kg_h: Annotated[Optional[float], Field(default=None, description="尿量 Average urine output (mL/kg/hour)")] = None,
        urine_output_duration_hours: Annotated[Optional[float], Field(default=None, description="尿量減少持續時間 Duration of reduced UO (hours)")] = None,
        on_rrt: Annotated[bool, Field(description="是否接受腎臟替代療法 On RRT (dialysis/CRRT)? Auto Stage 3")] = False,
    ) -> dict[str, Any]:
        """
        🫀 KDIGO AKI Staging: 急性腎損傷分期

        根據 KDIGO 標準分類急性腎損傷 (AKI) 的嚴重程度。

        **AKI 診斷標準 (符合任一):**
        - 48小時內血清肌酸酐上升 ≥0.3 mg/dL
        - 7天內血清肌酸酐上升至基準值 ≥1.5倍
        - 尿量 <0.5 mL/kg/h 持續 6小時

        **KDIGO AKI 分期:**

        | 分期 | 肌酸酐標準 | 尿量標準 |
        |------|-----------|---------|
        | 1 | 1.5-1.9倍基準 或 ≥0.3 mg/dL↑ | <0.5 mL/kg/h × 6-12h |
        | 2 | 2.0-2.9倍基準 | <0.5 mL/kg/h × ≥12h |
        | 3 | ≥3.0倍基準 或 ≥4.0 mg/dL 或 RRT | <0.3 mL/kg/h × ≥24h 或 無尿 ≥12h |

        **臨床意義:**
        - Stage 1: 輕度 AKI - 密切監測，找出並治療病因
        - Stage 2: 中度 AKI - 積極處理，會診腎臟科
        - Stage 3: 重度 AKI - 高死亡率，可能需要透析

        **參考文獻:**
        - KDIGO AKI Work Group. Kidney Int Suppl. 2012;2(1):1-138.
        - Kellum JA, et al. Crit Care. 2013;17(1):204. PMID: 23394211

        Returns:
            KDIGO AKI 分期 (0-3)、處置建議
        """
        request = CalculateRequest(
            tool_id="kdigo_aki",
            params={
                "current_creatinine": current_creatinine,
                "baseline_creatinine": baseline_creatinine,
                "creatinine_increase_48h": creatinine_increase_48h,
                "urine_output_ml_kg_h": urine_output_ml_kg_h,
                "urine_output_duration_hours": urine_output_duration_hours,
                "on_rrt": on_rrt,
            },
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_fena(
        urine_sodium: Annotated[float, Field(ge=0, le=300, description="尿液鈉 Urine sodium (mEq/L) | Range: 0-300")],
        plasma_sodium: Annotated[float, Field(ge=100, le=180, description="血漿鈉 Plasma/serum sodium (mEq/L) | Range: 100-180")],
        urine_creatinine: Annotated[float, Field(gt=0, le=500, description="尿液肌酸酐 Urine creatinine (mg/dL) | Range: 0-500")],
        plasma_creatinine: Annotated[float, Field(gt=0, le=30, description="血漿肌酸酐 Plasma/serum creatinine (mg/dL) | Range: 0-30")],
        on_diuretics: Annotated[bool, Field(description="是否使用利尿劑 On diuretics? (affects interpretation reliability)")] = False,
    ) -> dict[str, Any]:
        """
        🔬 FENa: 鈉排泄分數 (Fractional Excretion of Sodium)

        FENa 用於區分急性腎損傷 (AKI) 的病因：前腎性氮血症 vs 急性腎小管壞死 (ATN)。

        **公式:**
        FENa (%) = (尿鈉 × 血肌酐) / (血鈉 × 尿肌酐) × 100

        **解讀:**

        | FENa | 可能病因 | 腎臟狀態 |
        |------|---------|---------|
        | <1% | 前腎性氮血症 | 腎臟正常保鈉 |
        | 1-2% | 不確定 | 可能為過渡期 |
        | >2% | 腎實質性 (ATN) | 腎小管受損無法保鈉 |

        **注意事項:**
        - 利尿劑會增加 FENa，造成結果不可靠
        - 使用利尿劑時，建議改用 FEUrea (尿素排泄分數)
        - FENa <1% 也可見於：對比劑腎病變、橫紋肌溶解症、早期阻塞性腎病、急性腎絲球腎炎

        **參考文獻:**
        - Espinel CH. JAMA. 1976;236(6):579-581. PMID: 947239
        - Miller TR, et al. Ann Intern Med. 1978;89(1):47-50. PMID: 666184

        Returns:
            FENa 百分比與臨床解讀
        """
        request = CalculateRequest(
            tool_id="fena",
            params={
                "urine_sodium": urine_sodium,
                "plasma_sodium": plasma_sodium,
                "urine_creatinine": urine_creatinine,
                "plasma_creatinine": plasma_creatinine,
                "on_diuretics": on_diuretics,
            },
        )
        response = use_case.execute(request)
        return response.to_dict()
