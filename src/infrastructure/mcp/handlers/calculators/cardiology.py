"""
Cardiology Calculator Handlers

MCP tool handlers for cardiology calculators.
"""

from typing import Annotated, Any, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_cardiology_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all cardiology calculator tools with MCP"""

    @mcp.tool()
    def calculate_chads2_vasc(
        chf_or_lvef_lte_40: Annotated[bool, Field(
            description="心衰竭或 LVEF ≤40% CHF or LVEF ≤40%"
        )],
        hypertension: Annotated[bool, Field(
            description="高血壓病史 History of hypertension"
        )],
        age_gte_75: Annotated[bool, Field(
            description="年齡 ≥75 歲 Age ≥75 years (+2 points)"
        )],
        diabetes: Annotated[bool, Field(
            description="糖尿病 Diabetes mellitus"
        )],
        stroke_tia_or_te_history: Annotated[bool, Field(
            description="中風/TIA/血栓栓塞病史 Prior stroke, TIA, or thromboembolism (+2 points)"
        )],
        vascular_disease: Annotated[bool, Field(
            description="血管疾病 Prior MI, PAD, or aortic plaque"
        )],
        age_65_to_74: Annotated[bool, Field(
            description="年齡 65-74 歲 Age 65-74 years (if not ≥75)"
        )],
        female_sex: Annotated[bool, Field(
            description="女性 Female sex"
        )],
    ) -> dict[str, Any]:
        """
        🫀 CHA₂DS₂-VASc: 心房顫動中風風險評估

        評估非瓣膜性心房顫動患者的年中風風險，指導抗凝治療決策。

        **計分項目:**
        - **C**HF/LVEF ≤40%: +1
        - **H**ypertension: +1
        - **A₂**ge ≥75: +2
        - **D**iabetes: +1
        - **S₂**troke/TIA/TE: +2
        - **V**ascular disease: +1
        - **A**ge 65-74: +1
        - **S**ex category (female): +1

        **抗凝建議 (ESC 2020):**
        - 0分 (男) / 1分 (女): 不需抗凝
        - 1分 (男): 考慮抗凝
        - ≥2分: 建議抗凝 (DOAC 優先於 Warfarin)

        **參考文獻:** Lip GY, et al. Chest. 2010;137(2):263-272.
        PMID: 19762550

        Returns:
            CHA₂DS₂-VASc 分數 (0-9)、年中風風險、抗凝建議
        """
        request = CalculateRequest(
            tool_id="chads2_vasc",
            params={
                "chf_or_lvef_lte_40": chf_or_lvef_lte_40,
                "hypertension": hypertension,
                "age_gte_75": age_gte_75,
                "diabetes": diabetes,
                "stroke_tia_or_te_history": stroke_tia_or_te_history,
                "vascular_disease": vascular_disease,
                "age_65_to_74": age_65_to_74,
                "female_sex": female_sex,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_chads2_va(
        chf_or_lvef_lte_40: Annotated[bool, Field(
            description="心衰竭或 LVEF ≤40% CHF or LVEF ≤40%"
        )],
        hypertension: Annotated[bool, Field(
            description="高血壓病史 History of hypertension"
        )],
        age_gte_75: Annotated[bool, Field(
            description="年齡 ≥75 歲 Age ≥75 years (+2 points)"
        )],
        diabetes: Annotated[bool, Field(
            description="糖尿病 Diabetes mellitus"
        )],
        stroke_tia_or_te_history: Annotated[bool, Field(
            description="中風/TIA/血栓栓塞病史 Prior stroke, TIA, or thromboembolism (+2 points)"
        )],
        vascular_disease: Annotated[bool, Field(
            description="血管疾病 Prior MI, PAD, or aortic plaque"
        )],
        age_65_to_74: Annotated[bool, Field(
            description="年齡 65-74 歲 Age 65-74 years (if not ≥75)"
        )],
    ) -> dict[str, Any]:
        """
        🫀 CHA₂DS₂-VA: 心房顫動中風風險評估 (2024 ESC 新版)

        **2024 ESC 指引更新: 移除性別因素**

        評估非瓣膜性心房顫動患者的年中風風險，使用 2024 ESC 性別中性標準。

        **與舊版 CHA₂DS₂-VASc 差異:**
        - 移除 "Sc" (Sex category - female) 作為風險修飾因子
        - 最高分從 9 分降為 8 分
        - 性別中性的抗凝閾值

        **計分項目:**
        - **C**HF/LVEF ≤40%: +1
        - **H**ypertension: +1
        - **A₂**ge ≥75: +2
        - **D**iabetes: +1
        - **S₂**troke/TIA/TE: +2
        - **V**ascular disease: +1
        - **A**ge 65-74: +1

        **抗凝建議 (2024 ESC):**
        - 0分: 不需抗凝
        - 1分: 應考慮抗凝
        - ≥2分: 建議抗凝 (DOAC 優先)

        **參考文獻:** Van Gelder IC, et al. Eur Heart J. 2024;45(36):3314-3414.
        PMID: 39217497

        Returns:
            CHA₂DS₂-VA 分數 (0-8)、年中風風險、抗凝建議
        """
        request = CalculateRequest(
            tool_id="chads2_va",
            params={
                "chf_or_lvef_lte_40": chf_or_lvef_lte_40,
                "hypertension": hypertension,
                "age_gte_75": age_gte_75,
                "diabetes": diabetes,
                "stroke_tia_or_te_history": stroke_tia_or_te_history,
                "vascular_disease": vascular_disease,
                "age_65_to_74": age_65_to_74,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_heart_score(
        history_score: Annotated[
            Literal[0, 1, 2],
            Field(description="病史可疑程度 History | Options: 0=Slightly suspicious, 1=Moderately suspicious, 2=Highly suspicious")
        ],
        ecg_score: Annotated[
            Literal[0, 1, 2],
            Field(description="心電圖 ECG | Options: 0=Normal, 1=Non-specific repolarization changes, 2=Significant ST deviation")
        ],
        age_score: Annotated[
            Literal[0, 1, 2],
            Field(description="年齡 Age | Options: 0=<45 years, 1=45-64 years, 2=≥65 years")
        ],
        risk_factors_score: Annotated[
            Literal[0, 1, 2],
            Field(description="危險因子 Risk factors | Options: 0=None known, 1=1-2 factors, 2=≥3 factors or known atherosclerosis")
        ],
        troponin_score: Annotated[
            Literal[0, 1, 2],
            Field(description="肌鈣蛋白 Troponin | Options: 0=≤Normal limit, 1=1-3× ULN, 2=>3× ULN")
        ],
    ) -> dict[str, Any]:
        """
        🫀 HEART Score: 急診胸痛 MACE 風險分層

        評估急診胸痛患者發生主要心臟不良事件 (MACE) 的風險，
        協助決定出院或住院。

        **HEART 組成要素 (每項 0-2 分):**
        - **H**istory: 病史可疑程度
        - **E**CG: 心電圖變化
        - **A**ge: 年齡
        - **R**isk factors: 危險因子
        - **T**roponin: 肌鈣蛋白

        **風險分層 (6週 MACE):**
        - 0-3 分: 低風險 (0.9-1.7%) → 考慮早期出院
        - 4-6 分: 中度風險 (12-16.6%) → 住院觀察
        - 7-10 分: 高風險 (50-65%) → 住院介入

        **危險因子包括:** HTN, DM, hyperlipidemia,
        current smoking, family history of CAD, obesity (BMI>30)

        **參考文獻:** Six AJ, et al. Neth Heart J. 2008;16(6):191-196.
        PMID: 18665203

        Returns:
            HEART Score (0-10)、6 週 MACE 風險、處置建議
        """
        request = CalculateRequest(
            tool_id="heart_score",
            params={
                "history_score": history_score,
                "ecg_score": ecg_score,
                "age_score": age_score,
                "risk_factors_score": risk_factors_score,
                "troponin_score": troponin_score,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_has_bled(
        hypertension_uncontrolled: Annotated[bool, Field(
            description="未控制高血壓 Uncontrolled hypertension (SBP >160 mmHg)"
        )],
        renal_disease: Annotated[bool, Field(
            description="腎功能異常 Chronic dialysis, transplant, or Cr >2.26 mg/dL"
        )],
        liver_disease: Annotated[bool, Field(
            description="肝功能異常 Chronic hepatic disease (cirrhosis) or biochemical evidence"
        )],
        stroke_history: Annotated[bool, Field(
            description="中風病史 Previous stroke (ischemic or hemorrhagic)"
        )],
        bleeding_history: Annotated[bool, Field(
            description="出血病史 Previous major bleeding or predisposition"
        )],
        labile_inr: Annotated[bool, Field(
            description="不穩定INR Unstable/high INRs, TTR <60% (only if on warfarin)"
        )] = False,
        elderly_gt_65: Annotated[bool, Field(
            description="年齡>65歲 Age >65 years"
        )] = False,
        drugs_antiplatelet_nsaid: Annotated[bool, Field(
            description="併用藥物 Concomitant antiplatelet agents or NSAIDs"
        )] = False,
        alcohol_excess: Annotated[bool, Field(
            description="過量飲酒 Alcohol excess (≥8 drinks/week)"
        )] = False,
    ) -> dict[str, Any]:
        """
        🩸 HAS-BLED: 心房顫動出血風險評估 (2024 ESC 推薦)

        評估心房顫動患者使用抗凝劑時的主要出血風險。
        2024 ESC 指引建議與 CHA₂DS₂-VA 合併使用以平衡中風/出血風險。

        **計分項目 (各 1 分):**
        - **H**ypertension: 未控制高血壓 (SBP >160)
        - **A**bnormal renal/liver function: 腎/肝功能異常 (各 1 分，最多 2 分)
        - **S**troke: 中風病史
        - **B**leeding: 出血史或傾向
        - **L**abile INR: 不穩定 INR (TTR <60%，僅限 warfarin)
        - **E**lderly: 年齡 >65 歲
        - **D**rugs/alcohol: 抗血小板/NSAID 或酒精過量 (各 1 分，最多 2 分)

        **風險分層:**
        - 0-2 分: 低出血風險
        - ≥3 分: 高出血風險 - 需處理可修正因子

        **重要:** 高 HAS-BLED 分數不是抗凝禁忌症，而是提醒需要
        更密切監測並處理可修正的出血風險因子。

        **參考文獻:** Pisters R, et al. Chest. 2010;138(5):1093-1100. PMID: 20299623
        2024 ESC: Van Gelder IC, et al. Eur Heart J. 2024. PMID: 39217497

        Returns:
            HAS-BLED 分數 (0-9)、年主要出血風險、管理建議
        """
        request = CalculateRequest(
            tool_id="has_bled",
            params={
                "hypertension_uncontrolled": hypertension_uncontrolled,
                "renal_disease": renal_disease,
                "liver_disease": liver_disease,
                "stroke_history": stroke_history,
                "bleeding_history": bleeding_history,
                "labile_inr": labile_inr,
                "elderly_gt_65": elderly_gt_65,
                "drugs_antiplatelet_nsaid": drugs_antiplatelet_nsaid,
                "alcohol_excess": alcohol_excess,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_corrected_qt(
        qt_interval: Annotated[float, Field(
            ge=200, le=800,
            description="測量 QT 間期 Measured QT interval | Unit: ms | Range: 200-800"
        )],
        heart_rate: Annotated[float, Field(
            ge=30, le=250,
            description="心率 Heart rate | Unit: bpm | Range: 30-250"
        )],
        sex: Annotated[
            Literal["male", "female"],
            Field(description="性別 Sex | Options: male, female")
        ] = "male",
        formula: Annotated[
            Literal["bazett", "fridericia", "framingham"],
            Field(description="校正公式 Formula | Options: bazett (most common), fridericia (better for tachycardia), framingham")
        ] = "bazett",
    ) -> dict[str, Any]:
        """
        💓 Corrected QT (QTc): 校正 QT 間期計算

        計算心率校正的 QT 間期，用於藥物安全監測與心律不整風險評估。

        **公式:**
        - **Bazett** (最常用): QTc = QT / √RR
        - **Fridericia** (心搏過速/過緩較準): QTc = QT / ∛RR
        - **Framingham** (線性校正): QTc = QT + 154 × (1 - RR)

        **正常值:**
        - 男性: ≤450 ms
        - 女性: ≤460 ms

        **QTc 延長分級:**
        - 邊緣: 450-470 ms (男), 460-480 ms (女)
        - 延長: >470 ms (男), >480 ms (女)
        - 顯著延長: >500 ms (TdP 高風險)

        **常見 QT 延長藥物:**
        - 抗心律不整: amiodarone, sotalol, dofetilide
        - 抗生素: fluoroquinolones, macrolides, azoles
        - 抗精神病: haloperidol, droperidol, ziprasidone
        - 止吐劑: ondansetron (高劑量)
        - 其他: methadone, TCAs, citalopram

        **參考文獻:** Bazett 1920, ESC Guidelines 2015. PMID: 26320108

        Returns:
            QTc 值 (ms)、風險分級、藥物安全建議
        """
        request = CalculateRequest(
            tool_id="corrected_qt",
            params={
                "qt_interval": qt_interval,
                "heart_rate": heart_rate,
                "sex": sex,
                "formula": formula,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_grace_score(
        age: Annotated[int, Field(
            ge=18, le=120,
            description="年齡 Age | Unit: years | Range: 18-120"
        )],
        heart_rate: Annotated[int, Field(
            ge=30, le=250,
            description="心率 Heart rate | Unit: bpm | Range: 30-250"
        )],
        systolic_bp: Annotated[int, Field(
            ge=50, le=250,
            description="收縮壓 Systolic BP | Unit: mmHg | Range: 50-250"
        )],
        creatinine: Annotated[float, Field(
            ge=0.3, le=20.0,
            description="血清肌酸酐 Serum creatinine | Unit: mg/dL | Range: 0.3-20.0"
        )],
        killip_class: Annotated[
            Literal[1, 2, 3, 4],
            Field(description="Killip 分級 | Options: 1=No CHF, 2=Rales/JVD, 3=Pulmonary edema, 4=Cardiogenic shock")
        ],
        cardiac_arrest: Annotated[bool, Field(
            description="到院前心跳停止 Cardiac arrest at admission"
        )],
        st_deviation: Annotated[bool, Field(
            description="ST 段偏移 ST-segment deviation (depression or elevation)"
        )],
        elevated_troponin: Annotated[bool, Field(
            description="肌鈣蛋白升高 Elevated cardiac troponin/enzymes"
        )],
    ) -> dict[str, Any]:
        """
        🫀 GRACE Score: 急性冠心症風險分層

        評估急性冠心症 (ACS) 病人的住院和 6 個月死亡風險，
        用於指導治療策略和轉院決策。

        **GRACE 模型參數:**
        - 年齡
        - 心率
        - 收縮壓
        - 血清肌酸酐
        - Killip 分級
        - 心跳停止
        - ST 段偏移
        - 心肌酵素升高

        **GRACE Score 風險分類 (6 個月死亡):**
        - **低風險**: <109 分 (<3% 死亡率)
        - **中風險**: 109-140 分 (3-8% 死亡率)
        - **高風險**: >140 分 (>8% 死亡率)

        **臨床應用:**
        - 高風險 → 早期侵入性策略 (24-72h 內心導管)
        - 中風險 → 可考慮早期侵入性或保守策略
        - 低風險 → 可考慮保守策略

        **Killip 分級:**
        - I: 無心衰竭
        - II: 肺囉音/JVD
        - III: 急性肺水腫
        - IV: 心因性休克

        **參考文獻:** Fox KA, et al. BMJ. 2006;333(7578):1091. PMID: 17032691

        Returns:
            GRACE Score、6 個月死亡風險、治療策略建議
        """
        request = CalculateRequest(
            tool_id="grace_score",
            params={
                "age": age,
                "heart_rate": heart_rate,
                "systolic_bp": systolic_bp,
                "creatinine": creatinine,
                "killip_class": killip_class,
                "cardiac_arrest": cardiac_arrest,
                "st_deviation": st_deviation,
                "elevated_troponin": elevated_troponin,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_acef_ii(
        age: Annotated[int, Field(
            ge=18, le=100,
            description="年齡 Age | Unit: years | Range: 18-100"
        )],
        lvef: Annotated[float, Field(
            ge=5, le=80,
            description="左心室射出分率 LVEF | Unit: % | Range: 5-80"
        )],
        creatinine: Annotated[float, Field(
            ge=0.3, le=15,
            description="血清肌酸酐 Creatinine | Unit: mg/dL | Range: 0.3-15"
        )],
        emergency: Annotated[bool, Field(
            description="緊急手術 Emergency surgery (doubles the score)"
        )] = False,
    ) -> dict[str, Any]:
        """
        🫀 ACEF II Score: 心臟手術死亡風險預測

        簡約型心臟手術死亡風險模型，僅用 3 個變數達到與複雜評分相當的預測力。

        **ACEF II 公式:**
        ACEF II = (年齡 / LVEF) + 2 (若 Cr >2.0 mg/dL)
        緊急手術時，分數加倍

        **風險分類:**
        - ACEF II <1.0: 低風險 (~1% 死亡率)
        - ACEF II 1.0-2.0: 中風險 (2-5% 死亡率)
        - ACEF II 2.0-3.0: 高風險 (5-10% 死亡率)
        - ACEF II >3.0: 極高風險 (>10% 死亡率)

        **優點:**
        - 僅需 3 個變數 (vs EuroSCORE II 的 18+)
        - 床邊即可計算
        - 多個世代驗證

        **臨床應用:**
        - 術前風險評估
        - 心臟團隊討論
        - 與 EuroSCORE II, STS Score 互補使用

        **參考文獻:** Ranucci M, et al. Eur Heart J. 2018;39(23):2183-2189. PMID: 28498904

        Returns:
            ACEF II 分數、預估死亡率、手術風險建議
        """
        request = CalculateRequest(
            tool_id="acef_ii",
            params={
                "age": age,
                "lvef": lvef,
                "creatinine": creatinine,
                "emergency": emergency,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()

    @mcp.tool()
    def calculate_timi_stemi(
        age_years: Annotated[int, Field(
            description="年齡 Age in years",
            ge=18, le=120
        )],
        has_dm_htn_or_angina: Annotated[bool, Field(
            description="糖尿病、高血壓或心絞痛史 History of diabetes, hypertension, or angina"
        )],
        systolic_bp_lt_100: Annotated[bool, Field(
            description="收縮壓 <100 mmHg Systolic BP <100 mmHg"
        )],
        heart_rate_gt_100: Annotated[bool, Field(
            description="心率 >100 bpm Heart rate >100 bpm"
        )],
        killip_class: Annotated[int, Field(
            description="Killip 分級 (1-4) | 1=無心衰, 2=肺囉音/S3, 3=肺水腫, 4=心因性休克",
            ge=1, le=4
        )],
        weight_lt_67kg: Annotated[bool, Field(
            description="體重 <67 kg Body weight <67 kg"
        )],
        anterior_ste_or_lbbb: Annotated[bool, Field(
            description="前壁ST上升或左束支傳導阻滯 Anterior ST elevation or LBBB"
        )],
        time_to_treatment_gt_4h: Annotated[bool, Field(
            description="症狀發作至治療 >4 小時 Time from symptom onset to treatment >4 hours"
        )]
    ) -> dict[str, Any]:
        """
        ❤️ TIMI Risk Score for STEMI: ST 上升心肌梗塞死亡風險

        預測 STEMI 病患 30 天死亡率的床邊評分工具，
        由 InTIME-II 試驗資料發展並驗證。

        **TIMI STEMI 計分項目 (總分 0-14 分):**

        - **年齡**: 65-74歲 +2分, ≥75歲 +3分
        - **DM/HTN/心絞痛史**: +1分
        - **收縮壓 <100 mmHg**: +3分
        - **心率 >100 bpm**: +2分
        - **Killip II-IV**: +2分
        - **體重 <67 kg**: +1分
        - **前壁 STE 或 LBBB**: +1分
        - **治療延遲 >4 小時**: +1分

        **30 天死亡率 (依分數):**
        - 0 分: 0.8%
        - 1 分: 1.6%
        - 2 分: 2.2%
        - 3 分: 4.4%
        - 4 分: 7.3%
        - 5 分: 12.4%
        - 6 分: 16.1%
        - 7 分: 23.4%
        - 8 分: 26.8%
        - >8 分: 35.9%

        **風險分層:**
        - 0-2: 低風險 (<3%)
        - 3-4: 中風險 (4-7%)
        - 5-6: 高風險 (12-16%)
        - ≥7: 極高風險 (>23%)

        **臨床意義:**
        - 高分患者考慮 CCU/ICU 收治
        - Killip III-IV 考慮機械循環支持
        - Door-to-balloon <90 分鐘仍為關鍵

        **參考文獻:** Morrow DA, et al. Circulation. 2000;102(17):2031-2037.
        PMID: 11044416

        Returns:
            TIMI STEMI 分數 (0-14)、30 天死亡率、風險分層與處置建議
        """
        request = CalculateRequest(
            tool_id="timi_stemi",
            params={
                "age_years": age_years,
                "has_dm_htn_or_angina": has_dm_htn_or_angina,
                "systolic_bp_lt_100": systolic_bp_lt_100,
                "heart_rate_gt_100": heart_rate_gt_100,
                "killip_class": killip_class,
                "weight_lt_67kg": weight_lt_67kg,
                "anterior_ste_or_lbbb": anterior_ste_or_lbbb,
                "time_to_treatment_gt_4h": time_to_treatment_gt_4h
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
