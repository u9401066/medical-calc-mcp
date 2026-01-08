"""
Obstetrics Calculator MCP Handlers

產科計算器:
- Bishop Score: 子宮頸成熟度/引產評估
- Ballard Score: 新生兒胎齡評估
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_obstetrics_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register obstetrics calculator tools"""

    @mcp.tool()
    def calculate_bishop_score(dilation_cm: int, effacement_percent: int, station: int, consistency: str, position: str) -> dict[str, Any]:
        """
        🤰 Bishop Score: 子宮頸成熟度評估 (Cervical Ripening Assessment)

        評估子宮頸成熟度以預測引產成功率，是決定引產時機的標準工具。

        **Bishop Score 五項評估 (各 0-2 或 0-3 分):**

        | 項目 | 0分 | 1分 | 2分 | 3分 |
        |------|-----|-----|-----|-----|
        | **擴張 (cm)** | 0 | 1-2 | 3-4 | ≥5 |
        | **消退 (%)** | 0-30 | 40-50 | 60-70 | ≥80 |
        | **位置** | 後 | 中 | 前 | - |
        | **硬度** | 硬 | 中 | 軟 | - |
        | **先露位置** | -3 | -2 | -1,0 | +1,+2 |

        **引產成功率預測:**
        - 0-4 分: 不成熟 → 引產成功率低 (~50%)，考慮催熟
        - 5-7 分: 中等成熟 → 可考慮引產
        - ≥8 分: 成熟 → 引產成功率高 (>90%)

        **參考文獻:** Bishop EH. Obstet Gynecol. 1964;24:266-268.
        PMID: 14199536

        Args:
            dilation_cm: 子宮頸擴張 (0-10 cm)
            effacement_percent: 子宮頸消退 (0-100%)
            station: 先露位置 (-3 to +3)
            consistency: 硬度 (firm/medium/soft)
            position: 位置 (posterior/mid/anterior)

        Returns:
            Bishop Score、子宮頸成熟度、引產建議
        """
        params = {"dilation_cm": dilation_cm, "effacement_percent": effacement_percent, "station": station, "consistency": consistency, "position": position}
        return use_case.execute(CalculateRequest(tool_id="bishop_score", params=params)).to_dict()

    @mcp.tool()
    def calculate_ballard_score(
        # Neuromuscular maturity (6 items)
        posture: int,
        square_window: int,
        arm_recoil: int,
        popliteal_angle: int,
        scarf_sign: int,
        heel_to_ear: int,
        # Physical maturity (6 items)
        skin: int,
        lanugo: int,
        plantar_surface: int,
        breast: int,
        eye_ear: int,
        genitals: int,
    ) -> dict[str, Any]:
        """
        👶 New Ballard Score: 新生兒胎齡評估 (Gestational Age Assessment)

        透過神經肌肉成熟度和身體成熟度評估新生兒胎齡，
        適用於出生後 12-96 小時內評估，準確度 ±2 週。

        **神經肌肉成熟度 (Neuromuscular Maturity) - 各 0-5 分:**
        - **姿勢 (Posture)**: 觀察仰臥時四肢屈曲程度
        - **方窗角 (Square Window)**: 腕關節屈曲角度
        - **手臂回彈 (Arm Recoil)**: 伸展後回彈速度
        - **膕窩角 (Popliteal Angle)**: 膝關節伸展角度
        - **圍巾徵 (Scarf Sign)**: 手臂橫過胸前程度
        - **跟耳徵 (Heel to Ear)**: 腳跟拉向耳朵程度

        **身體成熟度 (Physical Maturity) - 各 0-5 分:**
        - **皮膚 (Skin)**: 透明度、紋理、脫皮
        - **胎毛 (Lanugo)**: 分布程度
        - **足底紋 (Plantar Surface)**: 皺摺深度
        - **乳房 (Breast)**: 乳暈和乳芽發育
        - **眼耳 (Eye/Ear)**: 眼瞼融合、耳廓彈性
        - **生殖器 (Genitals)**: 發育程度

        **胎齡換算:**
        - 總分 -10 至 50 分 → 對應 20-44 週胎齡
        - 公式: 胎齡(週) = (總分 × 2 + 120) / 5

        **參考文獻:** Ballard JL, et al. J Pediatr. 1991;119(3):417-423.
        PMID: 1880657

        Args:
            posture: 姿勢 (0-5)
            square_window: 方窗角 (0-5)
            arm_recoil: 手臂回彈 (0-5)
            popliteal_angle: 膕窩角 (0-5)
            scarf_sign: 圍巾徵 (0-5)
            heel_to_ear: 跟耳徵 (0-5)
            skin: 皮膚 (0-5)
            lanugo: 胎毛 (0-5)
            plantar_surface: 足底紋 (0-5)
            breast: 乳房 (0-5)
            eye_ear: 眼耳 (0-5)
            genitals: 生殖器 (0-5)

        Returns:
            Ballard Score、估計胎齡、早產/足月/過熟分類
        """
        params = {
            "posture": posture,
            "square_window": square_window,
            "arm_recoil": arm_recoil,
            "popliteal_angle": popliteal_angle,
            "scarf_sign": scarf_sign,
            "heel_to_ear": heel_to_ear,
            "skin": skin,
            "lanugo": lanugo,
            "plantar_surface": plantar_surface,
            "breast": breast,
            "eye_ear": eye_ear,
            "genitals": genitals,
        }
        return use_case.execute(CalculateRequest(tool_id="ballard_score", params=params)).to_dict()
