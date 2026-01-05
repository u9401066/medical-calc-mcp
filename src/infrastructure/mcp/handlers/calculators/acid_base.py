"""
Acid-Base & Electrolyte Calculator Tools

MCP tool handlers for acid-base and electrolyte calculators.
Uses Annotated + Field for rich parameter descriptions in JSON Schema.
"""

from typing import Annotated, Any, Literal, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

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

    @mcp.tool()
    def calculate_winters_formula(
        hco3: Annotated[
            float,
            Field(ge=5, le=30, description="血清碳酸氫鹽 Serum bicarbonate | Unit: mEq/L | Range: 5-30")
        ],
        actual_paco2: Annotated[
            Optional[float],
            Field(default=None, ge=10, le=80, description="測量 PaCO₂ (optional) Measured arterial CO₂ for comparison | Unit: mmHg | Range: 10-80")
        ] = None,
    ) -> dict[str, Any]:
        """
        🫁 Winter's Formula: 代謝性酸中毒呼吸代償預測

        預測代謝性酸中毒患者的適當呼吸代償 (預期 PaCO₂)。

        **公式:**
        - 預期 PaCO₂ = (1.5 × HCO₃⁻) + 8 ± 2

        **判讀:**

        | 測量 PaCO₂ | 診斷 |
        |-----------|------|
        | 在預期範圍內 | 適當呼吸代償，純粹代謝性酸中毒 |
        | 低於預期下限 | 合併原發性呼吸性鹼中毒 |
        | 高於預期上限 | 合併原發性呼吸性酸中毒 |

        **何時使用:**
        - 已確認代謝性酸中毒 (pH <7.35, HCO₃⁻ <22 mEq/L)
        - 評估是否有混合型酸鹼障礙

        **限制:**
        - 僅適用於代謝性酸中毒
        - 需時間讓呼吸代償完成 (12-24 小時)
        - 肺部疾病可能影響代償能力

        **參考文獻:**
        - Winter RB, et al. Arch Intern Med. 1967;120(2):209-213. PMID: 5660790
        - Narins RG, Emmett M. Medicine. 1980;59(3):161-187. PMID: 6247109

        Returns:
            預期 PaCO₂ 範圍 (mmHg)、代償評估、混合障礙診斷
        """
        request = CalculateRequest(
            tool_id="winters_formula",
            params={
                "hco3": hco3,
                "actual_paco2": actual_paco2,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_osmolar_gap(
        measured_osm: Annotated[
            float,
            Field(ge=200, le=450, description="測量血清滲透壓 Measured serum osmolality | Unit: mOsm/kg | Range: 200-450")
        ],
        sodium: Annotated[
            float,
            Field(ge=100, le=180, description="血清鈉 Serum sodium | Unit: mEq/L | Range: 100-180")
        ],
        glucose: Annotated[
            float,
            Field(ge=20, le=2000, description="血糖 Blood glucose | Unit: mg/dL | Range: 20-2000")
        ],
        bun: Annotated[
            float,
            Field(ge=1, le=200, description="血尿素氮 Blood urea nitrogen | Unit: mg/dL | Range: 1-200")
        ],
        ethanol: Annotated[
            Optional[float],
            Field(default=None, ge=0, le=600, description="血清乙醇 (optional) Serum ethanol level | Unit: mg/dL | Range: 0-600")
        ] = None,
    ) -> dict[str, Any]:
        """
        🧪 Osmolar Gap: 滲透壓間隙 (毒性醇類篩檢)

        計算測量與計算滲透壓之差，用於檢測未測量的滲透性物質，
        特別是**甲醇**和**乙二醇**中毒。

        **公式:**
        - 計算滲透壓 = 2×Na + (Glucose/18) + (BUN/2.8) + (Ethanol/4.6)
        - 滲透壓間隙 = 測量滲透壓 - 計算滲透壓

        **正常範圍:** -10 to +10 mOsm/kg

        **判讀:**

        | Osmolar Gap | 意義 |
        |-------------|------|
        | -10 to +10 | 正常 |
        | >10 | 升高，可能有未測量滲透物質 |
        | >20-25 | 顯著升高，高度懷疑毒性醇類 |

        **升高原因:**
        - **毒性醇類:** 甲醇、乙二醇、異丙醇、丙二醇
        - 乙醇 (如未納入計算)
        - 酮症 (DKA)
        - 慢性腎病
        - 休克/低灌注
        - 甘露醇

        **⚠️ 重要警告:**
        - 滲透壓間隙正常**不能排除**毒性醇類中毒
        - 隨著代謝，母體醇類減少，間隙可能正常化
        - 同時有高陰離子間隙酸中毒更具診斷價值

        **參考文獻:**
        - Hoffman RS, et al. J Toxicol Clin Toxicol. 1993;31(1):81-93. PMID: 8433417
        - Lynd LD, et al. Clin Toxicol. 2008;46(4):309-323. PMID: 17852166

        Returns:
            Osmolar Gap (mOsm/kg)、解釋、毒性醇類建議
        """
        request = CalculateRequest(
            tool_id="osmolar_gap",
            params={
                "measured_osm": measured_osm,
                "sodium": sodium,
                "glucose": glucose,
                "bun": bun,
                "ethanol": ethanol,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_free_water_deficit(
        current_sodium: Annotated[
            float,
            Field(ge=145, le=200, description="目前血鈉 Current serum sodium | Unit: mEq/L | Range: 145-200 (hypernatremia)")
        ],
        weight_kg: Annotated[
            float,
            Field(ge=2, le=300, description="體重 Body weight | Unit: kg | Range: 2-300")
        ],
        target_sodium: Annotated[
            float,
            Field(default=140.0, ge=135, le=145, description="目標血鈉 Target sodium | Unit: mEq/L | Default: 140")
        ] = 140.0,
        patient_type: Annotated[
            Literal["adult_male", "adult_female", "elderly_male", "elderly_female", "child"],
            Field(default="adult_male", description="病患類型 Patient type for TBW calculation: adult_male (60%), adult_female (50%), elderly_male (50%), elderly_female (45%), child (60%)")
        ] = "adult_male",
        correction_time_hours: Annotated[
            int,
            Field(default=24, ge=1, le=72, description="校正時間 Time for correction | Unit: hours | Range: 1-72 | Recommended: 24-48h")
        ] = 24,
    ) -> dict[str, Any]:
        """
        💧 Free Water Deficit: 高血鈉自由水補充計算

        計算高血鈉患者需要補充的自由水量。

        **公式:**
        - 自由水缺失 = TBW × ((目前 Na / 目標 Na) - 1)
        - TBW = 體重 × 水分比例

        **水分比例:**
        | 類型 | 比例 |
        |------|------|
        | 成年男性 | 60% |
        | 成年女性 | 50% |
        | 老年男性 | 50% |
        | 老年女性 | 45% |
        | 兒童 | 60% |

        **⚠️ 安全校正速率:**
        - **最大: 10-12 mEq/L per 24 hours**
        - 建議: 0.5 mEq/L per hour
        - 校正過快可能導致腦水腫

        **輸液選擇:**
        - D5W: 100% 自由水
        - 0.45% NaCl: ~50% 自由水
        - 0.225% NaCl: ~75% 自由水

        **治療提醒:**
        - 需加上維持液和持續流失量
        - 每 4-6 小時複查血鈉
        - 找出並治療高血鈉原因

        **參考文獻:**
        - Adrogue HJ, Madias NE. N Engl J Med. 2000;342(20):1493-1499. PMID: 10816188
        - Sterns RH. N Engl J Med. 2015;372(1):55-65. PMID: 25551526

        Returns:
            自由水缺失 (L)、輸注速率、安全警示
        """
        request = CalculateRequest(
            tool_id="free_water_deficit",
            params={
                "current_sodium": current_sodium,
                "weight_kg": weight_kg,
                "target_sodium": target_sodium,
                "patient_type": patient_type,
                "correction_time_hours": correction_time_hours,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
