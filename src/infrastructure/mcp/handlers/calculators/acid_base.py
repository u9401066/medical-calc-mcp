"""
Acid-Base & Electrolyte Calculator Tools

MCP tool handlers for acid-base and electrolyte calculators.
Uses Annotated + Field for rich parameter descriptions in JSON Schema.
"""

from typing import Any, Annotated, Optional, Literal

from pydantic import Field
from mcp.server.fastmcp import FastMCP

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_acid_base_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all acid-base and electrolyte calculator tools with MCP"""
    
    @mcp.tool()
    def calculate_anion_gap(
        sodium: Annotated[
            float,
            Field(ge=120, le=160, description="血清鈉 Serum sodium | Unit: mEq/L | Range: 120-160")
        ],
        chloride: Annotated[
            float,
            Field(ge=80, le=120, description="血清氯 Serum chloride | Unit: mEq/L | Range: 80-120")
        ],
        bicarbonate: Annotated[
            float,
            Field(ge=5, le=40, description="血清碳酸氫鹽 Serum bicarbonate (HCO₃⁻) | Unit: mEq/L | Range: 5-40")
        ],
        albumin: Annotated[
            Optional[float],
            Field(default=None, ge=0.5, le=6.0, description="血清白蛋白 Serum albumin (optional, for corrected AG) | Unit: g/dL | Range: 0.5-6.0")
        ] = None,
        include_potassium: Annotated[
            bool,
            Field(default=False, description="是否包含鉀 Include K⁺ in calculation (rarely used)")
        ] = False,
        potassium: Annotated[
            Optional[float],
            Field(default=None, ge=2.0, le=8.0, description="血清鉀 Serum potassium (if including K⁺) | Unit: mEq/L | Range: 2.0-8.0")
        ] = None,
    ) -> dict[str, Any]:
        """
        🧪 Anion Gap: 陰離子間隙計算
        
        計算血清陰離子間隙，用於代謝性酸中毒的鑑別診斷。
        
        **公式:**
        - AG = Na⁺ - (Cl⁻ + HCO₃⁻)
        - 校正 AG = AG + 2.5 × (4.0 - Albumin)
        
        **正常範圍:** 8-12 mEq/L (不含 K⁺)
        
        **高陰離子間隙酸中毒 (HAGMA) 病因 - MUDPILES:**
        - **M**ethanol (甲醇)
        - **U**remia (尿毒症)
        - **D**KA/Ketoacidosis (酮酸中毒)
        - **P**ropylene glycol (丙二醇)
        - **I**NH/Iron (異煙肼/鐵中毒)
        - **L**actic acidosis (乳酸酸中毒)
        - **E**thylene glycol (乙二醇)
        - **S**alicylates (水楊酸鹽)
        
        **正常陰離子間隙酸中毒 (NAGMA):**
        - GI HCO₃⁻ loss (腹瀉)
        - Renal tubular acidosis (腎小管酸中毒)
        - Dilutional acidosis (稀釋性酸中毒)
        
        **參考文獻:**
        - Kraut JA, Madias NE. Clin J Am Soc Nephrol. 2007;2(1):162-174. PMID: 17699401
        - Figge J, et al. Crit Care Med. 1998;26(11):1807-1810. PMID: 9824071
        
        Returns:
            Anion Gap (mEq/L)、校正 AG (如提供白蛋白)、鑑別診斷建議
        """
        request = CalculateRequest(
            tool_id="anion_gap",
            params={
                "sodium": sodium,
                "chloride": chloride,
                "bicarbonate": bicarbonate,
                "albumin": albumin,
                "include_potassium": include_potassium,
                "potassium": potassium,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_delta_ratio(
        anion_gap: Annotated[
            float,
            Field(ge=0, le=50, description="陰離子間隙 Measured anion gap (use corrected AG if available) | Unit: mEq/L | Range: 0-50")
        ],
        bicarbonate: Annotated[
            float,
            Field(ge=5, le=40, description="血清碳酸氫鹽 Measured serum bicarbonate | Unit: mEq/L | Range: 5-40")
        ],
        normal_ag: Annotated[
            float,
            Field(default=12.0, ge=6, le=14, description="正常陰離子間隙基準值 Normal AG baseline | Unit: mEq/L | Default: 12")
        ] = 12.0,
        normal_hco3: Annotated[
            float,
            Field(default=24.0, ge=22, le=26, description="正常碳酸氫鹽基準值 Normal HCO₃⁻ baseline | Unit: mEq/L | Default: 24")
        ] = 24.0,
    ) -> dict[str, Any]:
        """
        🔬 Delta Ratio (Delta Gap): 混合型酸鹼障礙鑑別
        
        用於識別高陰離子間隙代謝性酸中毒 (HAGMA) 患者是否合併其他酸鹼障礙。
        
        **公式:**
        - ΔAG = 測量 AG - 正常 AG (12)
        - ΔHCO₃⁻ = 正常 HCO₃⁻ (24) - 測量 HCO₃⁻
        - Delta Ratio = ΔAG / ΔHCO₃⁻
        
        **判讀:**
        
        | Delta Ratio | 診斷 | 說明 |
        |-------------|------|------|
        | <1 | HAGMA + NAGMA | HCO₃⁻下降 > AG上升 |
        | 1-2 | 純粹 HAGMA | AG上升 ≈ HCO₃⁻下降 |
        | >2 | HAGMA + 代謝性鹼中毒 | AG上升 > HCO₃⁻下降 |
        
        **臨床應用:**
        - 只有在 AG 升高 (HAGMA) 時才有意義
        - 幫助識別複雜的混合型酸鹼障礙
        
        **參考文獻:**
        - Wrenn K. Ann Emerg Med. 1990;19(11):1310-1313. PMID: 2240729
        - Rastegar A. J Am Soc Nephrol. 2007;18(9):2429-2431. PMID: 17656478
        
        Returns:
            Delta Ratio、混合型酸鹼障礙診斷、下一步建議
        """
        request = CalculateRequest(
            tool_id="delta_ratio",
            params={
                "anion_gap": anion_gap,
                "bicarbonate": bicarbonate,
                "normal_ag": normal_ag,
                "normal_hco3": normal_hco3,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_corrected_sodium(
        measured_sodium: Annotated[
            float,
            Field(ge=100, le=180, description="測量血鈉 Measured serum sodium | Unit: mEq/L | Range: 100-180")
        ],
        glucose: Annotated[
            float,
            Field(gt=0, description="血糖 Blood glucose level | Unit: mg/dL or mmol/L")
        ],
        formula: Annotated[
            Literal["katz", "hillier"],
            Field(default="katz", description="校正公式 Formula: 'katz' (1.6 factor, standard) or 'hillier' (2.4 factor, for very high glucose)")
        ] = "katz",
        glucose_unit: Annotated[
            Literal["mg/dL", "mmol/L"],
            Field(default="mg/dL", description="血糖單位 Glucose unit: 'mg/dL' or 'mmol/L'")
        ] = "mg/dL",
    ) -> dict[str, Any]:
        """
        🩸 Corrected Sodium: 高血糖校正血鈉
        
        計算高血糖患者的真實血鈉水平。高血糖造成水分從細胞內移至細胞外，
        稀釋血鈉，產生「假性低血鈉」。
        
        **公式:**
        - **Katz (1973)**: 校正 Na = 測量 Na + 1.6 × ((血糖 - 100) / 100)
        - **Hillier (1999)**: 校正 Na = 測量 Na + 2.4 × ((血糖 - 100) / 100)
        
        **何時使用:**
        - 糖尿病酮酸中毒 (DKA)
        - 高血糖高滲狀態 (HHS)
        - 任何顯著高血糖 (>200 mg/dL)
        
        **公式選擇:**
        - Katz: 標準公式，最常用
        - Hillier: 血糖極高時 (>400 mg/dL) 可能更準確
        
        **臨床意義:**
        - 校正鈉正常: 低鈉主要由高血糖稀釋造成
        - 校正鈉仍低: 真正的低血鈉，需另外評估
        - 校正鈉高: 真正的高血鈉，嚴重脫水
        
        **參考文獻:**
        - Katz MA. N Engl J Med. 1973;289(16):843-844. PMID: 4763428
        - Hillier TA, et al. Am J Med. 1999;106(4):399-403. PMID: 10225241
        
        Returns:
            校正血鈉 (mEq/L)、校正量、臨床解釋
        """
        request = CalculateRequest(
            tool_id="corrected_sodium",
            params={
                "measured_sodium": measured_sodium,
                "glucose": glucose,
                "formula": formula,
                "glucose_unit": glucose_unit,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
