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

    @mcp.tool()
    def calculate_abcd2(
        age_gte_60: Annotated[
            bool,
            Field(description="A - 年齡 ≥60歲 Age ≥60 years")
        ],
        bp_gte_140_90: Annotated[
            bool,
            Field(description="B - 血壓 ≥140/90 mmHg Blood pressure ≥140/90 at initial evaluation")
        ],
        clinical_features: Annotated[
            Literal["none", "speech_only", "unilateral_weakness"],
            Field(description="C - 臨床表現 Clinical features | Options: none=無明顯症狀, speech_only=僅語言障礙Speech disturbance only, unilateral_weakness=單側肢體無力Unilateral weakness (±speech)")
        ],
        duration_minutes: Annotated[
            Literal["lt_10", "10_to_59", "gte_60"],
            Field(description="D1 - 症狀持續時間 Duration of symptoms | Options: lt_10=<10分鐘, 10_to_59=10-59分鐘, gte_60=≥60分鐘")
        ],
        diabetes: Annotated[
            bool,
            Field(description="D2 - 糖尿病史 History of diabetes mellitus")
        ]
    ) -> dict[str, Any]:
        """
        🧠 ABCD2 Score: TIA 後短期中風風險評估
        
        預測短暫性腦缺血發作 (TIA) 後 2 天、7 天及 90 天的中風風險，
        協助決定住院與否及檢查急迫性。
        
        **ABCD2 評分項目 (總分 0-7 分):**
        
        - **A**ge (年齡): ≥60歲 = 1分
        - **B**lood pressure (血壓): ≥140/90 mmHg = 1分
        - **C**linical features (臨床表現):
          - 單側無力 = 2分
          - 僅語言障礙 = 1分
        - **D**uration (持續時間):
          - ≥60分鐘 = 2分
          - 10-59分鐘 = 1分
        - **D**iabetes (糖尿病): 有 = 1分
        
        **風險分層與 2 天中風率:**
        - 0-3 分: 低風險 (1.0%) → 可考慮門診追蹤
        - 4-5 分: 中風險 (4.1%) → 建議住院或觀察
        - 6-7 分: 高風險 (8.1%) → 強烈建議住院
        
        **7 天中風率:**
        - 0-3 分: 1.2%
        - 4-5 分: 5.9%
        - 6-7 分: 11.7%
        
        **臨床建議:**
        - 高分患者考慮雙抗血小板治療 (DAPT: aspirin + clopidogrel 21天)
        - 需完整 TIA 檢查：腦影像、血管影像、心律監測
        
        **參考文獻:** Johnston SC, et al. Lancet. 2007;369(9558):283-292.
        PMID: 17258668
        
        Returns:
            ABCD2 分數 (0-7)、2天/7天/90天中風風險、處置建議
        """
        request = CalculateRequest(
            tool_id="abcd2",
            params={
                "age_gte_60": age_gte_60,
                "bp_gte_140_90": bp_gte_140_90,
                "clinical_features": clinical_features,
                "duration_minutes": duration_minutes,
                "diabetes": diabetes
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_modified_rankin_scale(
        mrs_score: Annotated[
            Literal[0, 1, 2, 3, 4, 5, 6],
            Field(description="mRS 分數 Modified Rankin Scale grade | Options: 0=無症狀No symptoms, 1=無明顯失能No significant disability, 2=輕度失能Slight disability, 3=中度失能Moderate disability, 4=中重度失能Moderately severe disability, 5=重度失能Severe disability, 6=死亡Dead")
        ]
    ) -> dict[str, Any]:
        """
        🧠 Modified Rankin Scale (mRS): 中風後失能評估量表
        
        評估中風或其他神經疾病後的失能程度與日常生活獨立性，
        是中風研究與臨床評估最常用的功能預後量表。
        
        **mRS 分級 (0-6 分):**
        
        - **0**: 完全無症狀
        - **1**: 有症狀但無明顯失能，能執行所有日常活動
        - **2**: 輕度失能，無法完成所有先前活動，但能獨立處理個人事務
        - **3**: 中度失能，需要他人協助，但能獨立行走
        - **4**: 中重度失能，無法獨立行走，無法獨立處理個人需求
        - **5**: 重度失能，臥床、失禁、需要持續護理照護
        - **6**: 死亡
        
        **預後分類:**
        - mRS 0-2: **良好預後** (Favorable outcome) - 功能獨立
        - mRS 3: 中等預後 - 能行走但需協助
        - mRS 4-5: 不良預後 - 依賴他人照護
        - mRS 6: 死亡
        
        **臨床應用:**
        - 中風臨床試驗的主要療效指標
        - 評估治療效果 (如血栓溶解術後)
        - 長期預後追蹤
        
        **參考文獻:** van Swieten JC, et al. Stroke. 1988;19(5):604-607.
        PMID: 3363593
        
        Returns:
            mRS 分級、功能狀態分類、是否達良好預後
        """
        request = CalculateRequest(
            tool_id="modified_rankin_scale",
            params={
                "mrs_score": mrs_score
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

