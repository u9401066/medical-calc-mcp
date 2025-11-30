"""
Neurology Calculator Tools

MCP tool handlers for neurology calculators.
Uses Annotated + Field for rich parameter descriptions in JSON Schema.
"""

from typing import Any, Annotated, Literal

from pydantic import Field
from mcp.server.fastmcp import FastMCP

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_neurology_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all neurology calculator tools with MCP"""
    
    @mcp.tool()
    def calculate_nihss(
        loc: Annotated[
            Literal[0, 1, 2, 3],
            Field(description="1a. 意識程度 Level of Consciousness | Options: 0=清醒Alert, 1=嗜睡Drowsy, 2=昏迷Stuporous, 3=深度昏迷Coma")
        ],
        loc_questions: Annotated[
            Literal[0, 1, 2],
            Field(description="1b. 意識問題-月份年齡 LOC Questions (month, age) | Options: 0=兩者皆正確Both correct, 1=一個正確One correct, 2=皆錯誤Neither correct")
        ],
        loc_commands: Annotated[
            Literal[0, 1, 2],
            Field(description="1c. 意識指令-眨眼握拳 LOC Commands (blink, squeeze) | Options: 0=兩者皆行Both obey, 1=一個執行One obeys, 2=皆不行Neither obeys")
        ],
        best_gaze: Annotated[
            Literal[0, 1, 2],
            Field(description="2. 凝視 Best Gaze (horizontal eye movement) | Options: 0=正常Normal, 1=部分凝視麻痺Partial gaze palsy, 2=強制偏視Forced deviation")
        ],
        visual_fields: Annotated[
            Literal[0, 1, 2, 3],
            Field(description="3. 視野 Visual Fields | Options: 0=無缺損No visual loss, 1=部分偏盲Partial hemianopia, 2=完全偏盲Complete hemianopia, 3=雙側偏盲Bilateral hemianopia")
        ],
        facial_palsy: Annotated[
            Literal[0, 1, 2, 3],
            Field(description="4. 顏面麻痺 Facial Palsy | Options: 0=正常對稱Normal symmetric, 1=輕度Minor paralysis, 2=部分麻痺Partial paralysis, 3=完全麻痺Complete paralysis")
        ],
        motor_arm_left: Annotated[
            Literal[0, 1, 2, 3, 4],
            Field(description="5a. 左上肢運動 Motor Arm Left (hold 10 sec) | Options: 0=無下垂No drift, 1=下垂Drift, 2=無法抵抗重力Some effort against gravity, 3=無法舉起No effort against gravity, 4=完全癱瘓No movement")
        ],
        motor_arm_right: Annotated[
            Literal[0, 1, 2, 3, 4],
            Field(description="5b. 右上肢運動 Motor Arm Right (hold 10 sec) | Options: 0=無下垂No drift, 1=下垂Drift, 2=無法抵抗重力Some effort against gravity, 3=無法舉起No effort against gravity, 4=完全癱瘓No movement")
        ],
        motor_leg_left: Annotated[
            Literal[0, 1, 2, 3, 4],
            Field(description="6a. 左下肢運動 Motor Leg Left (hold 5 sec) | Options: 0=無下垂No drift, 1=下垂Drift, 2=無法抵抗重力Some effort against gravity, 3=無法舉起No effort against gravity, 4=完全癱瘓No movement")
        ],
        motor_leg_right: Annotated[
            Literal[0, 1, 2, 3, 4],
            Field(description="6b. 右下肢運動 Motor Leg Right (hold 5 sec) | Options: 0=無下垂No drift, 1=下垂Drift, 2=無法抵抗重力Some effort against gravity, 3=無法舉起No effort against gravity, 4=完全癱瘓No movement")
        ],
        limb_ataxia: Annotated[
            Literal[0, 1, 2],
            Field(description="7. 肢體運動失調 Limb Ataxia (finger-nose, heel-shin) | Options: 0=無失調Absent, 1=單肢失調Present in 1 limb, 2=雙肢失調Present in 2+ limbs")
        ],
        sensory: Annotated[
            Literal[0, 1, 2],
            Field(description="8. 感覺 Sensory (pinprick) | Options: 0=正常Normal, 1=輕中度減退Mild-moderate loss, 2=嚴重或完全喪失Severe or total loss")
        ],
        best_language: Annotated[
            Literal[0, 1, 2, 3],
            Field(description="9. 語言 Best Language (naming, reading, describing) | Options: 0=無失語No aphasia, 1=輕中度失語Mild-moderate aphasia, 2=嚴重失語Severe aphasia, 3=啞默或全失語Mute/global aphasia")
        ],
        dysarthria: Annotated[
            Literal[0, 1, 2],
            Field(description="10. 構音障礙 Dysarthria (speech clarity) | Options: 0=正常Normal, 1=輕中度Mild-moderate, 2=嚴重或無法言語Severe/mute")
        ],
        extinction_inattention: Annotated[
            Literal[0, 1, 2],
            Field(description="11. 忽略/消失現象 Extinction and Inattention | Options: 0=無異常No abnormality, 1=一種感覺忽略Inattention in 1 modality, 2=嚴重忽略Profound inattention in 2+ modalities")
        ]
    ) -> dict[str, Any]:
        """
        🧠 NIHSS: 美國國家衛生研究院中風量表 (NIH Stroke Scale)
        
        標準化評估急性中風嚴重程度的量表，廣泛用於決定血栓溶解治療適應症
        及預測中風預後。神經科中風評估必備工具。
        
        **NIHSS 11項評估 (總分 0-42 分):**
        
        1a. **意識程度** (0-3): 清醒到昏迷
        1b. **意識問題** (0-2): 回答月份和年齡
        1c. **意識指令** (0-2): 眨眼和握拳
        2. **凝視** (0-2): 水平眼球運動
        3. **視野** (0-3): 視野缺損
        4. **顏面麻痺** (0-3): 臉部對稱性
        5. **上肢運動** (0-4 x2): 左右分開評估，維持10秒
        6. **下肢運動** (0-4 x2): 左右分開評估，維持5秒
        7. **肢體運動失調** (0-2): 指鼻和腳跟脛骨測試
        8. **感覺** (0-2): 針刺感覺
        9. **語言** (0-3): 命名、閱讀、描述
        10. **構音障礙** (0-2): 言語清晰度
        11. **忽略/消失** (0-2): 感覺忽略
        
        **嚴重度分級:**
        - 0 分: 無中風症狀
        - 1-4 分: 輕度中風
        - 5-15 分: 中度中風
        - 16-20 分: 中重度中風
        - 21-42 分: 重度中風
        
        **臨床應用:**
        - NIHSS ≥4: 通常考慮 rtPA 血栓溶解治療
        - NIHSS >25: 出血風險增加，需謹慎評估
        
        **參考文獻:** Brott T, et al. Stroke. 1989;20(7):864-870.
        PMID: 2749846
        
        Returns:
            NIHSS 總分 (0-42)、中風嚴重度、各項細分分數
        """
        request = CalculateRequest(
            tool_id="nihss",
            params={
                "loc": loc,
                "loc_questions": loc_questions,
                "loc_commands": loc_commands,
                "best_gaze": best_gaze,
                "visual_fields": visual_fields,
                "facial_palsy": facial_palsy,
                "motor_arm_left": motor_arm_left,
                "motor_arm_right": motor_arm_right,
                "motor_leg_left": motor_leg_left,
                "motor_leg_right": motor_leg_right,
                "limb_ataxia": limb_ataxia,
                "sensory": sensory,
                "best_language": best_language,
                "dysarthria": dysarthria,
                "extinction_inattention": extinction_inattention
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
