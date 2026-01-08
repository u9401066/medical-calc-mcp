"""
General Calculator Tools

MCP tool handlers for general clinical calculators.
Uses Annotated + Field for rich parameter descriptions in JSON Schema.

Calculators:
- BSA (Body Surface Area) - Chemotherapy/burn dosing
- Cockcroft-Gault - Creatinine clearance for drug dosing
- Corrected Calcium - Albumin-adjusted calcium
- Parkland Formula - Burn fluid resuscitation
"""

from typing import Annotated, Any, Literal, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_general_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all general calculator tools with MCP"""

    @mcp.tool()
    def calculate_bsa(
        weight_kg: Annotated[float, Field(gt=0, le=500, description="體重 Weight | Unit: kg | Range: 1-500")],
        height_cm: Annotated[float, Field(gt=0, le=250, description="身高 Height | Unit: cm | Range: 50-250")],
        formula: Annotated[
            Literal["mosteller", "dubois", "haycock", "boyd"], Field(description="計算公式 Formula | Options: mosteller (default), dubois, haycock, boyd")
        ] = "mosteller",
    ) -> dict[str, Any]:
        """
        📐 Body Surface Area (BSA): 體表面積計算

        計算體表面積，用於化療藥物劑量、燒傷面積估算、及腎功能校正。

        **公式選項:**
        - **Mosteller** (1987): BSA = √(W × H / 3600) ➜ 最常用、簡便
        - **Du Bois** (1916): BSA = 0.007184 × W^0.425 × H^0.725 ➜ 經典
        - **Haycock** (1978): BSA = 0.024265 × W^0.5378 × H^0.3964 ➜ 兒童
        - **Boyd** (1935): 複雜公式，對肥胖較準確

        **正常值:** 1.7-2.0 m² (成人)

        **臨床應用:**
        - 化療劑量: mg/m² 計算
        - 燒傷: TBSA% 估算
        - 腎功能: GFR 校正至 1.73 m²
        - 心臟: Cardiac index = CO / BSA

        **參考文獻:**
        - Du Bois D, Du Bois EF. Arch Intern Med. 1916.
        - Mosteller RD. N Engl J Med. 1987;317(17):1098.

        Returns:
            BSA (m²)、化療劑量調整建議
        """
        request = CalculateRequest(
            tool_id="body_surface_area",
            params={
                "weight_kg": weight_kg,
                "height_cm": height_cm,
                "formula": formula,
            },
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_cockcroft_gault(
        age: Annotated[int, Field(ge=18, le=120, description="年齡 Age | Unit: years | Range: 18-120")],
        weight_kg: Annotated[float, Field(gt=0, le=300, description="體重 Weight | Unit: kg | Range: 30-300 (actual body weight)")],
        creatinine_mg_dl: Annotated[float, Field(gt=0, le=20, description="血清肌酸酐 Serum creatinine | Unit: mg/dL | Range: 0.2-20")],
        sex: Annotated[Literal["male", "female"], Field(description="性別 Sex | Options: male, female")],
        height_cm: Annotated[Optional[float], Field(default=None, gt=0, le=250, description="身高 Height (cm) | For IBW calculation in obesity")] = None,
    ) -> dict[str, Any]:
        """
        💊 Cockcroft-Gault: 肌酸酐清除率 (CrCl)

        估算肌酸酐清除率，用於腎功能藥物劑量調整。
        FDA 核准之藥物劑量調整多參考 Cockcroft-Gault。

        **公式:**
        CrCl = [(140 - age) × weight / (72 × Cr)] × 0.85 (女性)

        **體重選擇:**
        - 正常體重: 使用實際體重
        - 肥胖 (>120% IBW): 自動使用 IBW 或調整體重 (ABW)
        - 惡病質: 使用實際體重

        **藥物劑量調整等級:**
        - >80 mL/min: 正常劑量
        - 50-80 mL/min: 輕度減量
        - 30-50 mL/min: 中度減量
        - 10-30 mL/min: 重度減量/延長間隔
        - <10 mL/min: 考慮替代藥物/透析

        **注意:**
        - 不適用於急性腎損傷
        - 肌肉量極低者會高估
        - 建議搭配 CKD-EPI eGFR 判讀

        **參考文獻:**
        Cockcroft DW, Gault MH. Nephron. 1976;16(1):31-41. PMID: 1244564

        Returns:
            CrCl (mL/min)、藥物劑量調整建議
        """
        request = CalculateRequest(
            tool_id="cockcroft_gault",
            params={
                "age": age,
                "weight_kg": weight_kg,
                "creatinine_mg_dl": creatinine_mg_dl,
                "sex": sex,
                "height_cm": height_cm,
            },
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_corrected_calcium(
        calcium_mg_dl: Annotated[float, Field(gt=0, le=16, description="血清總鈣 Total serum calcium | Unit: mg/dL | Range: 4-16")],
        albumin_g_dl: Annotated[float, Field(gt=0, le=6, description="血清白蛋白 Serum albumin | Unit: g/dL | Range: 1.0-6.0")],
        normal_albumin: Annotated[
            float, Field(default=4.0, gt=0, le=6, description="正常白蛋白參考值 Normal albumin reference | Unit: g/dL | Default: 4.0")
        ] = 4.0,
    ) -> dict[str, Any]:
        """
        🦴 Corrected Calcium: 白蛋白校正鈣

        根據血清白蛋白校正血清鈣，評估真實鈣離子狀態。
        低白蛋白血症常見於 ICU、肝病、營養不良病患。

        **校正公式 (Payne):**
        Corrected Ca = Total Ca + 0.8 × (4.0 - Albumin)

        **正常校正鈣:** 8.5-10.5 mg/dL

        **低血鈣症狀:** QT 延長、抽搐、麻木、肌肉抽筋
        **高血鈣症狀:** 多尿、便秘、嗜睡、意識改變

        **臨床應用:**
        - ICU 病患評估
        - 腎病患者電解質管理
        - 副甲狀腺疾病診斷
        - 惡性腫瘤併發症評估

        **金標準:** 離子鈣 (iCa) 最準確，但需動脈血

        **參考文獻:**
        Payne RB, et al. Br Med J. 1973;4(5893):643-646. PMID: 4758544

        Returns:
            校正鈣濃度、鈣異常分類、處置建議
        """
        request = CalculateRequest(
            tool_id="corrected_calcium",
            params={
                "calcium_mg_dl": calcium_mg_dl,
                "albumin_g_dl": albumin_g_dl,
                "normal_albumin": normal_albumin,
            },
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_parkland_formula(
        weight_kg: Annotated[float, Field(gt=0, le=300, description="體重 Weight | Unit: kg | Range: 5-300")],
        tbsa_percent: Annotated[float, Field(gt=0, le=100, description="燒傷面積 TBSA% | Unit: % | Range: 1-100 (use Rule of 9s or Lund-Browder)")],
        hours_since_burn: Annotated[float, Field(ge=0, le=24, description="燒傷後經過時間 Hours since burn | Unit: hours | Range: 0-24")] = 0,
        is_pediatric: Annotated[bool, Field(description="兒童病患 Pediatric patient (adjusts urine output targets)")] = False,
    ) -> dict[str, Any]:
        """
        🔥 Parkland Formula: 燒傷液體復甦

        計算大面積燒傷患者 24 小時內晶體液需求量。
        適用於 TBSA ≥20% (成人) 或 ≥10% (兒童) 的燒傷。

        **Parkland 公式:**
        24h 總輸液量 = 4 mL × 體重(kg) × TBSA%

        **輸液速度:**
        - **前 8 小時**: 給予總量的 50% (從燒傷時間起算！)
        - **後 16 小時**: 給予剩餘 50%

        **首選晶體液:** Lactated Ringer's (LR)

        **輸液目標:**
        - 成人尿量: 0.5-1.0 mL/kg/h
        - 兒童尿量: 1.0-1.5 mL/kg/h
        - 根據尿量調整速率 (±20%)

        **注意事項:**
        - 公式僅供起始參考，必須根據反應調整
        - 電燒傷、吸入性傷害可能需要更多液體
        - 過度輸液 (fluid creep) 會導致腹腔間室症候群

        **參考文獻:**
        Baxter CR, Shires T. Surg Clin North Am. 1968;48(6):1299-1312. PMID: 5675174

        Returns:
            24小時總輸液量、各時段輸液速度、尿量目標
        """
        request = CalculateRequest(
            tool_id="parkland_formula",
            params={
                "weight_kg": weight_kg,
                "tbsa_percent": tbsa_percent,
                "hours_since_burn": hours_since_burn,
                "is_pediatric": is_pediatric,
            },
        )
        response = use_case.execute(request)
        return response.to_dict()
