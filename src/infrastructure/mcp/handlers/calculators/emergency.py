"""
Emergency Medicine Calculator Handlers

MCP tool handlers for emergency medicine calculators.
"""

from typing import Annotated, Any, Literal, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .....application.dto import CalculateRequest
from .....application.use_cases import CalculateUseCase


def register_emergency_tools(mcp: FastMCP, use_case: CalculateUseCase) -> None:
    """Register all emergency medicine calculator tools with MCP"""
    
    @mcp.tool()
    def calculate_wells_dvt(
        active_cancer: Annotated[bool, Field(
            description="活動性癌症 Active cancer (treatment ongoing, within 6 months, or palliative)"
        )],
        paralysis_paresis_or_recent_cast: Annotated[bool, Field(
            description="癱瘓/輕癱/近期石膏 Paralysis, paresis, or recent plaster cast of leg"
        )],
        bedridden_or_major_surgery: Annotated[bool, Field(
            description="臥床>3天或12週內大手術 Recently bedridden >3 days or major surgery within 12 weeks"
        )],
        tenderness_along_deep_veins: Annotated[bool, Field(
            description="深靜脈走向壓痛 Localized tenderness along the deep venous system"
        )],
        entire_leg_swollen: Annotated[bool, Field(
            description="整條腿腫脹 Entire leg swollen"
        )],
        calf_swelling_gt_3cm: Annotated[bool, Field(
            description="小腿周徑差>3cm Calf swelling >3 cm compared to asymptomatic leg"
        )],
        pitting_edema: Annotated[bool, Field(
            description="凹陷性水腫 Pitting edema confined to symptomatic leg"
        )],
        collateral_superficial_veins: Annotated[bool, Field(
            description="側支淺靜脈 Collateral superficial veins (non-varicose)"
        )],
        previous_dvt: Annotated[bool, Field(
            description="曾有 DVT 病史 Previously documented DVT"
        )],
        alternative_diagnosis_likely: Annotated[bool, Field(
            description="其他診斷可能性相當或更高 Alternative diagnosis at least as likely as DVT (-2 points)"
        )],
    ) -> dict[str, Any]:
        """
        🦵 Wells DVT: 深靜脈血栓機率評估
        
        評估疑似深靜脈血栓 (DVT) 患者的檢前機率，指導診斷流程。
        
        **計分項目 (各 +1 分):**
        - 活動性癌症
        - 癱瘓/輕癱/近期石膏
        - 臥床 >3 天或 12 週內大手術
        - 深靜脈走向壓痛
        - 整條腿腫脹
        - 小腿周徑差 >3 cm
        - 凹陷性水腫 (症狀側)
        - 側支淺靜脈 (非靜脈曲張)
        - 曾有 DVT 病史
        - **其他診斷可能性相當或更高: -2 分**
        
        **二級模型 (常用):**
        - ≤1 分: DVT Unlikely (~10%) → D-dimer 篩檢
        - ≥2 分: DVT Likely (~25%) → 直接超音波
        
        **三級模型:**
        - ≤0: 低風險 (~5%)
        - 1-2: 中等風險 (~17%)
        - ≥3: 高風險 (~53%)
        
        **參考文獻:** Wells PS, et al. Lancet. 1997;350:1795-1798.
        PMID: 9428249
        
        Returns:
            Wells DVT 分數、DVT 機率、診斷建議
        """
        request = CalculateRequest(
            tool_id="wells_dvt",
            params={
                "active_cancer": active_cancer,
                "paralysis_paresis_or_recent_cast": paralysis_paresis_or_recent_cast,
                "bedridden_or_major_surgery": bedridden_or_major_surgery,
                "tenderness_along_deep_veins": tenderness_along_deep_veins,
                "entire_leg_swollen": entire_leg_swollen,
                "calf_swelling_gt_3cm": calf_swelling_gt_3cm,
                "pitting_edema": pitting_edema,
                "collateral_superficial_veins": collateral_superficial_veins,
                "previous_dvt": previous_dvt,
                "alternative_diagnosis_likely": alternative_diagnosis_likely,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
    
    @mcp.tool()
    def calculate_wells_pe(
        clinical_signs_dvt: Annotated[bool, Field(
            description="DVT 臨床症狀/徵象 Clinical signs/symptoms of DVT (leg swelling, pain with palpation) (+3)"
        )],
        pe_most_likely_diagnosis: Annotated[bool, Field(
            description="PE 為最可能或同等可能的診斷 PE is #1 diagnosis or equally likely (+3)"
        )],
        heart_rate_gt_100: Annotated[bool, Field(
            description="心率 >100 bpm Heart rate >100 bpm (+1.5)"
        )],
        immobilization_or_surgery: Annotated[bool, Field(
            description="臥床≥3天或4週內手術 Immobilization ≥3 days or surgery in past 4 weeks (+1.5)"
        )],
        previous_dvt_pe: Annotated[bool, Field(
            description="曾有 DVT/PE 病史 Previous DVT or PE (+1.5)"
        )],
        hemoptysis: Annotated[bool, Field(
            description="咳血 Hemoptysis (+1)"
        )],
        malignancy: Annotated[bool, Field(
            description="活動性惡性腫瘤 Active malignancy (treatment ongoing, within 6 months, or palliative) (+1)"
        )],
    ) -> dict[str, Any]:
        """
        🫁 Wells PE: 肺栓塞機率評估
        
        評估疑似肺栓塞 (PE) 患者的檢前機率，指導診斷流程。
        
        **計分項目:**
        - DVT 臨床症狀/徵象: +3
        - PE 為最可能或同等可能的診斷: +3
        - 心率 >100 bpm: +1.5
        - 臥床 ≥3 天或 4 週內手術: +1.5
        - 曾有 DVT/PE 病史: +1.5
        - 咳血: +1
        - 活動性惡性腫瘤: +1
        
        **簡化二級模型 (最常用):**
        - ≤4 分: PE Unlikely (~12%) → D-dimer 篩檢
        - >4 分: PE Likely (~37%) → 直接 CTPA
        
        **三級模型:**
        - <2: 低風險 (~3.6%)
        - 2-6: 中等風險 (~20.5%)
        - >6: 高風險 (~66.7%)
        
        **參考文獻:** Wells PS, et al. Thromb Haemost. 2000;83(3):416-420.
        PMID: 10744147
        
        Returns:
            Wells PE 分數、PE 機率、診斷建議
        """
        request = CalculateRequest(
            tool_id="wells_pe",
            params={
                "clinical_signs_dvt": clinical_signs_dvt,
                "pe_most_likely_diagnosis": pe_most_likely_diagnosis,
                "heart_rate_gt_100": heart_rate_gt_100,
                "immobilization_or_surgery": immobilization_or_surgery,
                "previous_dvt_pe": previous_dvt_pe,
                "hemoptysis": hemoptysis,
                "malignancy": malignancy,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
    
    @mcp.tool()
    def calculate_shock_index(
        heart_rate: Annotated[float, Field(
            ge=20, le=300,
            description="心率 Heart rate | Unit: bpm | Range: 20-300"
        )],
        systolic_bp: Annotated[float, Field(
            ge=30, le=300,
            description="收縮壓 Systolic blood pressure | Unit: mmHg | Range: 30-300"
        )],
        diastolic_bp: Annotated[Optional[float], Field(
            ge=20, le=200,
            description="舒張壓 Diastolic BP (optional, for Modified SI) | Unit: mmHg | Range: 20-200"
        )] = None,
        patient_type: Annotated[
            Literal["adult", "pediatric", "obstetric"],
            Field(description="病患類型 Patient type | Options: adult, pediatric, obstetric")
        ] = "adult",
    ) -> dict[str, Any]:
        """
        🚨 Shock Index (SI): 休克指數 - 快速血流動力學評估
        
        計算心率與收縮壓比值，提供快速的血流動力學評估。
        
        **公式:**
        SI = 心率 (bpm) / 收縮壓 (mmHg)
        
        **正常範圍:** 0.5 - 0.7
        
        **判讀:**
        - < 0.6: 正常，血流動力學穩定
        - 0.6 - 0.9: 正常至邊緣
        - 1.0: 上限 (心率 = 收縮壓)
        - > 1.0: 升高 - 血流動力學不穩定
        - > 1.4: 嚴重升高 - 高死亡風險
        
        **臨床應用:**
        - 創傷分級
        - 早期偵測隱匿性出血
        - 預測大量輸血需求
        - 低血容性休克評估
        - 產後出血評估
        
        **優點:**
        - 床邊快速計算
        - 僅需生命徵象
        - 在血壓下降前偵測代償性休克
        - 預測死亡率優於單獨使用心率或血壓
        
        **Modified Shock Index (MSI):**
        若提供舒張壓，將計算 MSI = HR / MAP
        正常範圍: 0.7 - 1.3
        
        **參考文獻:** Allgöwer 1967, Cannon 2009. PMID: 20009697
        
        Returns:
            Shock Index、風險分級、處置建議、Modified SI (如適用)
        """
        request = CalculateRequest(
            tool_id="shock_index",
            params={
                "heart_rate": heart_rate,
                "systolic_bp": systolic_bp,
                "diastolic_bp": diastolic_bp,
                "patient_type": patient_type,
            }
        )
        response = use_case.execute(request)
        return response.to_dict()
