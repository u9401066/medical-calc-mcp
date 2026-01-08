"""
Hematology Calculator Handlers

MCP tool handlers for hematology calculators.
"""

from typing import Annotated, Any, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_hematology_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all hematology calculator tools with MCP"""

    @mcp.tool()
    def calculate_4ts_hit(
        thrombocytopenia_score: Annotated[
            Literal[0, 1, 2],
            Field(description="血小板下降 Thrombocytopenia | Options: 0=<30% fall or nadir <10K, 1=30-50% fall or nadir 10-19K, 2=>50% fall and nadir ≥20K"),
        ],
        timing_score: Annotated[
            Literal[0, 1, 2],
            Field(
                description="時序 Timing of platelet fall | Options: 0=<4d without recent heparin, 1=consistent (5-10d or >10d) or unclear, 2=clear onset 5-10d or ≤1d with recent heparin"
            ),
        ],
        thrombosis_score: Annotated[
            Literal[0, 1, 2],
            Field(description="血栓 Thrombosis | Options: 0=None, 1=Progressive/recurrent/suspected, 2=New confirmed thrombosis or skin necrosis"),
        ],
        other_causes_score: Annotated[
            Literal[0, 1, 2],
            Field(
                description="其他原因 Other causes for thrombocytopenia | Options: 0=Definite other cause, 1=Possible other cause, 2=No other cause apparent"
            ),
        ],
    ) -> dict[str, Any]:
        """
        🩸 4Ts Score: 肝素誘發血小板減少症 (HIT) 機率評估

        評估疑似 HIT 病人的臨床機率，指導後續檢查與處置。

        **4Ts 組成 (每項 0-2 分):**

        **T**hrombocytopenia (血小板減少):
        - 2分: 下降 >50% 且最低值 ≥20K
        - 1分: 下降 30-50% 或最低值 10-19K
        - 0分: 下降 <30% 或最低值 <10K

        **T**iming (時序):
        - 2分: 明確於第 5-10 天發生，或 ≤1 天 (近期肝素暴露)
        - 1分: 符合但不明確 (如 >10 天)，或不確定
        - 0分: <4 天且無近期肝素暴露

        **T**hrombosis (血栓):
        - 2分: 新確認血栓、皮膚壞死、急性全身反應
        - 1分: 進展中/復發/疑似血栓
        - 0分: 無

        **o**Ther causes (其他原因):
        - 2分: 無其他明顯原因
        - 1分: 可能有其他原因
        - 0分: 有明確其他原因

        **HIT 機率分層:**
        - 0-3 分: 低機率 (<5%) → 可繼續肝素
        - 4-5 分: 中等機率 (~14%) → 停肝素，送 HIT 檢驗
        - 6-8 分: 高機率 (~64%) → 立即停肝素，換替代抗凝

        **參考文獻:** Lo GK, Warkentin TE, et al. J Thromb Haemost. 2006;4(4):759-765. PMID: 16634744

        Returns:
            4Ts 分數 (0-8)、HIT 機率、處置建議
        """
        request = CalculateRequest(
            tool_id="4ts_hit",
            params={
                "thrombocytopenia": thrombocytopenia_score,
                "timing": timing_score,
                "thrombosis": thrombosis_score,
                "other_causes": other_causes_score,
            },
        )
        response = use_case.execute(request)
        return response.to_dict()
