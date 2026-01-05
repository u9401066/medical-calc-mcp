"""
Anesthesiology / Preoperative Calculator Tools

MCP tool handlers for anesthesiology and preoperative calculators.
Uses Annotated + Field for rich parameter descriptions in JSON Schema.
"""

from typing import Annotated, Any, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_anesthesiology_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all anesthesiology/preoperative calculator tools with MCP"""

    @mcp.tool()
    def calculate_asa_physical_status(
        asa_class: Annotated[
            Literal[1, 2, 3, 4, 5, 6],
            Field(description="ASA分級 ASA Physical Status | Options: 1=健康Healthy, 2=輕度Mild, 3=嚴重Severe, 4=致命Life-threatening, 5=瀕死Moribund, 6=腦死Brain-dead")
        ],
        is_emergency: Annotated[bool, Field(description="是否緊急手術 Emergency surgery (adds 'E' suffix)")] = False
    ) -> dict[str, Any]:
        """
        ASA 身體狀態分級 (ASA Physical Status Classification)

        Classify patient overall health for perioperative risk.
        I=Healthy, II=Mild, III=Severe, IV=Life-threatening, V=Moribund, VI=Brain-dead.
        """
        request = CalculateRequest(
            tool_id="asa_physical_status",
            params={"asa_class": asa_class, "is_emergency": is_emergency}
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_apfel_ponv(
        female_gender: Annotated[bool, Field(description="女性 Female gender")],
        history_motion_sickness_or_ponv: Annotated[bool, Field(description="暈動病或PONV病史 History of motion sickness or previous PONV")],
        non_smoker: Annotated[bool, Field(description="不吸菸 Non-smoker (does NOT currently smoke)")],
        postoperative_opioids: Annotated[bool, Field(description="術後使用鴉片類藥物 Postoperative opioids planned/anticipated")]
    ) -> dict[str, Any]:
        """
        🤢 Apfel Score: 術後噁心嘔吐風險評估 (PONV Risk Score)

        預測成人全身麻醉後發生術後噁心嘔吐的風險，指導預防性止吐藥使用。

        **四個風險因子 (各+1分):**
        - **F**emale gender: 女性
        - **H**istory: 暈動病或 PONV 病史
        - **N**on-smoking: 不吸菸者
        - **O**pioids: 術後使用鴉片類藥物

        **PONV 風險:**
        - 0 因子: ~10%
        - 1 因子: ~21%
        - 2 因子: ~39% → 考慮預防
        - 3 因子: ~61% → 建議多重預防
        - 4 因子: ~79% → 積極多重預防

        **預防策略:**
        - ≥2 風險因子: 雙重止吐預防 (Ondansetron + Dexamethasone)
        - ≥3 風險因子: 多重預防 + TIVA + 減少鴉片類

        **參考文獻:** Apfel CC, et al. Anesthesiology. 1999;91(3):693-700.
        PMID: 10485781

        Returns:
            Apfel 分數 (0-4)、PONV 風險百分比、預防建議
        """
        request = CalculateRequest(
            tool_id="apfel_ponv",
            params={
                "female_gender": female_gender,
                "history_motion_sickness_or_ponv": history_motion_sickness_or_ponv,
                "non_smoker": non_smoker,
                "postoperative_opioids": postoperative_opioids
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_mallampati(
        mallampati_class: Annotated[
            Literal[1, 2, 3, 4],
            Field(description="Mallampati分級 Mallampati Class | Options: 1=全視野Full visibility, 2=部分懸雍垂Partial uvula, 3=軟顎Soft palate only, 4=硬顎Hard palate only")
        ]
    ) -> dict[str, Any]:
        """
        Mallampati 氣道評估分級 (Modified Mallampati Classification)

        Predict difficult intubation. Higher class = higher difficulty.
        I=Easy, IV=Most difficult.
        """
        request = CalculateRequest(
            tool_id="mallampati_score",
            params={"mallampati_class": mallampati_class}
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_rcri(
        high_risk_surgery: Annotated[bool, Field(description="高風險手術 High-risk surgery (intra-abdominal/thoracic/suprainguinal vascular)")] = False,
        ischemic_heart_disease: Annotated[bool, Field(description="缺血性心臟病 Ischemic heart disease (MI/angina/positive stress test)")] = False,
        heart_failure: Annotated[bool, Field(description="心衰竭 Heart failure (CHF/pulmonary edema/S3/rales)")] = False,
        cerebrovascular_disease: Annotated[bool, Field(description="腦血管疾病 Cerebrovascular disease (TIA or stroke history)")] = False,
        insulin_diabetes: Annotated[bool, Field(description="胰島素糖尿病 Insulin-dependent diabetes mellitus")] = False,
        creatinine_above_2: Annotated[bool, Field(description="肌酐>2 Preoperative Cr >2.0 mg/dL")] = False
    ) -> dict[str, Any]:
        """
        計算 RCRI 心臟風險指數 (Revised Cardiac Risk Index)

        Cardiac risk for non-cardiac surgery. Score 0-6.
        0=0.4%, 1=0.9%, 2=6.6%, ≥3=11% major cardiac event.

        Reference: Lee TH, Circulation 1999.
        """
        request = CalculateRequest(
            tool_id="rcri",
            params={
                "high_risk_surgery": high_risk_surgery,
                "ischemic_heart_disease": ischemic_heart_disease,
                "heart_failure": heart_failure,
                "cerebrovascular_disease": cerebrovascular_disease,
                "insulin_diabetes": insulin_diabetes,
                "creatinine_above_2": creatinine_above_2
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_stop_bang(
        snoring: Annotated[bool, Field(description="打鼾 Snoring loudly (loud enough to be heard through closed doors)")],
        tired: Annotated[bool, Field(description="疲倦 Tired during daytime (frequently tired, fatigued, or sleepy)")],
        observed_apnea: Annotated[bool, Field(description="觀察到呼吸暫停 Observed stop breathing during sleep")],
        high_blood_pressure: Annotated[bool, Field(description="高血壓 High blood pressure (treated or untreated)")],
        bmi_over_35: Annotated[bool, Field(description="BMI>35 Obesity with BMI >35 kg/m²")],
        age_over_50: Annotated[bool, Field(description="年齡>50 Age >50 years")],
        neck_over_40cm: Annotated[bool, Field(description="頸圍>40cm Neck circumference >40 cm (>16 inches)")],
        male_gender: Annotated[bool, Field(description="男性 Male gender")]
    ) -> dict[str, Any]:
        """
        😴 STOP-BANG: 阻塞性睡眠呼吸中止症篩檢 (OSA Screening Questionnaire)

        術前評估阻塞性睡眠呼吸中止症 (OSA) 的風險，這是麻醉科超常用的篩檢工具。
        OSA 病人周術期風險增加，需特別注意氣道管理和術後監測。

        **STOP-BANG 八項評估 (各+1分):**
        - **S**noring: 大聲打鼾 (隔著門都聽得到)
        - **T**ired: 日間疲倦嗜睡
        - **O**bserved: 睡眠中被觀察到呼吸暫停
        - **P**ressure: 高血壓 (有無治療皆計)
        - **B**MI >35: 肥胖 BMI >35 kg/m²
        - **A**ge >50: 年齡大於50歲
        - **N**eck >40cm: 頸圍大於40公分
        - **G**ender: 男性

        **OSA 風險分層:**
        - 0-2 分: 低風險 OSA (~15%)
        - 3-4 分: 中度風險 OSA (~30%)
        - 5-8 分: 高風險 OSA (~60%)

        **周術期注意事項:**
        - 中高風險: 考慮術前 PSG 確診
        - 高風險: 減少鴉片類、術後延長監測、準備困難氣道

        **參考文獻:** Chung F, et al. Anesthesiology. 2008;108(5):812-821.
        PMID: 18431116

        Returns:
            STOP-BANG 分數 (0-8)、OSA 風險等級、周術期建議
        """
        request = CalculateRequest(
            tool_id="stop_bang",
            params={
                "snoring": snoring,
                "tired": tired,
                "observed_apnea": observed_apnea,
                "high_blood_pressure": high_blood_pressure,
                "bmi_over_35": bmi_over_35,
                "age_over_50": age_over_50,
                "neck_over_40cm": neck_over_40cm,
                "male_gender": male_gender
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_aldrete_score(
        activity: Annotated[
            Literal[0, 1, 2],
            Field(description="活動力 Activity | Options: 0=無法移動四肢Unable to move, 1=可移動兩肢Moves 2 extremities, 2=可移動四肢Moves 4 extremities voluntarily")
        ],
        respiration: Annotated[
            Literal[0, 1, 2],
            Field(description="呼吸 Respiration | Options: 0=呼吸暫停Apneic, 1=呼吸困難/淺弱Dyspnea or shallow breathing, 2=可深呼吸咳嗽Able to breathe deeply and cough")
        ],
        circulation: Annotated[
            Literal[0, 1, 2],
            Field(description="循環 Circulation (BP vs pre-anesthesia) | Options: 0=BP±50%以上BP±50%+, 1=BP±20-50%BP±20-50%, 2=BP±20%以內BP±20% of pre-anesthesia")
        ],
        consciousness: Annotated[
            Literal[0, 1, 2],
            Field(description="意識 Consciousness | Options: 0=無反應Not responding, 1=可喚醒Arousable on calling, 2=完全清醒Fully awake")
        ],
        oxygen_saturation: Annotated[
            Literal[0, 1, 2],
            Field(description="血氧飽和度 O2 Saturation | Options: 0=SpO2<90%即使給氧SpO2<90% on O2, 1=需給氧維持SpO2>90%Needs O2 to maintain SpO2>90%, 2=室內空氣SpO2>92%SpO2>92% on room air")
        ]
    ) -> dict[str, Any]:
        """
        🏥 Aldrete Score: 麻醉後恢復評估 (Post-Anesthesia Recovery Score)

        評估病人從麻醉恢復的程度，決定是否可從恢復室 (PACU) 出院。
        這是判斷病人是否可離開 PACU 的標準評估工具。

        **Aldrete 五項評估 (各 0-2 分):**
        - **Activity 活動力:**
          - 0分=無法移動四肢, 1分=可動兩肢, 2分=可動四肢
        - **Respiration 呼吸:**
          - 0分=呼吸暫停, 1分=呼吸淺弱/困難, 2分=可深呼吸咳嗽
        - **Circulation 循環:** (與術前血壓比較)
          - 0分=±50%以上, 1分=±20-50%, 2分=±20%以內
        - **Consciousness 意識:**
          - 0分=無反應, 1分=可喚醒, 2分=完全清醒
        - **O2 Saturation 血氧:**
          - 0分=給氧仍<90%, 1分=需給氧維持>90%, 2分=室內空氣>92%

        **出院標準:**
        - ≥9 分: 可考慮離開 PACU
        - <9 分: 需繼續在 PACU 監測

        **注意事項:**
        - 分數應每 5-15 分鐘評估一次
        - 需同時考慮手術特定因素和病人共病

        **參考文獻:** Aldrete JA, Kroulik D. Anesth Analg. 1970;49(6):924-934.
        PMID: 5534693

        Returns:
            Aldrete 分數 (0-10)、恢復狀態、PACU 出院建議
        """
        request = CalculateRequest(
            tool_id="aldrete_score",
            params={
                "activity": activity,
                "respiration": respiration,
                "circulation": circulation,
                "consciousness": consciousness,
                "oxygen_saturation": oxygen_saturation
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
